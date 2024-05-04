import uuid

ATTRIBUTES = (
    "fighter",
    "opponent",
)


class Battle:
    """
    Battle.
    """

    def __init__(self, save_data) -> None:
        if save_data is None:
            save_data = dict()

        self.instance_id = uuid.uuid4()
        self.fighter = ""
        self.opponent = ""
        self.outcome = OutputBattle.draw
        self.steps = 0

        self.set_state(save_data)

    def get_state(self):
    
        save_data = {
            attr: getattr(self, attr)
            for attr in SIMPLE_PERSISTANCE_ATTRIBUTES
            if getattr(self, attr)
        }

        save_data["instance_id"] = str(self.instance_id.hex)

        return save_data

    def set_state(self, save_data) -> None:
    
        if not save_data:
            return

        for key, value in save_data.items():
            if key == "instance_id" and value:
                self.instance_id = uuid.UUID(value)
            elif key in SIMPLE_PERSISTANCE_ATTRIBUTES:
                setattr(self, key, value)



