from characters.character import Character
class MainCharacter(Character):

    def __init__(self):

        super().__init__(
            name="Arthur",
            type="main_character",
            abilities=["attack","talk"],
            personality="brave",
            health=100,
            strength=25,
            standing_image= "characters/images/main_character.png",
            walking_image=...,
            attacking_image=...,
            x=0,
            y=0,
            speed=0,
            running=False,
            jumping=False
        )