import database as db
import json
import math

SCHOOLS = ["Fire", "Ice", "Storm", "Balance", "Myth", "Life", "Death"]

LEVEL_SCALED_DATA_TABLE = {
    "m_canonicalFireDamage": f"Fire Damage",
    "m_canonicalIceDamage": f"Ice Damage",
    "m_canonicalStormDamage": f"Storm Damage",
    "m_canonicalMythDamage": f"Myth Damage",
    "m_canonicalDeathDamage": f"Death Damage",
    "m_canonicalShadowDamage": f"Shadow Damage",
    "m_canonicalSunDamage": f"Sun Damage",
    "m_canonicalStarDamage": f"Star Damage",
    "m_canonicalMoonDamage": f"Moon Damage",
    "m_canonicalStormAccuracy": f"Storm Accuracy",
    "m_canonicalFireAccuracy": f"Fire Accuracy",
    "m_canonicalIceAccuracy": f"Ice Accuracy",
    "m_canonicalLifeAccuracy": f"Life Accuracy",
    "m_canonicalDeathAccuracy": f"Death Accuracy",
    "m_canonicalBalanceAccuracy": f"Balance Accuracy",
    "m_canonicalMythAccuracy": f"Myth Accuracy",
    "m_canonicalShadowAccuracy": f"Shadow Accuracy",
    "m_canonicalSunAccuracy": f"Sun Accuracy",
    "m_canonicalStarAccuracy": f"Star Accuracy",
    "m_canonicalMoonAccuracy": f"Moon Accuracy",
    "m_canonicalStormArmorPiercing": f"Storm Pierce",
    "m_canonicalFireArmorPiercing": f"Fire Pierce",
    "m_canonicalIceArmorPiercing": f"Ice Pierce",
    "m_canonicalLifeArmorPiercing": f"Life Pierce",
    "m_canonicalDeathArmorPiercing": f"Death Pierce",
    "m_canonicalBalanceArmorPiercing": f"Balance Pierce",
    "m_canonicalMythArmorPiercing": f"Myth Pierce",
    "m_canonicalShadowArmorPiercing": f"Shadow Pierce",
    "m_canonicalSunArmorPiercing": f"Sun Pierce",
    "m_canonicalStarArmorPiercing": f"Star Pierce",
    "m_canonicalMoonArmorPiercing": f"Moon Pierce",
    "m_canonicalAllArmorPiercing": f"Pierce",
    "m_canonicalLifeHealing": f"Outgoing Healing",
    "m_canonicalPowerPip": f"Power Pip Chance",
    "m_canonicalMaxMana": f"Mana",
    "m_canonicalMaxHealth": f"Health",
    "m_canonicalFireFlatDamage": f"Fire Flat Damage",
    "m_canonicalIceFlatDamage": f"Ice Flat Damage",
    "m_canonicalStormFlatDamage": f"Storm Flat Damage",
    "m_canonicalMythFlatDamage": f"Myth Flat Damage",
    "m_canonicalDeathFlatDamage": f"Death Flat Damage",
    "m_canonicalShadowFlatDamage": f"Shadow Flat Damage",
    "m_canonicalSunFlatDamage": f"Sun Flat Damage",
    "m_canonicalStarFlatDamage": f"Star Flat Damage",
    "m_canonicalMoonFlatDamage": f"Moon Flat Damage",
    "m_canonicalFireReduceDamage": f"Fire Resist",
    "m_canonicalIceReduceDamage": f"Ice Resist",
    "m_canonicalStormReduceDamage": f"Storm Resist",
    "m_canonicalMythReduceDamage": f"Myth Resist",
    "m_canonicalDeathReduceDamage": f"Death Resist",
    "m_canonicalShadowReduceDamage": f"Shadow Resist",
    "m_canonicalSunReduceDamage": f"Sun Resist",
    "m_canonicalStarReduceDamage": f"Star Resist",
    "m_canonicalMoonReduceDamage": f"Moon Resist",
    "m_canonicalIncHealing": f"Incoming Healing",
    "m_canonicalIncomingAccuracy": f"Accuracy",
    "m_canonicalLifeReduceDamage": f"Life Resist",
    "m_canonicalBalanceReduceDamage": f"Balance Resist",
    "m_canonicalLifeDamage": f"Life Damage",
    "m_canonicalLifeFlatDamage": f"Life Flat Damage",
    "m_canonicalBalanceDamage": f"Balance Damage",
    "m_canonicalBalanceFlatDamage": f"Balance Flat Damage",
    "m_canonicalAllPowerPipRating": f"Power Pip Chance",
    "m_canonicalStormCriticalHit": f"Storm Crit Rating",
    "m_canonicalMythCriticalHit": f"Myth Crit Rating",
    "m_canonicalLifeCriticalHit": f"Life Crit Rating",
    "m_canonicalIceCriticalHit": f"Ice Crit Rating",
    "m_canonicalFireCriticalHit": f"Fire Crit Rating",
    "m_canonicalDeathCriticalHit": f"Death Crit Rating",
    "m_canonicalBalanceCriticalHit": f"Balance Crit Rating",
    "m_canonicalShadowCriticalHit": f"Shadow Crit Rating",
    "m_canonicalSunCriticalHit": f"Sun Crit Rating",
    "m_canonicalStarCriticalHit": f"Star Crit Rating",
    "m_canonicalMoonCriticalHit": f"Moon Crit Rating",
    "m_canonicalBalanceBlock": f"Balance Block Rating",
    "m_canonicalDeathBlock": f"Death Block Rating",
    "m_canonicalFireBlock": f"Fire Block Rating",
    "m_canonicalIceBlock": f"Ice Block Rating",
    "m_canonicalLifeBlock": f"Life Block Rating",
    "m_canonicalMythBlock": f"Myth Block Rating",
    "m_canonicalStormBlock": f"Storm Block Rating",
    "m_canonicalShadowBlock": f"Shadow Block Rating",
    "m_canonicalSunBlock": f"Sun Block Rating",
    "m_canonicalStarBlock": f"StarBlock Rating",
    "m_canonicalMoonBlock": f"Moon Block Rating",
    "m_canonicalBalanceAccuracyRating": f"Balance Accuracy",
    "m_canonicalDeathAccuracyRating": f"Death Accuracy",
    "m_canonicalFireAccuracyRating": f"Fire Accuracy",
    "m_canonicalIceAccuracyRating": f"Ice Accuracy",
    "m_canonicalLifeAccuracyRating": f"Life Accuracy",
    "m_canonicalMythAccuracyRating": f"Myth Accuracy",
    "m_canonicalStormAccuracyRating": f"Storm Accuracy",
    "m_canonicalShadowAccuracyRating": f"Shadow Accuracy",
    "m_canonicalBalanceReduceDamageRating": f"Balance Resist",
    "m_canonicalDeathReduceDamageRating": f"Death Resist",
    "m_canonicalFireReduceDamageRating": f"Fire Resist",
    "m_canonicalIceReduceDamageRating": f"Ice Resist",
    "m_canonicalLifeReduceDamageRating": f"Life Resist",
    "m_canonicalMythReduceDamageRating": f"Myth Resist",
    "m_canonicalStormReduceDamageRating": f"Storm Resist",
    "m_canonicalShadowReduceDamageRating": f"Shadow Resist",
    "m_canonicalShadowPip": f"Shadow Pip Rating",
    "m_canonicalLifeFlatReduceDamage": f"Life Flat Resist",
    "m_canonicalDeathFlatReduceDamage": f"Death Flat Resist",
    "m_canonicalMythFlatReduceDamage": f"Myth Flat Resist",
    "m_canonicalStormFlatReduceDamage": f"Storm Flat Resist",
    "m_canonicalIceFlatReduceDamage": f"Ice Flat Resist",
    "m_canonicalFireFlatReduceDamage": f"Fire Flat Resist",
    "m_canonicalBalanceFlatReduceDamage": f"Balance Flat Resist",
    "m_canonicalShadowFlatReduceDamage": f"Shadow Flat Resist",
    "m_canonicalSunFlatReduceDamage": f"Sun Flat Resist",
    "m_canonicalStarFlatReduceDamage": f"Star Flat Resist",
    "m_canonicalMoonFlatReduceDamage": f"Moon Flat Resist",
    "m_canonicalAllPipConversion": f"Pip Conversion Rating",
    "m_canonicalFirePipConversion": f"Fire Pip Conversion Rating",
    "m_canonicalIcePipConversion": f"Ice Pip Conversion Rating",
    "m_canonicalLifePipConversion": f"Life Pip Conversion Rating",
    "m_canonicalDeathPipConversion": f"Death Pip Conversion Rating",
    "m_canonicalMythPipConversion": f"Myth Pip Conversion Rating",
    "m_canonicalBalancePipConversion": f"Balance Pip Conversion Rating",
    "m_canonicalStormPipConversion": f"Storm Pip Conversion Rating",
    "m_canonicalShadowPipConversion": f"Shadow Pip Conversion Rating",
    "m_canonicalSunPipConversion": f"Sun Pip Conversion Rating",
    "m_canonicalStarPipConversion": f"Star Pip Conversion Rating",
    "m_canonicalMoonPipConversion": f"Moon Pip Conversion Rating",
    "m_canonicalShadowPipRating": f"Shadow Pip Stat Rating",
    "m_canonicalAllArchmastery": f"Archmastery Rating",
    "m_maximumPips": f"Maximum Pips",
    "m_maximumPowerPips": f"Maximum Power Pips"
}

class wizardStats:
    def __init__(self):
        self.statCaps = self.createCaps()
        self.baseStats = self.createBaseStats()

    def createCaps(self):
        tempData = {}
        statCaps = json.load(open('LevelScaledData.json'))['m_levelScaledInfoList']

        statsToStandardize = ["Accuracy", "Damage", "Resist", "Pierce", "Healing", "Power Pip Chance"]

        for caps in statCaps:
            levelAndSchool = (caps['m_level'], caps['m_school'])
            del caps["m_level"], caps["m_school"], caps['m_class']
            value = {LEVEL_SCALED_DATA_TABLE.get(k, k): v for k, v in caps.items()}
            for stat in value:
                if any(statToStandardize in stat for statToStandardize in statsToStandardize) and "Flat Damage" not in stat:
                    value[stat] = round(value[stat] * 100)
            tempData[levelAndSchool] = value
        statCaps = tempData
        return statCaps
    
    def getCaps(self, level, school):
        return self.statCaps[(level, school)]
    
    def createBaseStats(self):
        baseStats = json.load(open('MagicXPConfig.json'))
        del baseStats['m_class'], baseStats['m_encounterXPFactors'], baseStats['m_maxSchoolLevel'], baseStats['m_experienceBonus'], baseStats['m_schoolOfFocusBonus'], baseStats['m_levelsConfig']
        
        universalStartingStats = {}

        for entry in baseStats['m_levelInfo']:
            level = entry['m_level']
            universalStartingStats[level] = {"Mana": entry["m_mana"],
                                            "Power Pip Chance": entry["m_pipChance"] * 100,
                                            "Energy": entry["m_petEnergy"],
                                            "Shadow Pip Stat Rating": entry["m_shadowPipRating"],
                                            "Archmastery Rating": entry["m_archmastery"]}

        schoolSpecificStartingStats = {}

        for entry in baseStats['m_classInfo']:
            del entry['m_class']
            schoolName = entry['m_className']
            if schoolName in SCHOOLS:
                for entry2 in entry['m_classLevelInfo']:
                    level = entry2['m_level']
                    schoolSpecificStartingStats[(level, schoolName)] = {"Health": entry2["m_hitpoints"],
                                                                         f"{schoolName} Pip Conversion Rating": entry2[f"m_pipConversionRating{schoolName}"]}
                    schoolSpecificStartingStats[(level, schoolName)] |= universalStartingStats[level]

        return schoolSpecificStartingStats
    
    def getBaseStats(self, level, school):
        return self.baseStats[(level, school)]

def main():
    woop = wizardStats()
    print()
main()