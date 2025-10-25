# game/story/investigation.rpy

# Wrapper so the phase can jump here per spec.
label investigation_phase:
    jump investigation

# Fallback investigation label so jumps resolve.
label investigation:
    n "Investigation phase coming soon..."
    jump interrogation

# Add to game/script.rpy
init 1 python:
    # Define placeholder evidence images early in the init process
    if not renpy.has_image("clue_letter"):
        renpy.image("clue_letter", Composite(
            (200, 150),
            (0, 0), Solid("#8B4513"),  # Brown background
            (10, 10), Solid("#F5F5DC", xsize=180, ysize=130),  # Beige paper
            (40, 60), Text("LETTER", size=28, color="#000000", bold=True)
        ))
    if not renpy.has_image("clue_glass"):
        renpy.image("clue_glass", Solid("#87CEEB", xsize=200, ysize=150))
    if not renpy.has_image("clue_handkerchief"):
        renpy.image("clue_handkerchief", Solid("#FFFFFF", xsize=200, ysize=150))