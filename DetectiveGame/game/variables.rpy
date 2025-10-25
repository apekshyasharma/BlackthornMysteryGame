# game/variables.rpy
# Defines characters, expressions, backgrounds, and CGs

# Character Definitions
define n = Character(None, what_prefix="\"", what_suffix="\"")   # Narrator
define b = Character("Butler", color="#BFA36B")   # was "#c0c0c0"
define r = Character("Sir Reginald", color="#c04040")
define c = Character("Clara", color="#40c0c0")
define e = Character("Edward", color="#c08040")
define m = Character("Lady Margaret", color="#8040c0")
define h = Character("Dr. Halberd", color="#4080c0")

# --------------------------------------------------------------------
# BACKGROUNDS
# --------------------------------------------------------------------
image bg manor    = At("images/bg/bg_mansion.png", bg_fade)
image bg corridor = At("images/bg/bg_corridor.png", bg_fade)
image bg dining   = At("images/bg/bg_lounge.png", bg_fade)  # lounge replacement
image bg study    = At("images/bg/bg_study.png", bg_fade)
image bg_funeral  = At("images/bg/bg_funeral.png", bg_fade)  # Added bg_funeral
# Alias to satisfy "bg_study" naming in spec
image bg_study    = At("images/bg/bg_study.png", bg_fade)

# --------------------------------------------------------------------
# CG
# --------------------------------------------------------------------
image reginald_dead = At("images/cg/victim_dead.png", char_base)

# --------------------------------------------------------------------
# CHARACTERS - EXPRESSIONS
# --------------------------------------------------------------------

# Butler
image butler_neutral = At("images/characters/butler_neutral.png", char_base, subtle_idle)
image butler_angry   = At("images/characters/butler_angry.png",   char_base, subtle_idle)

# Sir Reginald
image reginald_neutral = At("images/characters/victim_alive.png", char_base, subtle_idle)

# Clara
image clara_neutral = At("images/characters/clara_neutral.png", char_base, subtle_idle)
image clara_nervous = At("images/characters/clara_nervous.png", char_base, subtle_idle)

# Edward
image edward_neutral = At("images/characters/edward_neutral.png", char_base, subtle_idle)
image edward_angry   = At("images/characters/edward_angry.png",   char_base, subtle_idle)
image edward_crying  = At("images/characters/edward_crying.png",  char_base, subtle_idle)
image edward_nervous = At("images/characters/edward_nervous.png", char_base, subtle_idle)
image edward_smirk   = At("images/characters/edward_smirk.png",   char_base, subtle_idle)

# Lady Margaret
image margaret_neutral = At("images/characters/margaret_neutral.png", char_base, subtle_idle)
image margaret_angry   = At("images/characters/margaret_angry.png",   char_base, subtle_idle)
image margaret_crying  = At("images/characters/margaret_crying.png",  char_base, subtle_idle)
image margaret_nervous = At("images/characters/margaret_nervous.png", char_base, subtle_idle)
image margaret_smirk   = At("images/characters/margaret_smirk.png",   char_base, subtle_idle)

# Dr. Halberd
image halberd_neutral = At("images/characters/halberd_neutral.png", char_base, subtle_idle)
image halberd_angry   = At("images/characters/halberd_angry.png",   char_base, subtle_idle)
image halberd_crying  = At("images/characters/halberd_crying.png",  char_base, subtle_idle)
image halberd_nervous = At("images/characters/halberd_nervous.png", char_base, subtle_idle)
image halberd_smirk   = At("images/characters/halberd_smirk.png",   char_base, subtle_idle)
