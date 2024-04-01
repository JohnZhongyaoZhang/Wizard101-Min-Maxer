from pandas import Series
from pandas import DataFrame
import numpy as np
import pandas as pd

from gear import Gear
from mobs import Mobs

import database
import os

class Optimizer:
    def __init__(self):
        self.level = 170
        self.school = "Life"
        self.target = "Outgoing Healing"
        self.dualschooling = False
        #self.spells = []
        self.deckathalon = True
        self.kindsconsidered = ["Hat", "Robe", "Shoes", "Weapon", "Athame", "Amulet", "Ring", "Deck", "Mount"]
        self.schoolList = ['Fire', 'Ice', 'Storm', 'Balance', 'Life', 'Myth', 'Death', 'Shadow', 'Moon']
        self.universalstats= ['Damage','Accuracy','Pierce','Resist','Crit Rating','Block Rating', 'Pip Conversion Rating']
        self.baseaccuracy = dict(zip(self.schoolList, [70,75,65,80,85,75,80,100,100]))
        #self.thresholds = {"Power Pip Chance": 100, "Myth Accuracy": 100 - self.baseaccuracy['Myth']}
        self.thresholds = {}
        self.gearTable = None
        self.setTable = None
        self.mobTable = None

    def generateTables(self):
        GeneratorClass = Gear()
        MobClass = Mobs()
        if os.path.exists('data/allthegear.pkl'):
            self.gearTable = pd.read_pickle('data/allthegear.pkl')
        else:
            print("WHAT 1")
            self.gearTable = GeneratorClass.generateGear()

        if os.path.exists('data/allthesets.pkl'):
            self.setTable = pd.read_pickle('data/allthesets.pkl')
        else:
            print("WHAT 2")
            self.setTable = GeneratorClass.generateAllSets()
        
        if os.path.exists('data/allthemobs.pkl'):
            self.mobTable = pd.read_pickle('data/allthemobs.pkl')
        else:
            print("WHAT 3")
            #self.mobTable = MobClass.generateMobs()
        
        tables = self.restrictTableToInputtedParameters()
        self.gearTable = tables[0]
        self.setTable = tables[1]

    def restrictTableToInputtedParameters(self):
        masterystring = f"All schools except {self.school}"
        filteredGearTable = self.gearTable[~(self.gearTable["School"] == masterystring)]
        filteredGearTable = filteredGearTable[(filteredGearTable["School"] == self.school) | (filteredGearTable["School"] == "Universal")]
        filteredGearTable = filteredGearTable[(filteredGearTable["Level"] <= self.level)]
        if self.deckathalon == False:
            filteredGearTable = filteredGearTable[~((filteredGearTable['Kind'] == "Deck") & (filteredGearTable["Max Spells"] == 0))]
        filteredSetTable = self.setTable
        if self.target in filteredGearTable.columns.tolist() and self.target not in self.setTable.columns.tolist():
            filteredSetTable[self.target] = 0
        return filteredGearTable, filteredSetTable 

    def maximizeOneStat(self):
        print(f"{self.school} school")
        print(f"Level {self.level}")
        print(f"Optimizing {self.target}")
        print("Note: sets not fully implemented, manual arithmetic done to get true optimal setup")
        total = 0

        #print(self.gearTable[self.gearTable['Kind'] == "Mount"])

        for itemtype in self.kindsconsidered:
            considered = self.gearTable[(self.gearTable["Kind"] == itemtype)]
            if len(considered) == 0:
                print(f"Any {itemtype} 0.0")
            else:
                considered = considered.sort_values(by=[self.target], ascending=False).reset_index()
                considered = considered[considered[self.target] == considered.at[0,self.target]]
                if considered.at[0,self.target] == 0:
                    print(f'No {itemtype} offers any contribution to {self.target}')
                else:
                    print(considered[['Name','Display','Kind','Level',self.target]])
                total+=considered.at[0,self.target]
        print(total)
        return total
    
    def getAllUniqueItems(self):
        irrelevanttraits = ['Name','Display','Extra Flags','Cards','Maycasts']
        alltraits = self.gearTable.columns
        requiredtraits = [i for i in alltraits if i not in irrelevanttraits]
        newTable = self.gearTable.copy(deep=True)

        newTable.drop_duplicates(subset=requiredtraits, inplace=True, keep='first')
        return newTable

    def getNeededStats(self):
        savedStats = []
        if  "Effective Damage" in self.target:
            if self.school != "Universal":
                savedStats = [self.school + " " + 'Damage', self.school + " " + 'Pierce', self.school + " " + 'Crit Rating']
            else:
                savedStats = ['Damage', 'Pierce', 'Crit Rating']
        elif self.target == "Effective Health":
            savedStats = ['Health', 'Resist', 'Block Rating']
        else:
            savedStats = [self.target]
        if len(self.thresholds) > 0:
            savedStats.extend(list(self.thresholds.keys()))
        
        return savedStats

    def removeUselessItems(self):
        savedStats = self.getNeededStats()

        optimalGearTable = self.gearTable[(self.gearTable[savedStats] != 0).any(axis=1) | (self.gearTable['Set'] != 'None')]
        equippableSets = optimalGearTable['Set'].unique().tolist()
        equippableSets.remove("None")

        for setName in optimalGearTable['Set'].unique().tolist():
            setGroup = self.setTable[self.setTable['Set'] == setName]
            setGroup = setGroup[(setGroup[savedStats] != 0).any(axis=1)]

            # If a wizard has access to a benefiting set but cannot equip enough pieces to get the bonus, remove pieces with no useful stats in that set
            if len(setGroup) >  0 and len(optimalGearTable[optimalGearTable['Set'] == setName]['Kind'].unique().tolist()) < setGroup['Pieces'].min():
                optimalGearTable = optimalGearTable[~(optimalGearTable[savedStats] == 0).all(axis=1) | (optimalGearTable['Set'] != setName)]
            # If the set doesn't offer any benefit, remove pieces with no useful stats in that set
            elif len(setGroup) == 0:
                optimalGearTable = optimalGearTable[~(optimalGearTable[savedStats] == 0).all(axis=1) | (optimalGearTable['Set'] != setName)]

        # Only keep pieces that can be part of the optimal solution
        return optimalGearTable
    
    def removeSuboptimalItems(self):
        savedStats = self.getNeededStats()
        for itemtype in self.kindsconsidered:
            for stat in savedStats:
                considered = self.gearTable[(self.gearTable["Kind"] == itemtype)]
                if len(considered) == 0:
                    print(f"Any {itemtype} 0.0")
                else:
                    max_row_index = considered[stat].idxmax()
                    max_row = considered.loc[max_row_index]
                    if max_row[stat] == 0:
                        print(f"Any {itemtype} 0.0")
                    else:
                        print(max_row[['Name','Display','Kind','Level',stat]])
                        mask = (considered[savedStats] <= max_row[savedStats]).all(axis=1)
                        copeOutput = considered[~mask]
                        print(copeOutput)

    def combinationChecker(self):
        itemsByKind = []
        print(f"Number of Items: {len(self.gearTable)}")

        for itemtype in self.kindsconsidered:
            considered = self.gearTable[(self.gearTable["Kind"] == itemtype)]
            names = considered["Name"].tolist()
            itemsByKind.append(names)
        total = 1
        for i in range(len(itemsByKind)):
            print(f"Number of {self.kindsconsidered[i]}: {len(itemsByKind[i])}")
            total*=max(len(itemsByKind[i]),1)
        print(f"Number of combinations: {total}")
        
def main():
    TheOptimizer = Optimizer()
    TheOptimizer.generateTables()
    
    #TheOptimizer.gearTable = TheOptimizer.removeUselessItems()
    
    #TheOptimizer.gearTable = TheOptimizer.removeSuboptimalItems()

    TheOptimizer.maximizeOneStat()
    quit()
main()