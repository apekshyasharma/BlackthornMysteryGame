# game/story/prologue.rpy

label prologue:

    # Scene 1 – Mansion Exterior (Introduction)
    $ _ = renpy.call("scene_to", "bg manor")
    $ renpy.music.play("audio/bgm_storm.ogg", loop=True, fadein=2.0)
    n "Ashford Manor sits alone on the Yorkshire moors. Tonight's storm has cut off all roads and phone lines. In the flickering gaslight, secrets are about to be revealed."

    # Scene 2 – Corridor with Butler (Family Introduction)
    $ renpy.music.stop(fadeout=2.0)
    $ _ = renpy.call("scene_to", "bg corridor")
    $ renpy.music.play("audio/bgm_prologue.ogg", loop=True, fadein=2.0)
    show butler_neutral at left, slidein_left
    with None
    b "The Ashfords seem like the perfect family to outsiders. But Sir Reginald controls everyone's fate, and his friend Dr. Halberd knows all his secrets."
    hide butler_neutral with med_dissolve

    # Scene 3 – Dining Room (Character Introductions)
    $ _ = renpy.call("scene_to", "bg dining")

    show reginald_neutral at center, slidein_left
    with None
    r "Family is everything. Tonight, I have decisions to announce—matters that will shape our legacy."
    hide reginald_neutral with med_dissolve

    show clara_neutral at right, slidein_right
    with None
    c "Art is freedom… yet freedom comes at a price Father will never allow me to pay."
    hide clara_neutral with med_dissolve

    show edward_smirk at left, slidein_left
    with None
    e "One day, the estate will be mine. If only Father would loosen his iron grip."
    hide edward_smirk with med_dissolve

    show margaret_neutral at right, slidein_right
    with None
    m "Our family must endure, no matter the cost. Appearances must be preserved… always."
    hide margaret_neutral with med_dissolve

    show halberd_neutral at left, slidein_left
    with None
    h "I have stood beside Reginald for years. His body weakens, but his will remains unbreakable."
    hide halberd_neutral with med_dissolve

    show reginald_neutral at center, slidein_right
    with None
    r "Excuse me. I must retire to my study… urgent matters await."
    hide reginald_neutral with med_dissolve

    n "Lightning flashes. The storm grows heavier."
    call lightning_strike("medium")

    # Scene 4 – Corridor Return (The Shift)
    $ _ = renpy.call("scene_to", "bg corridor")
    show butler_angry at right, slidein_right
    with None
    b "But the night turned deadly. The laughter stopped, the storm grew louder... and then Sir Reginald Ashford was found dead."
    hide butler_angry with med_dissolve

    # Scene 5 – Study (Dead CG Reveal)
    $ _ = renpy.call("scene_to", "bg study")
    show reginald_dead at center with slow_dissolve
    b "From that moment, the Ashford family was bound not by love… but by suspicion."
    $ renpy.music.stop(fadeout=2.0)

    # Connect to funeral scene as per instructions.txt
    jump funeral_scene
