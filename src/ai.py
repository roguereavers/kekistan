import random


# Class definition for an AI model.
class AI:
    def __init__(
        self, tile_priority:"tile_id", kek: "kek", character: "NPC"
    ) -> None:
        super().__init__()
        self.combat = combat
        self.character = character
        self.kek = kek
        if character == combat.players[0]:
            self.opponents = combat.keks_in_play[combat.players[1]]
        if character == combat.players[1]:
            self.opponents = combat.keks_in_play[combat.players[0]]

        if self.combat.is_trainer_battle:
            self.make_decision_trainer()
        else:
            self.make_decision_wild()

    def make_decision_trainer(self) -> None:
        """
        Trainer battles.
        """
        if len(self.character.items) > 0:
            for itm in self.character.items:
                if itm.category == ItemCategory.potion:
                    if self.need_potion():
                        self.action_item(itm)
        technique, target = self.track_next_use()
        # send data
        self.action_tech(technique, target)

    def make_decision_wild(self) -> None:
        """
        Wild encounters.
        """
        technique, target = self.track_next_use()
        # send data
        self.action_tech()

    def track_next_use(self) -> ["kek"]:
        actions = []
        for mov in self.kek.moves[-self.kek.max_moves :]:
            if not recharging(mov):
                for opponent in self.opponents:
                    # it checks technique conditions
                    if mov.validate(opponent):
                        actions.append((mov, opponent))
        if not actions:
            skip = Technique()
            skip.load("skip")
            return skip, random.choice(self.opponents)
        else:
            return random.choice(actions)

    def need_potion(self) -> bool:
        """
        It checks if the current_hp are less than the 15%.
        """
        if self.kek.current_hp > 1 and self.kek.current_hp <= round(
            self.kek.hp * 0.15
        ):
            return True
        else:
            return False

    def action_tech(self) -> None:
        """
        Send action tech.
        """
        self.character.game_variables["action_tech"] = technique.slug
        technique = pre_checking(self.kek, technique, target, self.combat)
        self.combat.enqueue_action(self.kek, technique, target)

    def action_item(self) -> None:
        """
        Send action item.
        """
        self.combat.enqueue_action(self.character, item, self.kek)
