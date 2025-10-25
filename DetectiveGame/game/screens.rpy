################################################################################
## Initialization
################################################################################

init offset = -1

################################################################################
## Styles
################################################################################

style default:
    properties gui.text_properties()
    # language gui.language   # <- disabled, avoids AttributeError
    bold False

style input:
    properties gui.text_properties("input", accent=True)   # fixed here
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")

style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5
    bold False

style label_text is gui_text:
    properties gui.text_properties("label", accent=True)
    bold False

style prompt_text is gui_text:
    properties gui.text_properties("prompt")
    bold False

style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"

style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)

################################################################################
## Say Screen (dialogue)
################################################################################

screen say(who, what):

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "namebox"
                text who id "who"

            text what id "what" style "say_dialogue"

        else:
            # Narration (no speaker name)
            text what id "what" style "say_thought"

    if not renpy.variant("small"):
        use quick_menu

init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue
style namebox is default
style namebox_label is say_label

style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height
    yoffset -gui.textbox_bottom_safe_margin   # nudge textbox up a bit
    background Solid("#000000CC")  # semi-transparent black (was image -> gray)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height
    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile)
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5
    color gui.accent_color
    bold False
    outlines []  # no outline -> slimmer look

style say_dialogue:
    properties gui.text_properties("dialogue")
    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos
    textalign gui.dialogue_text_xalign
    size gui.dialogue_text_size
    line_spacing 0
    bold False
    adjust_spacing False
    outlines []  # keep your current outline choice

style say_thought:
    italic True
    textalign gui.dialogue_text_xalign
    size gui.dialogue_text_size
    line_spacing 0
    bold False
    outlines []

# Butler-only styles (apply only when Character b speaks via style_prefix="b")
style b_window is window:
    # Push textbox further up to avoid OS taskbar overlap only for Butler
    yoffset -(gui.textbox_bottom_safe_margin + 36)

style b_say_label is say_label
style b_namebox is namebox
style b_namebox_label is namebox_label

style b_say_dialogue is say_dialogue:
    size gui.dialogue_text_size
    line_spacing 0

# Narration-only styles (apply when Character n speaks via style_prefix="narration")
style narration_window is window:
    # Push textbox up a bit more for narration to avoid OS taskbar overlap
    yoffset -(gui.textbox_bottom_safe_margin + 36)

style narration_say_thought is say_thought:
    size gui.dialogue_text_size
    line_spacing 0
    # Optional: nudge text up a little inside the box
    ypos gui.dialogue_ypos - 4

# Character Definitions
define n = Character(None, style_prefix="narration")   # Narrator
define b = Character("Butler", color="#BFA36B", style_prefix="b")

# Add an Evidence button to the quick menu for easy access
screen quick_menu():

    ## Ensure this appears on screens that support it.
    hbox:
        style_prefix "quick"
        xalign 0.5
        yalign 1.0

        textbutton _("Back") action Rollback()
        textbutton _("History") action ShowMenu("history")
        textbutton _("Skip") action Skip()
        textbutton _("Auto") action Preference("auto-forward", "toggle")
        textbutton _("Save") action ShowMenu("save")
        textbutton _("Q.Save") action QuickSave()
        textbutton _("Q.Load") action QuickLoad()
        textbutton _("Prefs") action ShowMenu("preferences")
        textbutton _("Evidence") action Show("evidence_book")
