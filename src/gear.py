import time
from typing import List, Optional, Literal
from operator import itemgetter
import sqlite3

from loguru import logger

import src.database as database

import pandas as pd
import numpy as np

FIND_ITEM_QUERY = """
SELECT * FROM items
INNER JOIN locale_en ON locale_en.id == items.name
WHERE locale_en.data == ? COLLATE NOCASE
"""

FIND_SET_QUERY = """
SELECT * FROM set_bonuses
"""

SET_BONUS_NAME_QUERY = """
SELECT locale_en.data FROM set_bonuses
INNER JOIN locale_en ON locale_en.id == set_bonuses.name
WHERE set_bonuses.id == ?
"""

SPELL_NAME_ID_QUERY = """
SELECT locale_en.data FROM spells
INNER JOIN locale_en ON locale_en.id == spells.name
WHERE spells.template_id == ?
"""
FIND_ITEM_NAME_QUERY = """
SELECT locale_en.data FROM items
INNER JOIN locale_en ON locale_en.id == items.name
"""

DISPLAY_NAME_QUERY = """
SELECT locale_en.data FROM items
INNER JOIN locale_en ON locale_en.id == items.name
WHERE items.id == ?
"""

COMBINATION_QUERY = """ CREATE TABLE combination AS 
SELECT * FROM items, locale_en, item_stats
WHERE items.id == item_stats.item AND items.name == locale_en.id
ORDER BY items.id
"""
REFINED_COMBINATION_QUERY = """CREATE TABLE refinedcombination AS 
SELECT items.id,name,real_name,bonus_set,jewels,items.kind,extra_flags,equip_school,
equip_level,min_pet_level,max_spells,max_copies,max_school_copies,deck_school,
max_tcs,data,a,b FROM items, locale_en, item_stats
WHERE items.id == item_stats.item AND items.name == locale_en.id
ORDER BY items.id
"""

SET_BONUS_TABLE_QUERY = """ 
SELECT locale_en.data as "Set", set_stats.activate_count as "Pieces", set_stats.kind, set_stats.a, set_stats.b FROM set_bonuses, set_stats, locale_en 
WHERE set_bonuses.id == set_stats.bonus_set AND set_bonuses.name == locale_en.id
ORDER BY set_bonuses.id
"""

CLEANUPQUERIES = ["ALTER TABLE refinedcombination DROP COLUMN name", 
                  "ALTER TABLE refinedcombination RENAME COLUMN data to display"]

class Gear:
    def __init__(self):
        self.db = sqlite3.connect("databases/playerGear.db")
        self.id_list = None
        self.gearBlacklist = ['NV_Polymorph_Stats_Ring','Test','DONOTUSE', 'MinionDeck', 'GR_AZ_Parasaur_', 'BR_CL_Polymorph']
        self.setBonusBlacklist = ['Display Name']
        self.schoolList = ['Fire', 'Ice', 'Storm', 'Balance', 'Life', 'Myth', 'Death', 'Shadow', 'Moon']
        self.universalstats= ['Damage','Accuracy','Pierce','Resist','Crit Rating','Block Rating', 'Pip Conversion Rating']

    def changeDB(self,db):
        self.db.close()
        self.db = sqlite3.connect(db)

    def fetch_item(self, name: str) -> List[tuple]:
        cursor = self.db.execute(FIND_ITEM_QUERY, (name,)) 
        return cursor.fetchall()
        
    def fetch_set_bonus_name(self, set_id: int) -> Optional[tuple]:
        if set_id == 0:
            return None
        else:
            cursor = self.db.execute(SET_BONUS_NAME_QUERY, (set_id,)) 
            return (cursor.fetchone())[0]
    
    def fetch_item_attributes(self, item: int) -> List[str]:
        attributes = {}
        
        row = self.db.execute("SELECT * FROM items WHERE id == ?", (item,)).fetchone()
        #attributes['ID'] = item

        # gearBlacklisted pieces removed
        attributes['Name'] = row[2].decode() #1
        if any([x in row[2].decode() for x in self.gearBlacklist]):
            return {}
        
        attributes['Display'] = self.db.execute(DISPLAY_NAME_QUERY, (item,)).fetchone()[0] #2
        if '\\n' in attributes['Display']:
            attributes['Display'] = attributes['Display'].replace('\\n',' ')
        
        attributes['Set'] =  self.fetch_set_bonus_name(row[3]) #3
        #attributes['Rarity'] = database.translate_rarity(row[4])
        attributes['Jewels'] = database.format_sockets(row[5]) #4
        attributes['Kind'] = database.get_item_str(database.ItemKind(row[6])) #5

        # Remove none permanent mounts
        if attributes['Kind'] == "Mount" and " day)" in attributes['Display'].lower():
            return {}
        
        attributes['Extra Flags'] = database.translate_flags(database.ExtraFlags(row[7])) #6
        attributes['School'] = database.translate_equip_school(row[8]) #7
        attributes['Level'] = row[9] #8

        attributes['Max Spells'] = row[11] #9
        attributes['Max Copies'] = row[12] #10
        attributes['Max School Copies'] = row[13] #11
        attributes['Deck School'] = database.translate_equip_school(row[14]) #12
        attributes['Max Treasure Cards'] = row[15] #13

        # removes obvious mob decks
        if attributes['Max Copies'] > 64 or attributes['Max School Copies'] > 10 or attributes['Max Treasure Cards'] > 64:
             return {}
        
        attributes['Cards'] = [] #14
        attributes['Maycasts'] = [] #15

        cursor = self.db.execute("SELECT * FROM item_stats WHERE item == ?", (item,)).fetchall()
        
        for stat in cursor:
            a = stat[3]
            b = stat[4]

            match stat[2]:
                # Regular stat
                case 1:
                    stat = database.translate_stat(a)
                    rounded_value = int(round(b, 2))

                    # Pieces with negative stats are impossible in normal circumstances, remove them like this
                    if rounded_value > 0:
                        attributes[stat] = rounded_value
                    else:
                        return {}

                # Starting pips
                case 2:
                    if a != 0:
                        attributes['Pips'] =  int(a)
                    if b != 0:
                        attributes['Power Pips'] =  int(b)
                
                # Itemcards
                case 3:
                    cursor = self.db.execute(SPELL_NAME_ID_QUERY, (a,)) 
                    card_name = (cursor.fetchone())[0]

                    copies = b

                    for i in range (0,copies):
                        attributes["Cards"].append(card_name)
                
                # Maycasts
                case 4:
                    cursor = self.db.execute(SPELL_NAME_ID_QUERY, (a,)) 
                    card_name = (cursor.fetchone())[0]
                    attributes["Maycasts"].append(card_name)

            #If item has no stats, no cards, no set bonus, not a deck and no jewel slots, it is redundant
        if (len(attributes) <= 15 and attributes['Set'] is None and attributes['Kind'] != "Deck" and 
        attributes['Jewels'] == [] and attributes['Cards'] == [] and attributes ['Maycasts'] == []):
            return {}
        else:
            attributes['Jewels'] = '|'.join(sorted(attributes['Jewels']))
            attributes['Extra Flags'] = '|'.join(sorted(attributes['Extra Flags']))
            attributes['Cards'] = '|'.join(sorted(attributes['Cards']))
            attributes['Maycasts'] = '|'.join(sorted(attributes['Maycasts']))
            return attributes
    
    def generateGear(self):

        start = time.time()
        cursor = self.db.execute("SELECT id FROM items where items.kind != 256")
        #cursor = self.db.execute("SELECT id FROM items")
        allIDs = cursor.fetchall()
        self.id_list = []
        for i in allIDs:
            self.id_list.append(i[0])
        
        importantIDs = []
        for id in self.id_list:
            attributes = self.fetch_item_attributes(id)
            if attributes != {}:
                importantIDs.append(attributes)
            #else:
            #    print(id)
        
        table = pd.DataFrame.from_dict(importantIDs)
        table['Set'] = table['Set'].fillna('None')
        table['Jewels'] = table['Jewels'].fillna('None')
        table['Extra Flags'] = table['Extra Flags'].fillna('None')
        table.fillna(0,inplace=True)

        for stat in self.universalstats:
            for school in self.schoolList:
                columntitle= school + " " +stat
                if columntitle in table.columns:
                    table[columntitle]+=table[stat]

        table.to_pickle('data/allthegear.pkl')
        table.to_csv("data/allthegear.csv",index=False)

        end = time.time()
        print(end-start)

        return table

    def generateAllSets(self):
        start = time.time()
        table = pd.read_sql_query(SET_BONUS_TABLE_QUERY, self.db)
        table['Cards'] = [[] for x in range(len(table))]
        table['Maycasts'] = [[] for x in range(len(table))]

        for term in self.setBonusBlacklist:
            table = table[table['Set'] != term]
        table.reset_index(inplace=True)

        for i in table.index:
            a = table.at[i,'a'].item()
            b = table.at[i,'b'].item()
            match table.at[i,'kind']:
                # Regular stat
                case 1:
                    if "Flat" in database.translate_stat(a):
                        continue
                    table.at[i,database.translate_stat(a)] = round(b, 2)

                # Starting pips
                case 2:
                    if a != 0:
                        table.at[i,'Pips'] =  int(a)
                    if b != 0:
                        table.at[i,'Power Pips'] =  int(b)
                
                # Itemcards
                case 3:
                    cursor = self.db.execute(SPELL_NAME_ID_QUERY, (a,)) 
                    card_name = (cursor.fetchone())[0]

                    copies = b

                    for n in range (0,copies):
                        table.at[i,"Cards"].append(card_name)
                    table.at[i,'Cards'] = '|'.join(sorted(table.at[i,'Cards']))
                
                # Maycasts
                case 4:
                    cursor = self.db.execute(SPELL_NAME_ID_QUERY, (a,)) 
                    card_name = (cursor.fetchone())[0]
                    table.at[i,"Maycasts"].append(card_name)
                    table.at[i,'Maycasts'] = '|'.join(sorted(table.at[i,'Cards']))
                
                case _:
                    table.drop(i,inplace=True)
                
        table.drop(columns=['index','a','b','kind'],inplace=True)
        table.fillna(0,inplace=True)
        #table = table[table.astype(str)['Cards'] != '[]']

        for stat in self.universalstats:
            for school in self.schoolList:
                columntitle= school + " " +stat
                if columntitle in table.columns:
                    table[columntitle]+=table[stat]

        table.to_pickle('data/allthesets.pkl')
        table.to_csv("data/allthesets.csv",index=False)

        end = time.time()
        print(end-start)
        return table