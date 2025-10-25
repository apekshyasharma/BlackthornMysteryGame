# Evidence collection phase - starts from prologue

# Main entry point for evidence collection phase
label evidence_collection:
    scene bg_study
    with fade
    
    $ evidence_phase_done = False
    show screen evidence_scene

    # Wait here while allowing UI interactions without triggering the infinite loop guard
    jump evidence_collection_wait

label evidence_collection_wait:
    pause 0.25
    if evidence_phase_done:
        hide screen evidence_scene
        jump evidence_collection_end
    else:
        jump evidence_collection_wait

# End of evidence collection phase - transitions to butler explanation
label evidence_collection_end:
    hide screen evidence_scene
    # Remove the direct jump to investigation and add butler explanation
    jump butler_explains
