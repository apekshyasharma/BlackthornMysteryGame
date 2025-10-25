# game/butler_explains.rpy
# Evidence explanation scene where the butler interprets the collected clues

label butler_explains:
    # Set background to study (same as evidence collection)
    scene bg study
    with fade
    
    # Butler enters
    show butler_neutral at center
    with dissolve
    
    # Butler comments on the Broken Glass
    b "These glass shards... from the eastern study window. Master Edward always said that frame was fragile. Dr. Halberd checked those shutters earlier - said they were secure."

    # Brief pause for dramatic effect
    pause 0.5
    
    # Butler comments on the Bloody Handkerchief
    b "A bloodstained handkerchief... Lady Margaret carries embroidered ones like this, but there's no initials. Could be hers... or just one of the doctor's medical rags."

    # Brief pause
    pause 0.5
    
    # Butler comments on the Half-burnt Letter
    b "A charred letter fragment... the handwriting looks like Lady Clara's, but Edward burns papers after fights with the Master. I can make out 'inheritance' and 'betrayal.'"

    # Closing line
    b "These are but my humble thoughts, detective. I leave the true deduction to your keen eye."
    
    # Butler exits
    hide butler_neutral
    with dissolve
    
    # Fade out
    scene black
    with fade
    
    # Show fullscreen message
    centered "{size=+10}Interrogation stage starting soon.{/size}"
    pause 2.0
    
    # Fade to black and jump to interrogation
    scene black
    with fade
    
    jump interrogation_start