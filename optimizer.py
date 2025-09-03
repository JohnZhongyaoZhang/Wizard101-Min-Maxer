from pandas import Series
from pandas import DataFrame
import numpy as np
import pandas as pd

from src.gear import Gear
from src.mobs import Mobs

import src.database as database
import os

import time

class Optimizer:
    def __init__(self):
        self.level = 170
        self.levellowerbound = 170
        self.school = "Storm"
        self.target = "PvP"
        #self.spells = []

        self.deckaDeckAllowed = False
        self.PvPOnlyAllowed = False
        self.universalGearAllowed = False

        #self.kindsconsidered = ["Hat", "Robe", "Shoes", "Weapon", "Athame", "Amulet", "Ring", "Deck", "Mount"]
        self.kindsconsidered = ["Hat", "Robe", "Shoes", "Weapon", "Athame", "Amulet", "Ring", "Deck"]

        self.gearTable = None
        self.setTable = None
        self.mobTable = None

        self.generateTables()

    def generateTables(self):
        GeneratorClass = Gear()
        MobClass = Mobs()
        if os.path.exists('data/allthegear.pkl'):
            self.gearTable = pd.read_pickle('data/allthegear.pkl')
        else:
            print("Gear table not found, creating gear table")
            self.gearTable = GeneratorClass.generateGear()

        if os.path.exists('data/allthesets.pkl'):
            self.setTable = pd.read_pickle('data/allthesets.pkl')
        else:
            print("Set bonus table not found, creating set bonus table")
            self.setTable = GeneratorClass.generateAllSets()
        
        if os.path.exists('data/allthemobs.pkl'):
            self.mobTable = pd.read_pickle('data/allthemobs.pkl')
        else:
            print("Mob table not found, creating mob table")
            self.mobTable = MobClass.generateMobs()
            
        tables = self.restrictTableToInputtedParameters()
        self.gearTable = tables[0]
        self.setTable = tables[1]
        for col in self.gearTable.columns.difference(self.setTable.columns):
            self.setTable[col] = 0

    def restrictTableToInputtedParameters(self):
        masterystring = f"All schools except {self.school}"
        filteredGearTable = self.gearTable[~(self.gearTable["School"] == masterystring)]
        if self.universalGearAllowed:
            filteredGearTable = filteredGearTable[(filteredGearTable["School"] == self.school) | (filteredGearTable["School"] == "Universal")]
        else:
            filteredGearTable = filteredGearTable[filteredGearTable["School"] == self.school]
        filteredGearTable = filteredGearTable[(filteredGearTable["Level"] <= self.level)]
        filteredGearTable = filteredGearTable[(filteredGearTable["Level"] >= self.levellowerbound)]
        
        if self.deckaDeckAllowed == False:
            filteredGearTable = filteredGearTable[~((filteredGearTable['Kind'] == "Deck") & (filteredGearTable["Max Spells"] == 0))]
        if self.PvPOnlyAllowed == False:
            filteredGearTable = filteredGearTable[~(filteredGearTable["-100% Max Mana"] != 0)]
        filteredSetTable = self.setTable
        #if self.target in filteredGearTable.columns.tolist() and self.target not in self.setTable.columns.tolist():
        #    filteredSetTable[self.target] = 0
        return filteredGearTable, filteredSetTable

    def maximizeOneStat(self):
        print(f"{self.school} school")
        print(f"Level {self.level}")
        print(f"Optimizing {self.target}")
        print("Note: sets not fully implemented, manual arithmetic done to get true optimal setup")
        total = 0

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
        return self.gearTable.drop_duplicates(subset=requiredtraits, keep="first")

    def getNeededStats(self):
        savedStats = []
        if "PvP" in self.target:
            effectiveDamage = [self.school + " " + 'Damage', self.school + " " + 'Pierce', self.school + " " + 'Crit Rating']
            effectiveHealth = ['Health', 'Resist', 'Block Rating']
            utilities = [self.school+" Pip Conversion Rating", self.school+" Accuracy", "Power Pip Chance", "Shadow Pip Stat Rating"]
            savedStats = effectiveDamage + effectiveHealth + utilities
        elif "Effective Damage" in self.target:
            if self.school != "Universal":
                savedStats = [self.school + " " + 'Damage', self.school + " " + 'Pierce', self.school + " " + 'Crit Rating']
            else:
                savedStats = ['Damage', 'Pierce', 'Crit Rating']
        elif self.target == "Effective Health":
            savedStats = ['Health', 'Resist', 'Block Rating']
        else:
            savedStats = [self.target]
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
    
    # Deprecating this method temporarily because it's harder to implement than I thought it would
    def removeSuboptimalItems(self):
        savedStats = self.getNeededStats()
        newFrame = pd.DataFrame()
        for itemtype in self.kindsconsidered:
            for stat in savedStats:
                considered = self.gearTable[(self.gearTable["Kind"] == itemtype)].copy(deep=True)
                if len(considered) == 0:
                    print(f"Any {itemtype} 0.0")
                else:
                    max_row_index = considered[stat].idxmax()
                    max_row = considered.loc[max_row_index]
                    if max_row[stat] == 0:
                        print(f"Any {itemtype} 0.0")
                    else:
                        # FIX THIS METHOD
                        print("Piece:  " +itemtype+ " Stat: " +str(stat)+ " Shape: " +str(considered.shape))
                        otherStats = [s for s in savedStats if s != stat]
                        condition = (considered[savedStats] >= max_row[savedStats]).all(axis=1)
                        useful = considered[condition]
                        print("Piece: " +itemtype+ " Stat: " +str(stat)+ " Shape: " +str(useful.shape))
                        print(useful)
                        newFrame = pd.concat([newFrame,useful])
        return newFrame
    
    def removeSuboptimalItems2(self):
        prunecount = 0
        savedStats = self.getNeededStats()
        optimalItems = pd.DataFrame(columns=self.gearTable.columns)
        gearTableLevelSorted = self.gearTable.sort_values(by='Level', ascending=False)

        for contendingItemIndex, contendingItem in gearTableLevelSorted.iterrows():
            optimal = True
            for optimalItemIndex, optimalItem in optimalItems[optimalItems['Kind'] == contendingItem['Kind']].iterrows():
                for stat in savedStats:
                    if optimalItem[stat] > contendingItem[stat]:
                        optimal = False
                        break

            if optimal:
                pruned = True
                for potentiallySuboptimalItemIndex, potentiallySuboptimalItem in optimalItems[optimalItems['Kind'] == contendingItem['Kind']].iterrows():
                    for stat in savedStats:
                        if contendingItem[stat] < potentiallySuboptimalItem[stat]:
                            pruned = False
                            break
                    if pruned:
                        optimalItems.drop(potentiallySuboptimalItemIndex, inplace=True)
                        prunecount+=1
                optimalItems.loc[contendingItemIndex] = contendingItem
        
        print(prunecount)
        print(optimalItems)

        return optimalItems
                
                

    # This is a hardcoded method to prune setups involving pieces with jewel combinations that are so bad that they couldn't possibly be part of an optimal PvP setup
    # Turn this method off if the focus is not looking for a setup that can trade hits
    def removeBadSockets(self):
        tempTable = self.gearTable.copy(deep=True)
        usefulJewels = ['Square', "Circle", "Triangle"]
        socketedPieces = ['Athame', 'Ring', 'Amulet', 'Deck']

        def countUsefulJewels(jewelString):
            if type(jewelString) != str:
                return 0
            jewels = jewelString.split('|')
            return sum(jewels.count(jewel) for jewel in usefulJewels)
        
        athameMask = (tempTable['Kind'] == "Athame") & (tempTable['Jewels'].apply(countUsefulJewels) >= 3)
        ringMask = (tempTable['Kind'] == "Ring") & (tempTable['Jewels'].apply(countUsefulJewels) >= 2)
        amuletMask = (tempTable['Kind'] == "Amulet") & (tempTable['Jewels'].apply(countUsefulJewels) >= 2)
        deckMask = (tempTable['Kind'] == "Deck") & (tempTable['Jewels'].apply(countUsefulJewels) >= 1)

        finalMask = athameMask | ringMask | amuletMask | deckMask
        tempTable = tempTable[finalMask | (~tempTable['Kind'].isin(socketedPieces))]

        return tempTable

    # This is a hardcoded method to prune setups involving pieces without optimal shad rating
    # Turn this method off if the focus is not looking for a setup with high shad rating
    def getShadPieces(self):
        mainPieces = ["Hat", "Robe", "Shoes", "Weapon"]
        tempTable = self.gearTable.copy(deep=True)
        finalMask = pd.Series(False, index=tempTable.index)

        for piece in mainPieces:
            pieceMask = (tempTable['Kind'] == piece) & (tempTable['Shadow Pip Stat Rating'] > 0)
            finalMask |= pieceMask

        tempTable = tempTable[finalMask | (~tempTable['Kind'].isin(mainPieces))]

        return tempTable
    
    # This is a hardcoded method to remove suboptimal from the gear pool at level 160 and 170
    def getTopTierPieces(self):
        tempTable = self.gearTable.copy(deep=True)
        
        #tempTable = tempTable[tempTable['School'] != "Universal"]
        tempTable = tempTable[tempTable['Extra Flags'].str.contains("No Auction")]
        tempTable = tempTable[~tempTable['Display'].str.contains("Masterpiece")]
        tempTable = tempTable[~tempTable['Display'].str.contains("City Dweller")]
        tempTable = tempTable[~tempTable['Display'].str.contains("Enforcer")]
        tempTable = tempTable[~tempTable['Display'].str.contains("Warper")]
        tempTable = tempTable[~tempTable['Display'].str.contains("Manifest")]
        return tempTable

    def combinationCreator(self):
        alltheitems = []
        for kind in self.kindsconsidered:
            considered = self.gearTable[(self.gearTable["Kind"] == kind)]
            names = considered["Name"].tolist()
            if not names:
                names.append("No " +kind)
            alltheitems.append(names)
        index = pd.MultiIndex.from_product(alltheitems, names = self.kindsconsidered)
        index = index.drop_duplicates()
        combos = index.to_frame()
        print(combos)
        return combos

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
    #TheOptimizer.maximizeOneStat()

    TheOptimizer.gearTable = TheOptimizer.removeUselessItems()
    TheOptimizer.gearTable = TheOptimizer.getAllUniqueItems()
    TheOptimizer.gearTable = TheOptimizer.removeBadSockets()
    TheOptimizer.gearTable = TheOptimizer.getShadPieces()
    TheOptimizer.gearTable = TheOptimizer.getTopTierPieces()

    #TheOptimizer.gearTable = TheOptimizer.removeSuboptimalItems2()
    #TheOptimizer.maximizeOneStat()
    
    TheOptimizer.combinationChecker()

    print(TheOptimizer.gearTable)
    quit()

main()