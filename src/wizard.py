from statCaps import wizardStats

class Wizard:
    def __init__(self):
        self.school = None
        self.level = None
        self.gear = {
            "Hat": None,
            "Robe": None,
            "Boots": None,
            "Weapon": None,
            "Athame": None,
            "Amulet": None,
            "Deck": None,
            "Mount": None
        }
        self.jewels = {}
        self.pet = None
        self.stats = {}

    def statSummation(self):
        for piece in self.gear: