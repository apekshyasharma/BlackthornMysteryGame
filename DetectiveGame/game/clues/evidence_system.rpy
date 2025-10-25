# evidence_system.rpy
# Evidence data, validation, global list, and Evidence Book screen.

init python:
    import re
    import difflib
    # New imports for NLP backend integration
    try:
        import requests
    except Exception:
        requests = None

# Global store of collected evidence entries (each: {"id": ..., "name": ..., "thumb": ...})
default evidence_list = []
default evidence_collected = set()
define EVIDENCE_REQUIRED_TOTAL = 3
default evidence_guess = ""
default evidence_phase_done = False

# Confidence threshold as per instructions
define EVIDENCE_SIM_THRESHOLD = 0.65
define NLP_BEST_MATCH_URL = "http://127.0.0.1:5000/best_match"

# Canonical catalog of evidence in this scene - with CORRECT THUMB PATHS
define EVIDENCE_CATALOG = {
    "clue_glass": {
        "name": "glass",
        "display": "Broken Glass", 
        "thumb": "images/clues/thumbs/thumb_glass.png",  # Full path to thumbnail
        "idle": "images/clues/clue_glass.png",
        "hover": "images/clues/clue_glass_hover.png"
    },
    "clue_handkerchief": {
        "name": "handkerchief",
        "display": "Handkerchief",
        "thumb": "images/clues/thumbs/thumb_handkerchief.png",  # Full path to thumbnail
        "idle": "images/clues/clue_handkerchief.png",
        "hover": "images/clues/clue_handkerchief_hover.png"
    },
    "clue_letter": {
        "name": "letter",
        "display": "Half-burnt Letter",
        "thumb": "images/clues/thumbs/thumb_letter.png",  # Full path to thumbnail
        "idle": "images/clues/clue_letters.png",    # Note the 's' in "letters"
        "hover": "images/clues/clue_letters_hover.png"  # Note the 's' in "letters"
    },
}

# Define expanded synonyms for evidence items with more natural language variations
define EVIDENCE_SYNONYMS = {
    "glass": {
        "glass", "broken glass", "shattered glass", "piece of glass", "pieces of glass",
        "window glass", "fragments", "glass fragments", "broken window", "glass shards",
        "glass pieces", "shattered window", "window fragments", "broken pieces of glass",
        "window fragment", "sharp glass", "clear shards", "clear glass", "window shard",
        "broken window glass", "window glass piece", "glass from window", "broken pieces",
        "window pieces", "glass splinters", "broken glass pieces", "shards", "drinking glass", "broken drinking glass"
    },
    "handkerchief": {
        "handkerchief", "cloth", "rag", "bloody cloth", "bloody rag", 
        "stained fabric", "napkin", "handkerchiefs", "blood stained cloth",
        "blood-stained handkerchief", "fabric with blood", "stained cloth",
        "tissue", "bloody handkerchief", "stained handkerchief", "red cloth",
        "bloodied fabric", "stained handkerchief", "bloodstained rag", 
        "blood-soaked cloth", "fabric", "bloodied rag", "stained napkin",
        "blood stained fabric", "cloth with blood", "piece of cloth",
        "blood-covered cloth", "red-stained fabric", "small cloth", "bloodstained cloth",
        "cloth covered in blood"
    },
    "letter": {
        "letter", "note", "paper", "burnt paper", "sheet of paper", "piece of paper",
        "charred message", "scorched letter", "document", "message", 
        "written note", "correspondence", "memo", "parchment", "burned letter",
        "crumpled paper", "crumpled note", "torn paper", "folded paper",
        "handwritten note", "handwritten letter", "burned paper", "charred paper",
        "partially burned note", "singed letter", "burnt note", "burnt document",
        "scorched paper", "piece of burnt paper", "paper with writing", "written paper",
        "charred letter", "fire-damaged paper", "message on paper", "paper letter",
        "sheet with writing", "old letter", "torn letter", "folded note", "letter that's been burned", "letter thats been burned"
    }
    # Add more evidence items with synonyms as needed
}

init python:
    import re

    # Filler phrases to strip from player inputs
    FILLER_PATTERNS = [
        r"\bi think\b",
        r"\bmaybe\b",
        r"\bkind of\b",
        r"\blocks like\b",
        r"\blooks like\b",
        r"\bi guess\b",
        r"\bsort of\b",
        r"\bseems like\b",
        r"\bi found\b",
        r"\bi think i found\b",
        r"\bi believe\b",
        r"\bit might be\b",
    ]

    def _norm(s):
        """Normalize text by converting to lowercase and removing punctuation"""
        if not s:
            return ""
        s = s.strip().lower()
        # Replace punctuation with spaces, collapse spaces
        s = re.sub(r"[^a-z0-9]+", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def preprocess_input(s):
        """
        Lowercase, remove filler words, strip punctuation.
        """
        if not s:
            return ""
        text = s.lower().strip()
        for pat in FILLER_PATTERNS:
            text = re.sub(pat, " ", text, flags=re.IGNORECASE)
        text = re.sub(r"[^a-z0-9\s]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def nlp_best_match(text, candidates):
        """
        Call the Flask backend to get the best matching synonym for the given text.
        Returns (best_score: float, best_text: str). Raises on hard failure.
        """
        if not requests:
            raise RuntimeError("requests module not available")
        payload = {
            "text": text or "",
            "candidates": list(candidates) if candidates else []
        }
        try:
            resp = requests.post(NLP_BEST_MATCH_URL, json=payload, timeout=3.0)
            resp.raise_for_status()
            data = resp.json() or {}
            return float(data.get("best_score", 0.0)), data.get("best_text", "")
        except Exception as e:
            raise

    def check_evidence_input(user_input, correct_name):
        """
        Check if the user input matches the expected evidence item
        using a staged approach: NLP similarity → synonyms → fuzzy matching.

        Args:
            user_input: The text entered by the player
            correct_name: Canonical evidence name (e.g., 'handkerchief', 'letter', 'glass')

        Returns:
            tuple: (is_correct, similarity_score, stage_used)
        """
        # Normalize user input with filler removal
        processed_input = preprocess_input(user_input)

        if not processed_input:
            return (False, 0.0, "empty_input")

        # Default to a low similarity if the correct evidence has no synonyms
        if correct_name not in EVIDENCE_SYNONYMS:
            renpy.log(f"Warning: No synonyms found for evidence '{correct_name}'")
            return (False, 0.0, "no_synonyms")

        # Get all synonyms for this evidence
        synonyms = list(EVIDENCE_SYNONYMS[correct_name])

        # STAGE 1: NLP Model Similarity Check against all synonyms (>= 0.65 threshold)
        try:
            best_nlp_score, best_nlp_synonym = nlp_best_match(processed_input, synonyms)
            if best_nlp_score >= EVIDENCE_SIM_THRESHOLD:
                renpy.log(f"Matched: {best_nlp_synonym} ({best_nlp_score:.2f})")
                renpy.log(f"Stage 1 (NLP) match for '{processed_input}' → {correct_name}: {best_nlp_score:.2f} (matched '{best_nlp_synonym}')")
                return (True, best_nlp_score, "nlp_model")

            renpy.log(f"Stage 1 (NLP) failed for '{processed_input}' → {correct_name}: best score {best_nlp_score:.2f} (best '{best_nlp_synonym}')")

        except Exception as e:
            renpy.log(f"Stage 1 (NLP) error: {str(e)}. Moving to Stage 2.")

        # STAGE 2: Expanded Synonyms Dictionary Exact Check
        try:
            normalized_synonyms = [_norm(syn) for syn in synonyms]

            if _norm(processed_input) in normalized_synonyms:
                # Find the original synonym that matched
                for orig_syn in synonyms:
                    if _norm(orig_syn) == _norm(processed_input):
                        renpy.log(f"Matched: {orig_syn} (1.00)")
                        renpy.log(f"Stage 2 (synonyms) exact match for '{processed_input}' → {correct_name} (matched '{orig_syn}')")
                        return (True, 1.0, "synonyms_exact")

            renpy.log(f"Stage 2 (synonyms) failed for '{processed_input}' → {correct_name}")

        except Exception as e:
            renpy.log(f"Stage 2 (synonyms) error: {str(e)}. Moving to Stage 3.")

        # STAGE 3: Fuzzy Matching Fallback (difflib ratio >= 0.8)
        try:
            best_fuzzy_score = 0.0
            best_fuzzy_synonym = ""

            for synonym in synonyms:
                normalized_synonym = _norm(synonym)
                ratio = difflib.SequenceMatcher(None, _norm(processed_input), normalized_synonym).ratio()

                if ratio > best_fuzzy_score:
                    best_fuzzy_score = ratio
                    best_fuzzy_synonym = synonym

            if best_fuzzy_score >= 0.8:
                renpy.log(f"Matched: {best_fuzzy_synonym} ({best_fuzzy_score:.2f})")
                renpy.log(f"Stage 3 (fuzzy) match for '{processed_input}' → {correct_name}: {best_fuzzy_score:.2f} (matched '{best_fuzzy_synonym}')")
                return (True, best_fuzzy_score, "fuzzy_matching")

            renpy.log(f"Stage 3 (fuzzy) failed for '{processed_input}' → {correct_name}: best score {best_fuzzy_score:.2f}")

        except Exception as e:
            renpy.log(f"Stage 3 (fuzzy) error: {str(e)}.")

        # All stages failed
        renpy.log(f"All stages failed for '{processed_input}' → {correct_name}")
        return (False, 0.0, "all_stages_failed")

    # Updated function to process evidence with similarity check
    def process_evidence(evidence_id, guess_text):
        """
        Validate the player's guess using staged approach,
        update evidence, notify, and flag completion when all items are collected.
        """
        global evidence_phase_done
        meta = EVIDENCE_CATALOG.get(evidence_id)
        if not meta:
            renpy.notify("Something went wrong.")
            return

        guess = (guess_text or "").strip()
        correct_name = meta["name"]

        # Use updated staged similarity check
        is_match, sim, stage = check_evidence_input(guess, correct_name)

        if is_match:
            added = add_evidence(evidence_id)
            if added:
                renpy.notify(f"{meta['display']} has been added to the Evidence Book. (Score: {sim:.2f}, Stage: {stage})")
                renpy.log(f"Matched: {meta['name']} ({sim:.2f})")
            else:
                renpy.notify(f"Already collected. (Score: {sim:.2f}, Stage: {stage})")
        else:
            # Threshold fail → "Try again" behavior maintained
            renpy.notify(f"Not quite. Look again. (Best score: {sim:.2f}, Stage: {stage})")

        if len(evidence_collected) >= EVIDENCE_REQUIRED_TOTAL:
            evidence_phase_done = True

# Add missing add_evidence function
    def add_evidence(evidence_id):
        """
        Add evidence to the evidence list and collected set if not already present.

        Args:
            evidence_id: The ID of the evidence item to add

        Returns:
            bool: True if evidence was newly added, False if already present
        """
        if evidence_id in evidence_collected:
            return False

        # Get evidence metadata
        meta = EVIDENCE_CATALOG.get(evidence_id)
        if not meta:
            renpy.log(f"Warning: No metadata found for evidence '{evidence_id}'")
            return False

        # Add to collected set
        evidence_collected.add(evidence_id)

        # Add to evidence list for Evidence Book display
        evidence_entry = {
            "id": evidence_id,
            "name": meta["display"],
            "thumb": meta["thumb"]
        }
        evidence_list.append(evidence_entry)

        renpy.log(f"Added evidence: {evidence_id} ({meta['display']})")
        return True

# Define the required style exactly as specified in instructions.txt
style evidence_input_text:
    color "#FFFFFF"                 # WHITE text
    size 28                         # size 28
    font "DejaVuSans.ttf"           # specified font
    xalign 0.0                      # left-aligned text
    xpadding 12                     # proper padding
    ypadding 10

# Gold border glow for evidence input frame
transform gold_glow:
    alpha 0.95
    linear 0.7 alpha 1.0
    linear 0.7 alpha 0.75
    repeat

# Evidence Input Popup - fixed with proper modal behavior and styling
screen evidence_input_popup(eid):
    modal True
    zorder 200
    
    # Dim background
    add Solid("#00000088")
    
    # Exactly centered as required in instructions
    frame:
        background Solid("#FFD700")     # gold border
        padding (3, 3)
        xalign 0.5                      # centered horizontally
        yalign 0.5                      # centered vertically
        
        frame:
            background Solid("#222222")
            padding (20, 16)
            xsize 700
            yminimum 260

            vbox:
                spacing 18
                text "What do you think this is?" size 32 xalign 0.5 color "#FFD700"

                # Input area with gold border
                frame:
                    background Solid("#FFD700")
                    padding (2, 2)
                    
                    # Dark grey input background as specified in instructions.txt
                    frame:
                        background Solid("#333333")  # exact color from instructions
                        padding (10, 8)
                        xfill True
                        
                        input:
                            # Use EXACTLY the style name from instructions.txt
                            style "evidence_input_text"
                            value VariableInputValue("evidence_guess")
                            length 40
                            copypaste True

                hbox:
                    xalign 0.5
                    spacing 12
                    
                    textbutton "Submit":
                        style "button"
                        text_color "#FFD700"
                        action [Function(process_evidence, eid, evidence_guess),
                                Hide("evidence_input_popup")]
                    
                    textbutton "Cancel":
                        style "button"
                        text_color "#FFD700"
                        action Hide("evidence_input_popup")

# Evidence Book with proper close button - FIXED VERSION
screen evidence_book():
    modal True
    zorder 100
    tag evidence_book

    # Dark overlay
    add Solid("#00000099")

    # Smaller frame size (reduced from 900x650 to 800x550)
    frame:
        style "frame"
        background Frame("gui/frame.png", Borders(10, 10, 10, 10))
        xalign 0.5
        yalign 0.5
        xsize 800  # Reduced from 900
        ysize 550  # Reduced from 650
        padding (35, 35)  # Slightly smaller padding

        vbox:
            spacing 15  # Reduced spacing
            text "Evidence Book" size 38 xalign 0.5 color gui.accent_color bold True  # Slightly smaller text
            
            # Separator
            frame:
                background Solid(gui.accent_color)
                ysize 3
                xfill True
                ymargin 5
            
            # Evidence items or placeholder text
            if evidence_list:
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    xsize 730  # Reduced from 820
                    ysize 380  # Reduced from 450

                    vbox:
                        spacing 15  # Reduced spacing
                        for ev in evidence_list:
                            frame:
                                background Solid("#00000066")
                                xfill True
                                padding (15, 15)  # Reduced padding
                                
                                hbox:
                                    spacing 20  # Reduced spacing
                                    
                                    # Fixed thumbnail display with proper alignment and FULL PATH
                                    fixed:
                                        xsize 140  # Reduced from 150
                                        ysize 140  # Reduced from 150
                                        add Solid("#222222")  # Background for consistency
                                        
                                        # Get evidence ID and use FULL PATH to the thumbnail
                                        $ evidence_id = ev.get("id", "")
                                        if evidence_id == "clue_letter":
                                            # Use full path to the thumbnail image
                                            add "images/clues/thumbs/thumb_letter.png" align (0.5, 0.5)
                                        elif evidence_id == "clue_glass":
                                            add "images/clues/thumbs/thumb_glass.png" align (0.5, 0.5)
                                        elif evidence_id == "clue_handkerchief":
                                            add "images/clues/thumbs/thumb_handkerchief.png" align (0.5, 0.5)
                                        else:
                                            # Fallback
                                            add Solid("#FFD700", xsize=100, ysize=100) align (0.5, 0.5)
                                    
                                    vbox:
                                        spacing 10
                                        xsize 530  # Reduced from 600
                                        text ev["name"] size 30 color "#FFD700" bold True  # Slightly smaller text
                                        text "Found in the study." size 22  # Slightly smaller text
            else:
                text "No evidence collected yet." xalign 0.5 yalign 0.5 size 28 color gui.text_color

            # Close button
            null height 20  # Reduced spacing
            
            hbox:
                xalign 1.0
                textbutton "Close":
                    action Hide("evidence_book")
                    style "button"
                    text_style "button_text"
                    xpadding 25  # Reduced padding
                    ypadding 12  # Reduced padding
                    text_size 26  # Slightly smaller text