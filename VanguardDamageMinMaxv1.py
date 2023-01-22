from pandas import Series
from pandas import DataFrame
import numpy as np
import pandas as pd

#User defined constants
pvp = True
reinforce=True

def damagecurve(k0, n0, L, damagerating):
    assert (n0 <= 0.0)
    assert (k0 < L)
    if damagerating > k0 + n0:
        k = np.log(L / (L - k0)) / k0
        n = np.log(1 - (k0 + n0) / L) + k * (k0 + n0)
        percentage = L - (L / np.e ** (k * damagerating - n))
        return round(percentage)
    else:
        return damagerating

def damagehelper(damagerating, PvP):
    if PvP:
        return damagecurve(183, 0, 188, damagerating)
    else:
        return damagecurve(220, 0, 225, damagerating)

def pierceresist(pierce, resist):
    if pierce < resist:
        return (100 - resist + pierce) / 100
    else:
        return 1

def critdamage(c, b, PvP):
    if PvP:
        return 2 - (5 * b) / (c + 5 * b)
    else:
        return 2 - (3 * b) / (c + 3 * b)

def clamp(number, highend):
    if number >= highend:
        return highend
    else:
        return number

def critchance(c, b, PvP, casterlevel=160):
    if PvP:
        return clamp(clamp(casterlevel / 185, 1) * (12 * c) / (12 * c + b), .95)
    else:
        return clamp(clamp(casterlevel / 100, 1) * (3 * c) / (3 * c + b), .95)

def blockchance(c, b, PvP, receiverlevel=160):
    if PvP:
        return clamp(receiverlevel / 185, 1) * b / (b + 12 * c)
    else:
        return .4 * (1 - critchance(c, b, PvP, receiverlevel))

def effectivecrit(c, b, PvP, casterlevel=160, receiverlevel=160):
    if PvP:
        effectivecritchance = critchance(c, b, PvP, casterlevel) * (1 - blockchance(c, b, PvP, receiverlevel))
        return 1 + effectivecritchance * (critdamage(c, b, PvP) - 1)
    else:
        effectivecritchance = critchance(c, b, PvP, casterlevel) * (1 - blockchance(c, b, PvP, receiverlevel))
        return 1 + effectivecritchance * (critdamage(c, b, PvP) - 1)

def effectivedpp(hitter, hitterschools, PvP, defender):
    schooldpp = {"Storm": 125, "Fire": 100, "Ice": 83, "Balance": 85, "Myth": 90, "Death": 85, "Life": 83}
    dpp = schooldpp[hitterschools]
    damage = damagehelper(hitter['Damage'], PvP)
    critical = hitter["Critical"]
    pierce = hitter["Pierce"]
    block = defender["Universal Block"]
    schoolresist = f"{hitterschools} Resist"
    totalresist = defender["Universal Resist"] + defender[schoolresist]
    totaleffectivedamage = (100 + damage) / 100 * pierceresist(pierce, totalresist) * effectivecrit(critical, block,
                                                                                                    PvP)
    effectivedpp = totaleffectivedamage * dpp
    return effectivedpp

def pipstodie(hitter, hitterschools, defender, PvP, reinforce=False):
    schooldpp = {"Storm": 125, "Fire": 100, "Ice": 83, "Balance": 85, "Myth": 90, "Death": 85, "Life": 83}
    dpp = 0
    for school in hitterschools:
        dpp += schooldpp[school] / len(hitterschools)
    damage = damagehelper(hitter['Universal Damage'], PvP)
    critical = hitter["Universal Critical"]
    # pierce = hitter["Pierce"]
    playerhealth = defender["Health"]
    block = defender["Block"]
    # schoolresist = f"{hitterschools} Resist"
    # totalresist = defender["Universal Resist"] + defender[schoolresist]
    # if reinforce is True:
    #    totalpipstodie = playerhealth/((100 + damage)/100 * pierceresist(pierce,totalresist - 40) * PvPeffectivecrit(critical,block))
    # else:
    #    totalpipstodie = playerhealth/((100 + damage)/100 * pierceresist(pierce,totalresist) * PvPeffectivecrit(critical,block))
    totalpipstodie = playerhealth / ((100 + damage) / 100 * effectivecrit(critical, block, PvP))
    pipstodie = totalpipstodie / dpp
    return pipstodie

def howtoaddjewels(pips,accuracy):
    jewels = {"Power Pip": 0, "Accuracy": 0}
    totaljewels = 0
    while totaljewels < 2:
        if accuracy < 100 or pips >= 100:
            accuracy+=16
            jewels["Accuracy"]+=1
            totaljewels+=1
        elif pips < 100:
            pips+=10
            jewels["Power Pip"]+=1
            totaljewels+=1
    return jewels

# MAIN

# imports all files
data = open("RaidGearv1.csv")
data = pd.read_csv(data)
data['Set'].fillna("N/A",inplace=True)
data.fillna(0,inplace=True)

setbonuses = open("SetBonuses.csv")
setbonuses = pd.read_csv(setbonuses)
setbonuses.fillna(0,inplace=True)

mobs = open("RaidMobs.csv")
mobs = pd.read_csv(mobs)
mobs = mobs.fillna(0)

# Initializing dataframes
columns = []
for column in data.select_dtypes(include=np.number).columns:
    columns.append(column)
schools = ["Storm","Fire","Ice","Balance","Myth","Death","Life"]
allthesetups = {}
for school in schools:
    newdataframe = pd.DataFrame(columns=columns)
    allthesetups[school] = newdataframe

# Creating Cartesian Product from all gear pieces
types = data['Type'].unique().tolist()
allthecombos = {}
for school in schools:
    items = data[(data["School"] == school) | (data["School"] == "Any")]
    alltheitems = []
    for itemtype in types:
        considered = items[(items["Type"] == itemtype)]
        names = considered["Name"].tolist()
        alltheitems.append(names)
    index = pd.MultiIndex.from_product(alltheitems, names = types)
    index = index.drop_duplicates()
    combos = pd.DataFrame(index = index).reset_index()
    allthecombos[school] = combos

# Establishing base stats for all configurations
accuracyneeded = {"Storm": 35,"Fire": 30,"Ice": 25,"Balance": 20,"Myth": 25,"Death": 20,"Life": 15}
basehealth = {"Fire":4063,"Ice":5429,"Storm":3213,"Myth":3973,"Life":5280,"Death":4744,"Balance":4873}
for school in schools:
    allthesetups[school] = pd.concat([allthecombos[school],allthesetups[school]])
    allthesetups[school]['Pierce'].fillna(18,inplace=True)
    allthesetups[school]['Power Pip'].fillna(40,inplace=True)
    allthesetups[school]['Accuracy'].fillna(100-accuracyneeded[school],inplace=True)
    allthesetups[school]['Health'].fillna(basehealth[school] + 155*3,inplace=True)
    allthesetups[school].fillna(0,inplace=True)

# Stat summation and set bonus handling for all configurations
for school in schools:
    for rowindex in range(0,len(allthesetups[school])):
        setup = allthesetups[school].iloc[rowindex].tolist()[:10]
        amountofpiecesperset = {}
        for item in setup:
            itemdataentry = data[data['Name'] == item].reset_index()

            if len(itemdataentry) > 1:
                schoolspecific = itemdataentry[itemdataentry['School'] == school].reset_index()
                universal = itemdataentry[itemdataentry['School'] == "Any"].reset_index()
                if len(schoolspecific) == 1:
                    itemdataentry = schoolspecific
                else:
                    itemdataentry = universal

            # SET BONUS CODE
            if itemdataentry.loc[0,'Set'] != "N/A":
                if itemdataentry.loc[0,'Set'] not in amountofpiecesperset:
                    amountofpiecesperset[itemdataentry.loc[0,'Set']] = 1
                else:
                    amountofpiecesperset[itemdataentry.loc[0,'Set']]+=1

            # THIS SUMMATION FUNCTION CAN PROBABLY BE OPTIMIZED
            for column in allthesetups[school].select_dtypes(include=np.number).columns:
                allthesetups[school].loc[rowindex,column]+=itemdataentry[column].mean()
        #SET BONUS CODE
        for sets in amountofpiecesperset:
            if amountofpiecesperset[sets] > 1:
                setdataentries = setbonuses[setbonuses['Name'] == sets].reset_index()
                setdataentries = setdataentries[setdataentries['Pieces'] <= amountofpiecesperset[sets]]
                for setbonusrowindex in range(0,len(setdataentries)):
                    for column in allthesetups[school].select_dtypes(include=np.number).columns:
                        allthesetups[school].loc[rowindex,column]+=setdataentries[column].sum()

# Calculates optimal jewels for all set ups
for school in schools:
    for rowindex in range(0,len(allthesetups[school])):
        jewels = howtoaddjewels(allthesetups[school].loc[rowindex,'Power Pip'],
                                       allthesetups[school].loc[rowindex,'Accuracy'])
        allthesetups[school].loc[rowindex,'Power Pip']+=(10 * jewels['Power Pip'])
        allthesetups[school].loc[rowindex,'Accuracy']+=(16 * jewels['Accuracy'])

# Drops setups that do not reach 100% power pip and accuracy
for school in schools:
    allthesetups[school] = allthesetups[school][(allthesetups[school]['Power Pip'] >= 100) & 
                                                (allthesetups[school]['Accuracy'] >= 100)]
    allthesetups[school] = allthesetups[school].reset_index()
    allthesetups[school].drop('index',inplace=True,axis=1)

# Handles calculations for bosses and minions
# Bosses get an individual dataframe, minions get one dataframe that represents an average of all minions
minions = mobs[mobs['Minion']].reset_index()
bosses = mobs[~mobs['Minion']].reset_index()
bosses.drop('index',inplace=True,axis=1)
minions.drop('index',inplace=True,axis=1)
mobframes = {}
mobframes['Minions'] = {}
for bossindex in range(0,len(bosses)):
    mobframes[bosses.loc[bossindex,"Name"]] = {}
    for school in schools:
        for rowindex in range(0,len(allthesetups[school])):
            player = allthesetups[school].loc[rowindex]
            enemy = bosses.loc[bossindex]
            enemyschools = enemy['School'].split(";")
            allthesetups[school].loc[rowindex,'Effective DPP'] = effectivedpp(player,school,pvp,enemy)
            allthesetups[school].loc[rowindex,'Pips to die'] = pipstodie(enemy,enemyschools,player,pvp,True)
        if len(allthesetups[school]) > 0:
            allthesetups[school] = allthesetups[school].sort_values("Effective DPP",ascending=False)
        mobframes[bosses.loc[bossindex,"Name"]][school] = allthesetups[school].copy()
        allthesetups[school]['Effective DPP'] = 0
        allthesetups[school]['Pips to die'] = 0
        
for minionindex in range(0,len(minions)):
    for school in schools:
        for rowindex in range(0,len(allthesetups[school])):
            player = allthesetups[school].loc[rowindex]
            enemy = bosses.loc[bossindex]
            enemyschools = enemy['School'].split(";")
            allthesetups[school].loc[rowindex,'Effective DPP']+=effectivedpp(player,school,pvp,enemy)/len(minions)
            allthesetups[school].loc[rowindex,'Pips to die']+=pipstodie(enemy,enemyschools,player,pvp,True)/len(minions)
            
    if len(allthesetups[school]) > 0:
            allthesetups[school] = allthesetups[school].sort_values("Effective DPP",ascending=False)
    mobframes['Minions'][school] = allthesetups[school].copy()
    allthesetups[school]['Effective DPP'] = 0
    allthesetups[school]['Pips to die'] = 0

# Output
a = mobframes['Gobblorian Bandit']['Storm']
a.to_csv("results.csv")





