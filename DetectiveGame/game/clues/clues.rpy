# clues/clues.rpy
# Manages the evidence collection system

default evidence_book = []

# Define the evidence images directly 
init -100 python:
    # Create the evidence images with the EXACT names used in EVIDENCE_CATALOG
    if not renpy.has_image("clue_glass"):
        renpy.image("clue_glass", Composite(
            (200, 150),
            (0, 0), Solid("#87CEEB"),  # Light blue
            (10, 10), Solid("#ADD8E6", xsize=180, ysize=130),  # Lighter blue
            (50, 60), Text("GLASS", size=24, color="#000000", bold=True)
        ))
    
    if not renpy.has_image("clue_handkerchief"):
        renpy.image("clue_handkerchief", Composite(
            (200, 150),
            (0, 0), Solid("#FFFFFF"),  # White
            (10, 10), Solid("#F0F0F0", xsize=180, ysize=130),  # Off-white
            (30, 60), Text("CLOTH", size=24, color="#000000", bold=True)
        ))
    
    if not renpy.has_image("clue_letter"):
        renpy.image("clue_letter", Composite(
            (200, 150),
            (0, 0), Solid("#8B4513"),  # Brown background
            (10, 10), Solid("#F5F5DC", xsize=180, ysize=130),  # Beige paper
            (40, 60), Text("LETTER", size=24, color="#000000", bold=True)
        ))

    # Create thumbnails too
    if not renpy.has_image("thumb_glass"):
        renpy.image("thumb_glass", Composite(
            (100, 75),
            (0, 0), Solid("#87CEEB"),  # Light blue
            (5, 5), Solid("#ADD8E6", xsize=90, ysize=65),  # Lighter blue
            (25, 30), Text("GLASS", size=12, color="#000000", bold=True)
        ))
    
    if not renpy.has_image("thumb_handkerchief"):
        renpy.image("thumb_handkerchief", Composite(
            (100, 75),
            (0, 0), Solid("#FFFFFF"),  # White
            (5, 5), Solid("#F0F0F0", xsize=90, ysize=65),  # Off-white
            (15, 30), Text("CLOTH", size=12, color="#000000", bold=True)
        ))
    
    if not renpy.has_image("thumb_letter"):
        renpy.image("thumb_letter", Composite(
            (100, 75),
            (0, 0), Solid("#8B4513"),  # Brown background
            (5, 5), Solid("#F5F5DC", xsize=90, ysize=65),  # Beige paper
            (20, 30), Text("LETTER", size=12, color="#000000", bold=True)
        ))

label add_clue(clue_name):
    if clue_name not in evidence_book:
        $ evidence_book.append(clue_name)
        n "You collected [clue_name]."
    return

# Use only catalog images with full file paths. Check if they're loadable.
init python:
    def _catalog_images_or_x(eid):
        meta = EVIDENCE_CATALOG.get(eid, {})
        idle = meta.get("idle")
        hover = meta.get("hover", idle)
        
        # Try to load the file if it's a file path
        if idle and renpy.loadable(idle):
            return idle, hover if hover and renpy.loadable(hover) else idle
        
        # Fall back to a red X if file not loadable
        red_x = Text("X", color="#ff0000", size=28, outlines=[(1, "#000000")])
        return red_x, red_x

# Evidence scene overlay with exact positions from instructions.txt
screen evidence_scene():
    zorder 50

    default _hover_glass = False
    default _hover_handkerchief = False
    default _hover_letter = False

    # clue_handkerchief: xpos=226, ypos=591, zoom 0.8 idle / 0.9 hover
    $ idle_hk, hover_hk = _catalog_images_or_x("clue_letter")
    if "clue_letter" not in evidence_collected:
        imagebutton:
            idle idle_hk
            hover hover_hk
            xpos 226  # EXACT position from instructions.txt
            ypos 591  # EXACT position from instructions.txt
            at Transform(zoom=0.9 if _hover_letter else 0.8)
            focus_mask True
            hovered SetScreenVariable("_hover_letter", True)
            unhovered SetScreenVariable("_hover_letter", False)
            action [ SetVariable("evidence_guess", ""),
                    Show("evidence_input_popup", eid="clue_letter") ]
    else:
        add idle_hk:
            xpos 226
            ypos 591
            zoom 0.8
            alpha 0.55

    # clue_glass: xpos=1054, ypos=573
    $ idle_gl, hover_gl = _catalog_images_or_x("clue_glass")
    if "clue_glass" not in evidence_collected:
        imagebutton:
            idle idle_gl
            hover hover_gl
            xpos 1054  # EXACT position from instructions.txt
            ypos 573   # EXACT position from instructions.txt
            at Transform(zoom=0.9 if _hover_glass else 0.8)
            focus_mask True
            hovered SetScreenVariable("_hover_glass", True)
            unhovered SetScreenVariable("_hover_glass", False)
            action [ SetVariable("evidence_guess", ""),
                    Show("evidence_input_popup", eid="clue_glass") ]
    else:
        add idle_gl:
            xpos 1054
            ypos 573
            zoom 0.8
            alpha 0.55

    # clue_handkerchief: xpos=686, ypos=800
    $ idle_lt, hover_lt = _catalog_images_or_x("clue_handkerchief")
    if "clue_handkerchief" not in evidence_collected:
        imagebutton:
            idle idle_lt
            hover hover_lt
            xpos 1010  # EXACT position from instructions.txt
            ypos 500  # EXACT position from instructions.txt
            at Transform(zoom=0.9 if _hover_handkerchief else 0.8)
            focus_mask True
            hovered SetScreenVariable("_hover_handkerchief", True)
            unhovered SetScreenVariable("_hover_handkerchief", False)
            action [ SetVariable("evidence_guess", ""),
                    Show("evidence_input_popup", eid="clue_handkerchief") ]
    else:
        add idle_lt:
            xpos 1010
            ypos 500
            zoom 0.8
            alpha 0.55
            
    # Evidence Book button
    hbox:
        xalign 1.0
        yalign 0.05
        spacing 10
        xoffset -20
        textbutton "Evidence Book" action Show("evidence_book") style "quick_button"


