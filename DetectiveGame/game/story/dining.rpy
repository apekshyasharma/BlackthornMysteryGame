# Dining Hall Scene - long dining table, storm sound continues softly

label dining_scene:
    # Set the background
    scene expression "images/bg/bg_dining.png"
    with fade
    # Stop funeral BGM at the start of the dining scene
    $ renpy.music.stop(fadeout=2.0)
    # Play prologue BGM throughout the dining scene
    $ renpy.music.play("audio/bgm_prologue.ogg", loop=True, fadein=2.0)

    play sound "audio/rain.ogg" loop
    play sound "audio/thunder.ogg" fadein 1.0

    # Show only one character at a time (cinematic style)
    show clara_angry at center
    with dissolve

    c "We cannot let Father's death go unanswered."
    c "I will hire a detective. Someone impartial."

    hide clara_angry
    show edward_angry at center
    with dissolve
    
    e "No! We don't need outsiders poking through our lives."
    e "We can handle this ourselves."

    hide edward_angry
    show clara_angry at center
    with dissolve
    
    c "Edward, your pride will not solve this mystery."
    c "The truth must come out, no matter the cost."

    hide clara_angry
    show margaret_angry at center
    with dissolve
    
    m "Clara is right. We need help."

    hide margaret_angry
    show halberd_angry at center
    with dissolve
    
    h "Let the detective do their work. We owe Reginald that much."

    hide halberd_angry
    # Clara changes to neutral at the end as specified in instructions
    show clara_neutral at center
    with dissolve
    
    c "Very well. I trust you all will cooperate."
    c "You. I want you to begin in Father's study. Find anything that might explain what happened."

    hide clara_neutral
    with dissolve
    
    stop sound
    with fade
    # Stop dining BGM before leaving the scene
    $ renpy.music.stop(fadeout=2.0)

    # Jump to investigation as in the original
    jump evidence_collection