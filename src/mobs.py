from typing import List, Optional, Literal
from operator import itemgetter
import sqlite3
import time
import src.database as database
import pandas as pd

FIND_MOB_QUERY = """
SELECT * FROM mobs
INNER JOIN locale_en ON locale_en.id == mobs.name
WHERE locale_en.data == ? COLLATE NOCASE
"""

FIND_SPECIFIC_DISPLAY_QUERY = """
SELECT locale_en.data FROM mobs
INNER JOIN locale_en ON locale_en.id == mobs.name
WHERE mobs.id == ?
"""

class Mobs:
    def __init__(self):
        self.db = sqlite3.connect("databases/everything.db")
        self.id_list = None
        self.mobBlacklist = []
        self.schoolList = ['Fire', 'Ice', 'Storm', 'Balance', 'Life', 'Myth', 'Death', 'Shadow', 'Moon']
        self.universalstats= ['Damage','Accuracy','Pierce','Resist','Crit Rating','Block Rating', 'Pip Conversion Rating']

    def fetch_mob(self, name: str) -> List[tuple]:
        return self.db.execute(FIND_MOB_QUERY, (name,)).fetchall()

    def sum_stats(self, existing_stats: dict, equipped_items: List[int]):
        processed_item_ids = set()

        for item_id in equipped_items:
            if item_id in processed_item_ids:
                continue

            processed_item_ids.add(item_id)
            itemStats = self.fetch_mob_item_attributes(item_id)

            for stat in itemStats:
                if stat in existing_stats:
                    existing_stats[stat] += itemStats[stat]
                else:
                    existing_stats[stat] = itemStats[stat]
        return existing_stats

    def fetch_mob_item_attributes(self, item: int) -> List[str]:
        attributes = {}
        cursor = self.db.execute("SELECT * FROM item_stats WHERE item == ?", (item,)).fetchall()
        
        for stat in cursor:
            a = stat[3]
            b = stat[4]

            match stat[2]:
                # Regular stat
                case 1:
                    stat = database.translate_stat(a)
                    rounded_value = int(round(b, 2))
                    attributes[stat] = rounded_value

                # Starting pips
                case 2:
                    if a != 0:
                        attributes['Pips'] =  int(a)
                    if b != 0:
                        attributes['Power Pips'] =  int(b)

        return attributes

    def fetch_mob_items(self, mob: int) -> List[str]:
        items = []
        cursor = self.db.execute("SELECT * FROM mob_items WHERE mob == ?", (mob,))
        for row in cursor:
            items.append(row[2])
        return items

    def fetch_mob_attributes(self, mob: int) -> List[str]:
        
        attributes = {}
        
        row = self.db.execute("SELECT * FROM mobs WHERE id == ?", (mob,)).fetchone()

        #attributes['Item'] = item
        #attributes["ID"] = row[0]
        attributes["Name"] = row[2].decode("utf-8")
        if any([x in row[2].decode() for x in self.mobBlacklist]):
            return {}
        attributes['Display'] = self.db.execute(FIND_SPECIFIC_DISPLAY_QUERY, (mob,)).fetchone()[0] #2
        #if '\\n' in attributes['Display']:
        #    attributes['Display'] = attributes['Display'].replace('\\n',' ')
        #attributes["image_file"] = row[3].decode("utf-8")
        #attributes["Title"] = row[4]
        #attributes["Rank"] = row[5]
        attributes["Health"] = row[6]
        attributes["School"] = database.translate_equip_school(row[7])
        if row[8] not in [0,1] :
            attributes["Secondary School"] = database.translate_equip_school(row[8])
        attributes["Max Shadow Pips"] = row[9]
        #attributes["Cheats"] = row[10]
        #attributes["Intelligence"] = row[11]
        #attributes["Selfishness"] = row[12]
        #attributes["Aggressiveness"] = row[13]
        #attributes["Monstro"] = database.MonstrologyKind(row[14])
        #attributes["Mob Name"] = row[16]
        
        cursor = self.db.execute("SELECT * FROM mob_stats WHERE mob == ?", (mob,)).fetchall()
        
        for stat in cursor:
            a = stat[3]
            b = stat[4]

            match stat[2]:
                # Regular stat
                case 1:
                    stat = database.translate_stat(a)
                    rounded_value = int(round(b, 2))
                    attributes[stat] = rounded_value

                # Starting pips
                case 2:
                    if a != 0:
                        attributes['Pips'] =  int(a)
                    if b != 0:
                        attributes['Power Pips'] =  int(b)
        
        items = self.fetch_mob_items(mob)
        #print(f'ITEMS HERE: {items}')
        attributes = self.sum_stats(attributes, items)
        return attributes
    
    def generateMobs(self):
        start = time.time()
        cursor = self.db.execute("SELECT id FROM mobs")
        allIDs = cursor.fetchall()
        self.id_list = []
        for i in allIDs:
            self.id_list.append(i[0])
        
        importantIDs = []
        for id in self.id_list:
            attributes = self.fetch_mob_attributes(id)
            if attributes != {}:
                importantIDs.append(attributes)
            #else:
            #    print(id)
        
        table = pd.DataFrame.from_dict(importantIDs)
        table['Secondary School'] = table['Secondary School'].fillna('None')
        table.fillna(0,inplace=True)

        for stat in self.universalstats:
            for school in self.schoolList:
                columntitle= school + " " +stat
                if columntitle in table.columns:
                    table[columntitle]+=table[stat]

        table.to_pickle('data/allthemobs.pkl')
        table.to_csv("data/allthemobs.csv",index=False)

        end = time.time()
        print(end-start)

        self.db.close()
        return table