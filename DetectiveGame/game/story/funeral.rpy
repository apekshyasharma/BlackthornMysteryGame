# Funeral Scene - outdoor funeral grounds in the rain

label funeral_scene:
    scene bg_funeral
    with fade
    # Start funeral BGM after death montage narration ended
    $ renpy.music.play("audio/bgm_funeral.ogg", loop=True, fadein=2.0)

    play sound "audio/rain.ogg" loop
    play sound "audio/thunder.ogg"

    # Lightning flash at start
    call lightning_strike("medium")

    # Hide all previous characters first to prevent overlap
    hide edward_neutral
    hide margaret_neutral  
    hide halberd_neutral
    hide clara_neutral
    hide butler_angry
    hide reginald_dead
    with None
    
    # Show only one character at a time (cinematic style)
    show edward_crying at center
    with dissolve
    
    e "He was... he was everything. I can't believe he's gone."
    e "Father always said the manor would stand forever. But now..."

    hide edward_crying
    show margaret_crying at center
    with dissolve
    
    m "Edward, we must be strong. For him. For each other."
    m "The rain will not wash away our grief."

    hide margaret_crying
    show halberd_crying at center
    with dissolve
    
    h "Reginald was a stubborn man. But he did not deserve this end."
    h "We must find the truth, no matter how painful."

    # Lightning flash
    call lightning_strike("small")

    hide halberd_crying
    show clara_crying at center
    with dissolve
    
    c "Enough. We cannot stand here forever, mourning in the rain."
    c "Father would want us to act, not weep."
    c "Inside. All of you. Now."

    hide clara_crying
    with dissolve

    # Ensure funeral BGM plays only in this scene
    $ renpy.music.stop(fadeout=2.0)

    stop sound
    with fade

    jump dining_scene