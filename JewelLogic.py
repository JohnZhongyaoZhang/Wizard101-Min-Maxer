# This class will serve as a rough draft for how jewels will be handled in the main optimizer class
# Because the amount of jewels in the game are relatively low. They can be hardcoded

class JewelLogic():
    def __init__(self):
        self.trianglespecificaccuracy = {15: 2, 25: 3, 35: 4, 45: 5, 55: 6, 65: 7, 75: 8, 85: 9, 95: 10, 105: 11, 115: 12, 125: 13, 135: 14, 145: 15, 155: 16}
        self.trianglepowerpip = {25: 2, 35: 3, 45: 4, 55: 5, 65: 6, 75: 7, 85: 8, 95: 9, 105: 10}
        self.triangleuniversalaccuracy = {15: 1, 35: 2, 55: 3, 75: 4, 95: 5, 115: 6, 135: 7}
        self.squarehealth = {170: {"Storm": 525, "Fire": 595, "Ice": 735, "Balance": 670, "Myth": 595, "Death": 650, "Life": 775}}
        self.circlepierce = {55: 2, 65: 3, 75: 4, 85: 5, 95: 6}
        self.circledamage = {170: {"Storm": 11, "Fire": 10, "Ice": 9, "Balance": 10, "Myth": 10, "Death": 11, "Life": 9}}
        self.tearhealth = {15: 15, 25: 25, 35: 35, 45: 45, 55: 55, 65: 65, 75: 75, 85: 85, 95: 95, 105: 105, 115: 115, 125: 125, 135: 135, 145: 145, 155: 155}
        for level in range(15,156,10):
            self.health[level] = level

def main():
    TheJewelLogic = JewelLogic()
    print(TheJewelLogic.health)

main()