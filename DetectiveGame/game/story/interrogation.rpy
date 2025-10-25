# Interrogation phase with NLP-driven question classification

# Import check_similarity from nlp_service.py
init -5 python:
    # Import the similarity functions from the NLP service
    import sys
    import os

    # Add the parent directory to the path so we can import nlp_service
    sys.path.append(renpy.loader.transfn("../"))

    try:
        from nlp_service import check_similarity, best_intent
        renpy.log("Successfully imported interrogation helpers (check_similarity, best_intent)")
    except ImportError:
        # Fallbacks if the import fails
        renpy.log("Failed to import interrogation helpers, using fallbacks")

        def check_similarity(text1, text2):
            """Fallback similarity function using difflib"""
            import difflib
            return difflib.SequenceMatcher(None, (text1 or "").lower(), (text2 or "").lower()).ratio()

        def best_intent(user_text, intents, threshold=0.35):
            """
            Fallback intent matcher using difflib best ratio across canonical+synonyms.
            Mirrors the nlp_service.best_intent output shape.
            """
            import difflib
            q = (user_text or "").strip().lower()
            if not q or not intents:
                return {"best_id": "", "best_text": "", "best_score": 0.0, "matched": False}

            best_id = ""
            best_text = ""
            best_score = 0.0

            for it in intents:
                cid = it.get("id") or it.get("name") or ""
                canon = (it.get("canonical") or "").strip().lower()
                syns = [s.strip().lower() for s in (it.get("synonyms") or []) if s]
                pool = ([canon] if canon else []) + syns
                for cand in pool:
                    score = difflib.SequenceMatcher(None, q, cand).ratio()
                    if score > best_score:
                        best_score = score
                        best_id = cid
                        best_text = cand

            return {
                "best_id": best_id,
                "best_text": best_text,
                "best_score": best_score,
                "matched": best_score >= threshold
            }
# Entry point from butler_explains
label interrogation_start:
    # Fade out from the Butler's explanation scene
    scene black
    with fade
    
    # Show interrogation message
    centered "{size=+10}Please interrogate suspects solely on the basis of evidence collected.{/size}"
    
    pause 1.0
    
    # Transition to interrogation background
    scene bg_foyer
    with fade
    
    # Introduce Edward
    show edward_neutral at center, slidein_left with None
    e "Detective, I'll answer your questions — but make it quick."
    hide edward_neutral with med_dissolve
    
    # Introduce Clara
    show clara_neutral at center, slidein_right with None
    c "I have nothing to hide. Ask what you will."
    hide clara_neutral with med_dissolve
    
    # Introduce Margaret
    show margaret_neutral at center, slidein_left with None
    m "This whole affair is dreadful. But I'll cooperate."
    hide margaret_neutral with med_dissolve
    
    # Introduce Doctor
    show halberd_neutral at center, slidein_right with None
    h "If this clears the air, then so be it."
    hide halberd_neutral with med_dissolve
    
    # Fade out and back in with the interrogation room
    scene black with fade
    scene bg_foyer with fade
    
    # End introduction and jump to main interrogation phase
    jump interrogation_phase2

# Expanded seed phrases for question categories (~8 per category as specified)
define QUESTION_CATEGORIES = {
    "alibi": [
        "where were you", "what were you doing", "can anyone verify", 
        "do you have an alibi", "can you prove your whereabouts",
        "who saw you", "were you alone", "what time"
    ],
    "evidence": [
        "what about the glass", "explain the handkerchief", "what about the letter",
        "do you recognize this evidence", "is this yours", 
        "does this look familiar", "how do you explain this", "what do you know about the clues"
    ],
    "motive": [
        "why would you kill him", "did you hate him", "what did you gain",
        "were you angry with him", "did you want him dead", 
        "what was your motive", "did you benefit", "did you argue with him"
    ],
    "relationships": [
        "how did you get along", "what about the others", "who else had reason","do you love him",
        "tell me about the family", "what was your relationship like", 
        "who might have done it", "tell me about edward/clara/margaret/doctor", "how were things between you"
    ],
    # New accusation category with seed phrases
    "accusation": [
        "why accuse", "why suspect", "why blame", "who would you accuse"
        "why are you pointing at", "why do you think", 
        "do you think they did it", "who do you suspect", "who do you think killed him"
    ]
}

# Add semantic intents used by best_intent from the backend (easy to extend later)
define INTERROGATION_INTENTS = [
    {
        "id": "alibi",
        "canonical": "ask about alibi",
        "synonyms": [
            "where were you", "where were you last night", "what were you doing",
            "your whereabouts", "can anyone verify your location",
            "can you prove your whereabouts", "do you have an alibi",
            "who saw you", "were you alone", "what time were you there",
            "on the night of the murder", "before he died where were you",
            "last evening timeline", "account for your time"
        ],
    },
    {
        "id": "evidence",
        "canonical": "ask about evidence",
        "synonyms": [
            "what about the glass", "broken glass", "broken window",
            "explain the handkerchief", "bloody cloth", "cloth with blood",
            "what about the letter", "burnt letter", "burnt paper", "half-burnt letter",
            "do you recognize this evidence", "is this yours", "does this belong to you",
            "does this look familiar", "how do you explain this", "tell me about this clue"
        ],
    },
    {
        "id": "motive",
        "canonical": "ask about motive",
        "synonyms": [
            "why would you kill him", "did you hate him", "what did you gain",
            "did you benefit", "what was your motive", "why kill","did you guys talk","did you have a fight","what happened last night"
            "were you angry with him", "did you want him dead", "reason to do it",
            "what would you get out of this", "inheritance motive"
        ],
    },
    {
        "id": "relationships",
        "canonical": "ask about relationships",
        "synonyms": [
            "how did you get along", "what was your relationship like","did you like him",
            "tell me about the family", "how were things between you","love","did you love him","did he love you",
            "who else had reason", "what about the others",
            "did you argue with him", "tension between you",
            "talk to your father before he died", "feelings toward edward",
            "feelings toward clara", "feelings toward margaret", "feelings toward the doctor"
        ],
    },
    {
        "id": "accusation",
        "canonical": "accuse or ask who they suspect",
        "synonyms": [
            "i think you did it", "did you kill him", "you killed him",
            "i accuse you", "i'm accusing you", "you are the killer",
            "who do you suspect", "who would you accuse", "who killed him",
            "who murdered him", "is edward the killer", "is clara guilty",
            "is margaret responsible", "did the doctor do it", "do you think they did it",
            "why suspect edward", "why blame clara", "why accuse margaret", "why accuse the doctor"
        ],
    },
]

# Story-faithful suspect responses with added accusation replies
define SUSPECT_RESPONSES = {
    "Edward": {
        "alibi": "I'm miserable right now. I was in the dining hall drinking. The servants saw me—though I doubt they'll speak up.",
        "evidence": "That's personal. Broken glass? That window was weak for months. The letter? Ashroff burned plenty. Handkerchiefs? Never mine.",
        "motive": "I agree, we argued. He was my father, and we fought. But blood is blood—I'd never go that far.",
        "relationships": "He is my father who died but I did notice, Clara quarreled with him more than anyone. Always tension in their voices. Ask her if you doubt me.",
        "accusation": "Clara had bitter quarrels with Ashroff. She had more reason than I to wish him dead. And don't overlook the doctor—always hovering, administering his 'treatments'.",
        "why_would_kill": "Clara had every reason—Father humiliated her over her secret correspondences. And the doctor? He wanted Father gone so he could meddle in our inheritance."
    },
    "Clara": {
        "alibi": "I'm miserable right now. I will only answer questions related to the case. I was in the music room, playing the piano. No one else was there. I can't prove it… but why should I lie?",
        "evidence": "That's personal. That letter? Smudged words could resemble my hand, but they are not mine. The glass and handkerchief? They prove nothing.",
        "motive": "Ashroff was difficult, yes. But murder? No! I loved him in my own way. Why would I wish him dead?",
        "relationships": "Ashroff is my father. Edward's temper often frightened Ashroff. Margaret avoids conflict. And the doctor—always meddling in family affairs.",
        "accusation": "Edward's temper is notorious. He lashes out at anyone, even his own father. Margaret may seem quiet, but she harbored deep resentments toward Ashroff.",
        "why_would_kill": "Edward often lost control. If rage blinded him, he could do the unthinkable. Margaret too—she kept silent, but silence hides bitterness."
    },
    "Margaret": {
        "alibi": "I will only answer questions related to the case. I was in the garden, breathing the night air. No one was with me… I prefer solitude.",
        "evidence": "That's personal. The handkerchief resembles mine, but I cannot swear it is. Glass shatters often here. Letters burn in every hearth.",
        "motive": "Ashroff was harsh, but murder is monstrous. I gain nothing from his death—except sorrow.",
        "relationships": "I am miserable right now. Ashroff was my dear husband. I know who did it, Edward's anger was well known. Clara… she hid her resentment behind grace. And Halbert, quarreled over Ashroff's health.",
        "accusation": "The doctor was always concerned about Ashroff's will. Clara pretended to love him, but her eyes betrayed her true feelings. Look closely at them both.",
        "why_would_kill": "I'm not sure about what I think. Edward's inheritance was motive enough. Clara's endless quarrels drove Ashroff mad. Both had stronger reasons than I ever did."
    },
    "Doctor": {
        "alibi": "I will only answer questions related to the case. I was in the library, recording notes on his declining health. The butler may have seen me pass.",
        "evidence": "That's personal. I own many bloodied cloths—tools of my trade. That proves nothing. As for the glass and letter, they are irrelevant to me.",
        "motive": "He ignored my medical advice, true. But why would I kill a man who was my patient? His death profits me nothing.",
        "relationships": "Ashroff's kin circled him like vultures. Edward's rage, Clara's bitterness, Margaret's silence—all more dangerous than my counsel.",
        "accusation": "Ashroff had one of his kidneys failed. Edward stood to inherit the most. His outbursts were legendary—even Ashroff feared him at times. And Margaret, so quiet, but so observant... perhaps too observant.",
        "why_would_kill": "I'm not sure about what I think. Edward stood to gain the most in wealth. Clara in freedom. Motive surrounds them both."
    }  
}

# Keep track of interrogation state
default current_suspect_index = 0
default questions_asked = 0
default detective_question = ""
default SUSPECT_ORDER = ["Edward", "Clara", "Margaret", "Doctor"]
default SUSPECT_SPRITES = {"Edward": "edward", "Clara": "clara", "Margaret": "margaret", "Doctor": "halberd"}

# Function to determine the category of a question using NLP similarity
# Updated to handle both "accusation" category and "why_would_kill" questions
init python:
    import re

    # Centralized fallback text the suspect will say
    FALLBACK_INTERROGATION_TEXT = "i dont know what you're asking or saying."

    # Minimal normalized length to consider a question meaningful
    MIN_QUESTION_LEN = 3

    # Domain vocabulary required for a question to be considered relevant
    DOMAIN_KEYWORDS = {
        # interrogatives / directives
        "who","what","where","when","why","how","did","do","does","can","could",
        "would","will","is","are","was","were","explain","tell me","show me",
        # categories / nouns
        "alibi","motive","evidence","clue","letter","handkerchief","glass","window",
        "relationship","relationships","argue","fight","talk","speak","last night","timeline",
        "benefit","gain","inherit","inheritance","suspect","accuse","accusation","murder","murdered","kill","killer",
        # suspect names
        "edward","clara","margaret","doctor","halberd","dr"
    }

    # Patterns that indicate chit-chat / compliments / irrelevant content
    IRRELEVANT_PATTERNS = [
        # compliments/flirt to the speaker
        re.compile(r"\b(you( are|re|re)?|ur)\s+(so\s+)?(beautiful|pretty|handsome|cute|lovely|gorgeous|sexy|hot|amazing|smart|nice|awesome)\b", re.I),
        re.compile(r"\b(beautiful|pretty|handsome|cute|lovely|gorgeous|sexy|hot)\b", re.I),
        # greetings/small talk/thanks
        re.compile(r"^\s*(hello|hi|hey|yo|sup|good (morning|evening|night))\b", re.I),
        re.compile(r"\b(thanks|thank you|nice to meet you|how are you|hru)\b", re.I),
        # memes/short interjections
        re.compile(r"\b(lol+|lmao+|rofl|haha+|hehe+|bruh|wtf|omg|k|ok|okay|cool|nice|wow)\b", re.I),
        # meta/commands
        re.compile(r"\b(save|load|pause|resume|skip|settings|options|inventory|help|quit|exit)\b", re.I),
        # ascii art / repeated punctuation
        re.compile(r"^[\W_]+$", re.I),
        # mostly numbers
        re.compile(r"^\d[\d\s]*$"),
    ]

    # Emoji detector
    EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U00002600-\U000026FF]")

    # Accusation-style statements (allowed even without a question mark)
    ACCUSATION_PATTERNS = [
        re.compile(r"\b(i\s+accuse|i'm accusing|im accusing|you\s+(killed|murdered)\b)", re.I),
        re.compile(r"\b(you\s+did\s+it)\b", re.I),
        re.compile(r"\b(is|was)\s+(edward|clara|margaret|doctor|dr\.?\s*halberd)\s+(the\s+)?(killer|murderer)\b", re.I),
    ]

    STOPWORDS = {
        "the","a","an","and","or","but","if","then","else","of","to","in","on","for",
        "with","about","as","by","at","from","into","over","after","before","under",
        "between","without","within","than","too","very","so","just","only","that",
        "this","these","those","it","its","you","your","yours","me","my","mine",
        "we","our","ours","they","their","theirs","he","him","his","she","her","hers",
        "be","am","is","are","was","were","been","being","do","does","did","doing"
    }

    def _normalize_question(s):
        return (s or "").strip().lower()

    def _contains_domain_keyword(s):
        return any(k in s for k in DOMAIN_KEYWORDS)

    def _looks_like_question(s):
        if "?" in s:
            return True
        # starts with an interrogative/helper verb
        return bool(re.match(r"^\s*(who|what|where|when|why|how|did|do|does|can|could|would|will|is|are|was|were|tell me|explain)\b", s))

    def _is_accusation(s):
        return any(p.search(s) for p in ACCUSATION_PATTERNS)

    def _too_few_content_words(s):
        tokens = [t for t in re.findall(r"[a-z0-9']+", s) if t not in STOPWORDS]
        return len([t for t in tokens if len(t) >= 3]) < 2

    def _is_irrelevant_input(s):
        """
        Returns True if the input looks like small talk/compliments/noise,
        lacks domain keywords, doesn't look like a question, and isn't a valid accusation.
        """
        if not s:
            return True

        # emoji-only or contains many emojis
        if EMOJI_RE.search(s) and not _contains_domain_keyword(s):
            return True

        # direct irrelevant patterns
        if any(p.search(s) for p in IRRELEVANT_PATTERNS):
            # If clearly smalltalk and no domain cues, irrelevant.
            if not _contains_domain_keyword(s):
                return True

        # allow accusation-like statements even if not a question
        if _is_accusation(s):
            return False

        # require question-like form OR domain keywords
        if not _looks_like_question(s) and not _contains_domain_keyword(s):
            return True

        # require at least a couple of content words unless there are domain cues
        if _too_few_content_words(s) and not _contains_domain_keyword(s):
            return True

        return False

    def classify_question(question_text, threshold=0.4):
        """
        Primary classifier using backend best_intent with INTERROGATION_INTENTS.
        Returns (category, score, matched_bool).
        """
        result = best_intent(question_text or "", INTERROGATION_INTENTS, threshold=0.35)
        return (result.get("best_id") or "", float(result.get("best_score", 0.0)), bool(result.get("matched", False)))

    def get_question_category(question_text):
        """
        Maps natural questions to a controlled interrogation category.
        Keeps outputs restricted to SUSPECT_RESPONSES keys only.
        """
        question = _normalize_question(question_text)

        # Guard: extremely short/empty inputs immediately fallback
        if len(question) < MIN_QUESTION_LEN:
            renpy.log("Interrogation classify: too short/empty -> fallback")
            return "", 0.0

        # Strong irrelevant filter (compliments, greetings, emojis, commands, noise)
        if _is_irrelevant_input(question):
            renpy.log("Interrogation classify: irrelevant/smalltalk/noise -> fallback")
            return "", 0.0

        # Special direct handling for "who killed" style questions -> route to why_would_kill
        if ("who killed" in question) or ("who do you think killed" in question) or ("who murdered" in question):
            renpy.log("Direct who-killed mapping -> why_would_kill")
            return "why_would_kill", 1.0

        # First pass: semantic intent matching
        cat, score, matched = classify_question(question, threshold=0.4)

        # If semantic pass doesn't confidently match, do a light seed-phrase pass as a backup
        if not matched:
            best_category = ""
            best_score = 0.0
            for category, seed_phrases in QUESTION_CATEGORIES.items():
                for phrase in seed_phrases:
                    s = check_similarity(question, phrase)
                    if s > best_score:
                        best_score = s
                        best_category = category
            cat = best_category or cat
            score = max(score, best_score)

        renpy.log(f"Interrogation classify: '{question_text}' => {cat} ({score:.3f})")
        return cat or "", score

    def _say_by_suspect(suspect, line):
        """
        Dispatch helper so fallback lines are spoken by the current suspect.
        """
        if suspect == "Edward":
            renpy.say(e, line)
        elif suspect == "Clara":
            renpy.say(c, line)
        elif suspect == "Margaret":
            renpy.say(m, line)
        else:  # Doctor
            renpy.say(h, line)

# Main interrogation phase
label interrogation_phase2:
    # Initialize for first suspect
    $ current_suspect = SUSPECT_ORDER[current_suspect_index]
    $ questions_asked = 0

    # Continue until we've gone through all suspects
    while current_suspect_index < len(SUSPECT_ORDER):
        # Set the scene for each suspect
        scene bg_foyer
        with fade

        # Show the current suspect based on the index
        $ current_suspect = SUSPECT_ORDER[current_suspect_index]
        $ suspect_sprite = SUSPECT_SPRITES[current_suspect]
        $ suspect_char = suspect_sprite + "_neutral"

        # Display the correct character sprite
        show expression suspect_char at center
        with dissolve

        # Introduction line for each suspect when starting their questioning
        if questions_asked == 0:
            if current_suspect == "Edward":
                e "Ask your questions, detective. I have nothing to hide."
            elif current_suspect == "Clara":
                c "What would you like to know? I'll try to be helpful."
            elif current_suspect == "Margaret":
                m "Yes, detective? How can I assist your investigation?"
            else: # Doctor
                h "I'm at your disposal. What questions do you have?"

        # Call the question input screen
        call screen question_input_screen

        # Process the question using semantic intent classification
        $ category, score = get_question_category(detective_question)

        # Controlled fallback per instructions if not relevant or unmapped
        if (score < 0.4) or (category not in SUSPECT_RESPONSES.get(current_suspect, {})):
            # Suspect speaks the fallback line
            $ _say_by_suspect(current_suspect, FALLBACK_INTERROGATION_TEXT)
        else:
            # Display the appropriate response from the suspect (dictionary-controlled)
            $ response = SUSPECT_RESPONSES[current_suspect][category]
            if current_suspect == "Edward":
                e "[response]"
            elif current_suspect == "Clara":
                c "[response]"
            elif current_suspect == "Margaret":
                m "[response]"
            else: # Doctor
                h "[response]"

        # Increment the question counter
        $ questions_asked += 1

        # Check if we've asked enough questions to move to the next suspect
        if questions_asked >= 4:
            # Hide the current suspect
            hide expression suspect_char
            with dissolve

            # Move to the next suspect
            $ current_suspect_index += 1
            $ questions_asked = 0

            # If we've gone through all suspects, end the interrogation phase
            if current_suspect_index >= len(SUSPECT_ORDER):
                # Jump to the final phase
                jump interrogation_phase3

            # Brief transition between suspects
            scene black
            with fade
            pause 0.5

# Input screen for detective questions with improved styling
screen question_input_screen():
    modal True
    
    # Background frame for the input area
    frame:
        style "input_frame"
        xalign 0.5
        yalign 0.95
        xsize 800
        padding (20, 20)
        
        vbox:
            spacing 10
            xalign 0.5
            
            text "Ask your question:" size 28 xalign 0.5 color "#FFD700"
            
            # Input field with gold border as specified in instructions.txt
            frame:
                background "#FFD700"
                padding (2, 2)
                
                frame:
                    background "#333333"  # Dark grey input background as specified
                    padding (10, 8)
                    xfill True
                    
                    input:
                        style "evidence_input_text"  # Using the exact style from evidence_system
                        value VariableInputValue("detective_question")
                        length 100
                        copypaste True
            
            # Submit button
            textbutton "Ask":
                style "button"
                text_color "#FFD700"
                xalign 0.5
                action Return()

# Style definitions for the input screen
style input_frame:
    background Frame("gui/frame.png", Borders(10, 10, 10, 10))
    
style input_text:
    color "#FFFFFF"
    size 24
    xalign 0.0
    xpadding 10
    ypadding 8

# Replace the existing placeholder interrogation_phase3 label with this implementation
label interrogation_phase3:
    scene black
    with fade
    
    centered "{size=+10}Your final accusation, detective…{/size}"
    
    pause 1.5
    
    # Initialize the final accusation variable
    $ final_accusation = ""
    
    # Start the accusation process
    label accusation_loop:
        # Call the accusation input screen
        call screen accusation_input_screen

        # Process the accusation using the helper function
        $ accused_suspect, similarity_score = get_accused_suspect(final_accusation)
        $ renpy.log(f"Player accused: {accused_suspect}, score: {similarity_score}")

        # Branch based on who was accused
        if accused_suspect == "Clara":
            # Player correctly accused Clara - go to the good ending
            jump ending_clara_confession

        elif accused_suspect in ("Unknown", "Invalid"):
            # Any input not mapping to a suspect → notify and retry
            n "Write the name of the suspects."
            $ final_accusation = ""  # Clear previous input
            jump accusation_loop

        else:
            # Player accused Edward/Margaret/Doctor - wrong ending
            jump ending_wrong_accusation

# Helper function to determine which suspect was accused - with strict name/synonym handling
init python:
    def get_accused_suspect(accusation_text):
        """
        Strictly map the player's input to one of the suspects using keywords and similarity.
        Allowed suspects: Edward, Clara, Margaret, Doctor (Dr Halberd).
        Returns (suspect_name, similarity_score). If not a suspect, returns ("Invalid", score).
        """
        import re

        suspects = {
            "Edward": {"edward", "ed"},
            "Clara": {"clara"},
            "Margaret": {"margaret", "maggie", "lady margaret"},
            "Doctor": {"dr", "doctor", "doc", "halberd", "dr halberd", "dr. halberd", "doctor halberd"}
        }

        if not accusation_text or len(accusation_text.strip()) < 2:
            return "Unknown", 0.0

        s = accusation_text.lower().strip()
        s_norm = re.sub(r"[^a-z0-9\s\.]", " ", s)
        s_norm = re.sub(r"\s+", " ", s_norm).strip()

        # Direct keyword containment (high confidence)
        for name, keys in suspects.items():
            for k in keys:
                if k in s_norm:
                    return name, 0.95

        # Similarity fallback across synonyms
        best_name = "Invalid"
        best_score = 0.0
        for name, keys in suspects.items():
            for k in keys:
                score = check_similarity(s_norm, k)
                if score > best_score:
                    best_score = score
                    best_name = name

        # Require solid confidence to avoid random matches
        return (best_name, best_score) if best_score >= 0.6 else ("Invalid", best_score)

# Accusation input screen with styling matching the evidence input screen
screen accusation_input_screen():
    modal True
    
    # Background frame for the input area
    frame:
        style "input_frame"
        xalign 0.5
        yalign 0.95
        xsize 800
        padding (20, 20)
        
        vbox:
            spacing 10
            xalign 0.5
            
            text "Who do you accuse?" size 28 xalign 0.5 color "#FFD700"
            
            # Input field with gold border as specified in instructions.txt
            frame:
                background "#FFD700"
                padding (2, 2)
                
                frame:
                    background "#333333"  # Dark grey input background as specified
                    padding (10, 8)
                    xfill True
                    
                    input:
                        style "evidence_input_text"  # Using the same style as evidence input
                        value VariableInputValue("final_accusation")
                        length 100
                        copypaste True
            
            # Submit button
            textbutton "Accuse":
                style "button"
                text_color "#FFD700"
                xalign 0.5
                action Return()
