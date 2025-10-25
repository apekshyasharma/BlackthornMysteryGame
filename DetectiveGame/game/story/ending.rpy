# Endings for the murder mystery

label ending_clara_confession:
    # Clara breaks down and confesses
    scene bg_foyer
    with fade
    
    show clara_crying at center
    with dissolve
    
    c "How... how did you know?"
    c "I... I never meant for it to happen this way..."
    c "Yes... it was me! Father pushed me too far... I couldn't bear his cruelty any longer."
    c "The letter you found... it was from my secret lover. Father threatened to disinherit me if I didn't break it off."
    c "When he confronted me that night, I grabbed the first thing I could find... that glass paperweight."
    
    # Cinematic transition
    scene black
    with fade
    
    # Show epilogue text
    centered "{size=+10}Clara Ashford confessed to the murder of Sir Reginald.{/size}"
    pause 1.0
    centered "{size=+10}The bloody handkerchief was hers, used to clean her hands after the deed.{/size}"
    pause 1.0
    centered "{size=+10}The letter was indeed addressed to her secret lover, which Reginald had discovered.{/size}"
    pause 1.0
    centered "{size=+10}She was arrested and the inheritance was distributed among the remaining family members.{/size}"
    pause 1.0
    
    # Final message
    centered "{size=+15}You solved the case. Justice is served.{/size}"
    pause 2.0
    
    # Return to main menu
    return

label ending_wrong_accusation:
    # Wrong accusation - Clara gets away with murder
    scene bg_foyer
    with fade
    
    show clara_smirk at center
    with dissolve
    
    c "Foolish detective... accusing the wrong person. Now the fortune is mine."
    c "Father's estate passes to me now, and no one will ever know what really happened that night."
    
    # Cinematic transition
    scene black
    with fade
    
    # Show epilogue text
    centered "{size=+10}Your accusation was wrong.{/size}"
    pause 1.0
    centered "{size=+10}Clara Ashford inherited her father's vast fortune.{/size}"
    pause 1.0
    centered "{size=+10}The true culprit walked free, while an innocent was blamed.{/size}"
    pause 1.0
    
    # Final failure message
    centered "{size=+15}You failed. Clara has won.{/size}"
    pause 2.0
    
    # Show restart menu
    menu:
        "What would you like to do?"
        
        "Restart the game":
            jump start
            
        "Quit":
            return
