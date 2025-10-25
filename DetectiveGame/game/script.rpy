label start:
    # Just call the prologue directly instead
    jump prologue

# Renamed from _after_load to avoid colliding with Ren'Py's internal label.
label after_load:
    $ renpy.block_rollback()  # create a fresh rollback boundary after load

    python:
        # Safeguard interrogation defaults
        if not hasattr(store, "current_suspect_index"):
            store.current_suspect_index = 0
        if not hasattr(store, "questions_asked"):
            store.questions_asked = 0
        if not hasattr(store, "detective_question"):
            store.detective_question = ""
        if not hasattr(store, "SUSPECT_ORDER"):
            store.SUSPECT_ORDER = ["Edward", "Clara", "Margaret", "Doctor"]

        # Safeguard evidence phase flag without touching matching logic
        if not hasattr(store, "evidence_phase_done"):
            store.evidence_phase_done = False

    # Dismiss transient UI that could linger across reloads
    hide screen evidence_scene
    hide screen evidence_wait
    hide screen evidence_book
    hide screen question_input_screen
    hide screen interrogation_try_again
    hide screen accusation_input_screen

    return
