# Centralized BGM control using a label callback.
# Only uses renpy.music.play()/stop() and does not modify any story/GUI code.

init -10 python:
    # Map label names to BGM files (under the audio/ folder).
    # This follows the exact scene mapping from instructions.txt.
    _BGM_MAP = {
        # 1) Manor introduction (until Sir Reginald goes to the study room)
        # Start when the prologue begins.
        "prologue": "audio/bgm_storm.ogg",

        # 2) After hall communication + butler announcing murder
        # If dedicated labels exist, keep both keys mapped to the same track.
        "hall_communication": "audio/bgm_prologue.ogg",
        "butler_announces_murder": "audio/bgm_prologue.ogg",

        # 4) Evidence collection until butler finishes explaining the evidences.
        # Start at evidence_collection and keep same track during butler_explains.
        "evidence_collection": "audio/bgm_evidence.ogg",  # label exists
        "butler_explains": "audio/bgm_evidence.ogg",

        # 5) Interrogation phases
        "interrogation_phase1": "audio/bgm_interrogation.ogg",
        "interrogation_phase2": "audio/bgm_interrogation.ogg",

        # 6) Accusation scene (starts with the accusation UI/flow)
        # interrogation_phase3 is the accusation implementation in this project.
        "interrogation_phase3": "audio/bgm_accusation.ogg",  # label exists

        # 7) Ending (post confession/smirk -> outcome)
        "ending": "audio/bgm_prologue.ogg",
        "epilogue": "audio/bgm_prologue.ogg",
        "results": "audio/bgm_prologue.ogg",
        "outcome": "audio/bgm_prologue.ogg",
    }

    _current_bgm = None

    def _bgm_label_callback(name, abnormal):
        """
        Called whenever a label is entered. Smoothly transitions between BGMs
        based on the mapping above. Avoids restarting the same track.
        """
        global _current_bgm

        track = _BGM_MAP.get(name, None)
        if track is None:
            return

        if _current_bgm != track:
            # Stop current track before switching, with fadeout.
            renpy.music.stop(fadeout=2.0)
            # Start the new track with fadein and loop.
            renpy.music.play(track, loop=True, fadein=2.0)
            _current_bgm = track

    # Register the callback so no story code needs to be touched.
    config.label_callback = _bgm_label_callback