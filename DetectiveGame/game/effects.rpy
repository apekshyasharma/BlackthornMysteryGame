init offset = -1

define slow_dissolve = Dissolve(0.6)
define med_dissolve = Dissolve(0.4)
define fast_dissolve = Dissolve(0.2)
define fade_long = Fade(0.3, 0.1, 0.3, color="#000000")
define flash = Fade(0.05, 0.05, 0.15, color="#FFFFFF")

# Dissolve when changing expressions on the same tag (e.g., butler_neutral -> butler_angry)
define config.say_attribute_transition = med_dissolve

# Background base: soft fade in/out
transform bg_fade:
    on show:
        alpha 0.0
        linear 0.35 alpha 1.0
    on hide:
        linear 0.25 alpha 0.0

# Character base: short dissolve in/out
transform char_base:
    on show:
        alpha 0.0
        linear 0.25 alpha 1.0
    on hide:
        linear 0.20 alpha 0.0

# Subtle idle breathing to keep sprites alive
transform subtle_idle:
    yoffset 0
    linear 1.6 yoffset -2
    linear 1.6 yoffset 0
    repeat

# Slide-in entrances
transform slidein_left:
    xoffset -80
    alpha 0.0
    easeout 0.35 xoffset 0 alpha 1.0

transform slidein_right:
    xoffset 80
    alpha 0.0
    easeout 0.35 xoffset 0 alpha 1.0

# Slide-out exits
transform slideout_left:
    easein 0.30 xoffset -100 alpha 0.0

transform slideout_right:
    easein 0.30 xoffset 100 alpha 0.0

# Slight bounce when speaking / active
transform talk_bounce:
    yoffset 0
    easein 0.06 yoffset -6
    easeout 0.12 yoffset 0
    pause 0.60
    repeat

# Existing small shake 
transform shake_small:
    xoffset 0
    linear 0.03 xoffset 8
    linear 0.03 xoffset -8
    repeat 4

# Existing medium shake
transform shake_medium:
    xoffset 0
    linear 0.03 xoffset 14
    linear 0.03 xoffset -14
    repeat 6

# Screen-wide shake for storm effects (applied to a layer)
transform screen_shake_small:
    xoffset 0 yoffset 0
    linear 0.03 xoffset 10 yoffset -6
    linear 0.03 xoffset -8 yoffset 8
    linear 0.03 xoffset 6 yoffset -4
    linear 0.03 xoffset 0 yoffset 0

transform screen_shake_medium:
    xoffset 0 yoffset 0
    linear 0.03 xoffset 16 yoffset -10
    linear 0.03 xoffset -14 yoffset 12
    linear 0.03 xoffset 10 yoffset -8
    linear 0.03 xoffset 0 yoffset 0

# Reusable scene transition label (modular)
label scene_to(bg_name):
    scene expression bg_name
    with fade_long
    return

# Lightning + thunder effect with screen shake (modular)
label lightning_strike(strength="medium"):
    $ thunder_sfx = "audio/thunder.ogg"
    python:
        if renpy.loadable(thunder_sfx):
            renpy.sound.play(thunder_sfx)
    show expression Solid("#FFFFFF") as _lightning_flash
    with flash
    hide _lightning_flash

    if strength == "small":
        show layer master at screen_shake_small
    else:
        show layer master at screen_shake_medium

    $ renpy.pause(0.28)
    show layer master  
    return

# Subtle gold glow pulse used by the evidence input border.
transform gold_glow:
    alpha 0.95
    linear 0.7 alpha 1.0
    linear 0.7 alpha 0.75
    repeat