from enum import IntFlag
from struct import unpack
from typing import Tuple, List
from dataclasses import dataclass

_PET_LEVELS = ["Baby", "Teen", "Adult", "Ancient", "Epic", "Mega", "Ultra"]

_ITEMS_STR = [
    "Hat",
    "Robe",
    "Shoes",
    "Weapon",
    "Athame",
    "Amulet",
    "Ring",
    "Deck",
    "Jewel",
    "Mount",
]

_SCHOOLS_STR = [
    "Universal",
    "Universal",
    "Fire",
    "Ice",
    "Storm",
    "Myth",
    "Life",
    "Death",
    "Balance",
    "Star",
    "Sun",
    "Moon",
    "Gardening",
    "Shadow",
    "Fishing",
    "Cantrips",
    "Castlemagic",
    "WhirlyBurly",
]

_SPELL_TYPES_STR = [
    "Any",
    "Healing",
    "Damage",
    "Charm",
    "Ward",
    "Aura",
    "Global",
    "AOE",
    "Steal",
    "Manipulation",
    "Enchantment",
    "Polymorph",
    "Curse",
    "Jinx",
    "Mutate",
    "Cloak",
    "Shadow",
    "Shadow",
    "Shadow",
]


_MONSTROLOGY_EXTRACTS = [
    "Undead",
    "Gobbler",
    "Mander",
    "Spider",
    "Colossus",
    "Cyclops",
    "Golem",
    "Draconian",
    "Treant",
    "Imp",
    "Pig",
    "Elephant",
    "Wyrm",
    "Dino",
    "Bird",
    "Insect",
    "Polar Bear",
]

class MonstrologyKind(IntFlag):
    UNDEAD = 1 << 0
    GOBBLER = 1 << 1
    MANDER = 1 << 2
    SPIDER = 1 << 3
    COLOSSUS = 1 << 4
    CYCLOPS = 1 << 5
    GOLEM = 1 << 6
    DRACONIAN = 1 << 7
    TREANT = 1 << 8
    IMP = 1 << 9
    PIG = 1 << 10
    ELEPHANT = 1 << 11
    WYRM = 1 << 12
    DINO = 1 << 13
    PARROT = 1 << 14
    INSECT = 1 << 15
    POLAR_BEAR = 1 << 16


class ItemKind(IntFlag):
    HAT = 1 << 0
    ROBE = 1 << 1
    SHOES = 1 << 2
    WEAPON = 1 << 3
    ATHAME = 1 << 4
    AMULET = 1 << 5
    RING = 1 << 6
    DECK = 1 << 7
    JEWEL = 1 << 8
    MOUNT = 1 << 9


class ExtraFlags(IntFlag):
    PET_JEWEL = 1 << 0
    NO_AUCTION = 1 << 1
    CROWNS_ONLY = 1 << 2
    NO_GIFT = 1 << 3
    INSTANT_EFFECT = 1 << 4
    NO_COMBAT = 1 << 5
    NO_DROPS = 1 << 6
    NO_DYE = 1 << 7
    NO_HATCHMAKING = 1 << 8
    NO_PVP = 1 << 9
    NO_SELL = 1 << 10
    NO_SHATTER = 1 << 11
    NO_TRADE = 1 << 12
    PVP_ONLY = 1 << 13
    ARENA_POINTS_ONLY = 1 << 14
    BLUE_ARENA_POINTS_ONLY = 1 << 15


@dataclass
class StatObject:
    order: int
    value: int
    string: str

    def to_string(self) -> str:
        if self.string.startswith(("Allows", "Invul", "Gives", "Maycasts")):
            return self.string
        elif self.value > 0:
            return f"+{self.value}{self.string}"
        else:
            return f"{self.value}{self.string}"


def translate_flags(flag: int) -> List[str]:
    flags = []
    if flag & ExtraFlags.NO_AUCTION:
        flags.append("No Auction")
    if flag & ExtraFlags.CROWNS_ONLY:
        flags.append("Crowns Only")
    if flag & ExtraFlags.NO_COMBAT:
        flags.append("No Combat")
    if flag & ExtraFlags.NO_DROPS:
        flags.append("No Drops")
    if flag & ExtraFlags.NO_DYE:
        flags.append("No Dye")
    if flag & ExtraFlags.NO_HATCHMAKING:
        flags.append("No Hatchmaking")
    if flag & ExtraFlags.NO_PVP:
        flags.append("No PvP")
    if flag & ExtraFlags.NO_SELL:
        flags.append("No Sell")
    if flag & ExtraFlags.NO_SHATTER:
        flags.append("No Shatter")
    if flag & ExtraFlags.NO_TRADE:
        flags.append("No Trade")
    if flag & ExtraFlags.PVP_ONLY:
        flags.append("PvP Only")
    if flag & ExtraFlags.ARENA_POINTS_ONLY:
        flags.append("Arena Points Only")
    if flag & ExtraFlags.BLUE_ARENA_POINTS_ONLY:
        flags.append("Blue Arena Points Only")

    return flags



def _fnv_1a(data: bytes) -> int:
    state = 0xCBF2_9CE4_8422_2325
    for b in data:
        state ^= b
        state *= 0x0000_0100_0000_01B3
        state &= 0xFFFF_FFFF_FFFF_FFFF
    return state >> 1


_STAT_DISPLAY_TABLE = {
    _fnv_1a(b"CanonicalFireDamage"): f"Fire Damage",
    _fnv_1a(b"CanonicalIceDamage"): f"Ice Damage",
    _fnv_1a(b"CanonicalStormDamage"): f"Storm Damage",
    _fnv_1a(b"CanonicalMythDamage"): f"Myth Damage",
    _fnv_1a(b"CanonicalDeathDamage"): f"Death Damage",
    _fnv_1a(b"CanonicalShadowDamage"): f"Shadow Damage",
    _fnv_1a(b"CanonicalSunDamage"): f"Sun Damage",
    _fnv_1a(b"CanonicalStarDamage"): f"Star Damage",
    _fnv_1a(b"CanonicalMoonDamage"): f"Moon Damage",
    _fnv_1a(b"CanonicalAllDamage"): f"Damage",
    _fnv_1a(b"CanonicalAllFishingLuck"): f"Fishing Luck",
    _fnv_1a(b"CanonicalStormAccuracy"): f"Storm Accuracy",
    _fnv_1a(b"CanonicalFireAccuracy"): f"Fire Accuracy",
    _fnv_1a(b"CanonicalIceAccuracy"): f"Ice Accuracy",
    _fnv_1a(b"CanonicalLifeAccuracy"): f"Life Accuracy",
    _fnv_1a(b"CanonicalDeathAccuracy"): f"Death Accuracy",
    _fnv_1a(b"CanonicalBalanceAccuracy"): f"Balance Accuracy",
    _fnv_1a(b"CanonicalMythAccuracy"): f"Myth Accuracy",
    _fnv_1a(b"CanonicalShadowAccuracy"): f"Shadow Accuracy",
    _fnv_1a(b"CanonicalSunAccuracy"): f"Sun Accuracy",
    _fnv_1a(b"CanonicalStarAccuracy"): f"Star Accuracy",
    _fnv_1a(b"CanonicalMoonAccuracy"): f"Moon Accuracy",
    _fnv_1a(b"CanonicalAllAccuracy"): f"Accuracy",
    _fnv_1a(b"CanonicalStormArmorPiercing"): f"Storm Pierce",
    _fnv_1a(b"CanonicalFireArmorPiercing"): f"Fire Pierce",
    _fnv_1a(b"CanonicalIceArmorPiercing"): f"Ice Pierce",
    _fnv_1a(b"CanonicalLifeArmorPiercing"): f"Life Pierce",
    _fnv_1a(b"CanonicalDeathArmorPiercing"): f"Death Pierce",
    _fnv_1a(b"CanonicalBalanceArmorPiercing"): f"Balance Pierce",
    _fnv_1a(b"CanonicalMythArmorPiercing"): f"Myth Pierce",
    _fnv_1a(b"CanonicalShadowArmorPiercing"): f"Shadow Pierce",
    _fnv_1a(b"CanonicalSunArmorPiercing"): f"Sun Pierce",
    _fnv_1a(b"CanonicalStarArmorPiercing"): f"Star Pierce",
    _fnv_1a(b"CanonicalMoonArmorPiercing"): f"Moon Pierce",
    _fnv_1a(b"CanonicalAllArmorPiercing"): f"Pierce",
    _fnv_1a(b"CanonicalLifeHealing"): f"Outgoing Healing",
    _fnv_1a(b"CanonicalPowerPip"): f"Power Pip Chance",
    _fnv_1a(b"CanonicalMaxMana"): f"Mana",
    _fnv_1a(b"CanonicalMaxHealth"): f"Health",
    _fnv_1a(b"CanonicalFireFlatDamage"): f"Fire Flat Damage",
    _fnv_1a(b"CanonicalIceFlatDamage"): f"Ice Flat Damage",
    _fnv_1a(b"CanonicalStormFlatDamage"): f"Storm Flat Damage",
    _fnv_1a(b"CanonicalMythFlatDamage"): f"Myth Flat Damage",
    _fnv_1a(b"CanonicalDeathFlatDamage"): f"Death Flat Damage",
    _fnv_1a(b"CanonicalShadowFlatDamage"): f"Shadow Flat Damage",
    _fnv_1a(b"CanonicalSunFlatDamage"): f"Sun Flat Damage",
    _fnv_1a(b"CanonicalStarFlatDamage"): f"Star Flat Damage",
    _fnv_1a(b"CanonicalMoonFlatDamage"): f"Moon Flat Damage",
    _fnv_1a(b"CanonicalAllFlatDamage"): f"Flat Damage",
    _fnv_1a(b"CanonicalFireReduceDamage"): f"Fire Resist",
    _fnv_1a(b"CanonicalIceReduceDamage"): f"Ice Resist",
    _fnv_1a(b"CanonicalStormReduceDamage"): f"Storm Resist",
    _fnv_1a(b"CanonicalMythReduceDamage"): f"Myth Resist",
    _fnv_1a(b"CanonicalDeathReduceDamage"): f"Death Resist",
    _fnv_1a(b"CanonicalShadowReduceDamage"): f"Shadow Resist",
    _fnv_1a(b"CanonicalSunReduceDamage"): f"Sun Resist",
    _fnv_1a(b"CanonicalStarReduceDamage"): f"Star Resist",
    _fnv_1a(b"CanonicalMoonReduceDamage"): f"Moon Resist",
    _fnv_1a(b"CanonicalAllReduceDamage"): f"Resist",
    _fnv_1a(b"CanonicalIncHealing"): f"Incoming Healing",
    _fnv_1a(b"CanonicalIncomingAccuracy"): f"Accuracy",
    _fnv_1a(b"CanonicalLifeReduceDamage"): f"Life Resist",
    _fnv_1a(b"CanonicalBalanceReduceDamage"): f"Balance Resist",
    _fnv_1a(b"CanonicalLifeDamage"): f"Life Damage",
    _fnv_1a(b"CanonicalLifeFlatDamage"): f"Life Flat Damage",
    _fnv_1a(b"CanonicalBalanceDamage"): f"Balance Damage",
    _fnv_1a(b"CanonicalBalanceFishingLuck"): f"Balance Fishing Luck",
    _fnv_1a(b"CanonicalDeathFishingLuck"): f"Death Fishing Luck",
    _fnv_1a(b"CanonicalFireFishingLuck"): f"Fire Fishing Luck",
    _fnv_1a(b"CanonicalIceFishingLuck"): f"Ice Fishing Luck",
    _fnv_1a(b"CanonicalLifeFishingLuck"): f"Life Fishing Luck",
    _fnv_1a(b"CanonicalMythFishingLuck"): f"Myth Fishing Luck",
    _fnv_1a(b"CanonicalShadowFishingLuck"): f"Shadow Fishing Luck",
    _fnv_1a(b"CanonicalStormFishingLuck"): f"Storm Fishing Luck",
    _fnv_1a(b"CanonicalBalanceFlatDamage"): f"Balance Flat Damage",
    _fnv_1a(b"CanonicalMaxManaPercentReduce"): f"-100% Max Mana",
    _fnv_1a(b"XPPercent"): f"XP%",
    _fnv_1a(b"GoldPercent"): f"Gold%",    
    _fnv_1a(b"CanonicalMaxEnergy"): f"Energy",
    _fnv_1a(b"CanonicalAllCriticalHit"): f"Crit Rating",
    _fnv_1a(b"CanonicalAllBlock"): f"Block Rating",
    _fnv_1a(b"CanonicalAllPowerPipRating"): f"Power Pip Chance",
    _fnv_1a(b"CanonicalAllReduceDamageRating"): f"Resist",
    _fnv_1a(b"CanonicalAllAccuracyRating"): f"Accuracy",
    _fnv_1a(b"CanonicalStormCriticalHit"): f"Storm Crit Rating",
    _fnv_1a(b"CanonicalMythCriticalHit"): f"Myth Crit Rating",
    _fnv_1a(b"CanonicalLifeCriticalHit"): f"Life Crit Rating",
    _fnv_1a(b"CanonicalIceCriticalHit"): f"Ice Crit Rating",
    _fnv_1a(b"CanonicalFireCriticalHit"): f"Fire Crit Rating",
    _fnv_1a(b"CanonicalDeathCriticalHit"): f"Death Crit Rating",
    _fnv_1a(b"CanonicalBalanceCriticalHit"): f"Balance Crit Rating",
    _fnv_1a(b"CanonicalShadowCriticalHit"): f"Shadow Crit Rating",
    _fnv_1a(b"CanonicalSunCriticalHit"): f"Sun Crit Rating",
    _fnv_1a(b"CanonicalStarCriticalHit"): f"Star Crit Rating",
    _fnv_1a(b"CanonicalMoonCriticalHit"): f"Moon Crit Rating",
    _fnv_1a(b"CanonicalBalanceBlock"): f"Balance Block Rating",
    _fnv_1a(b"CanonicalDeathBlock"): f"Death Block Rating",
    _fnv_1a(b"CanonicalFireBlock"): f"Fire Block Rating",
    _fnv_1a(b"CanonicalIceBlock"): f"Ice Block Rating",
    _fnv_1a(b"CanonicalLifeBlock"): f"Life Block Rating",
    _fnv_1a(b"CanonicalMythBlock"): f"Myth Block Rating",
    _fnv_1a(b"CanonicalStormBlock"): f"Storm Block Rating",
    _fnv_1a(b"CanonicalShadowBlock"): f"Shadow Block Rating",
    _fnv_1a(b"CanonicalSunBlock"): f"Sun Block Rating",
    _fnv_1a(b"CanonicalStarBlock"): f"StarBlock Rating",
    _fnv_1a(b"CanonicalMoonBlock"): f"Moon Block Rating",
    _fnv_1a(b"CanonicalBalanceAccuracyRating"): f"Balance Accuracy",
    _fnv_1a(b"CanonicalDeathAccuracyRating"): f"Death Accuracy",
    _fnv_1a(b"CanonicalFireAccuracyRating"): f"Fire Accuracy",
    _fnv_1a(b"CanonicalIceAccuracyRating"): f"Ice Accuracy",
    _fnv_1a(b"CanonicalLifeAccuracyRating"): f"Life Accuracy",
    _fnv_1a(b"CanonicalMythAccuracyRating"): f"Myth Accuracy",
    _fnv_1a(b"CanonicalStormAccuracyRating"): f"Storm Accuracy",
    _fnv_1a(b"CanonicalShadowAccuracyRating"): f"Shadow Accuracy",
    _fnv_1a(b"CanonicalBalanceReduceDamageRating"): f"Balance Resist",
    _fnv_1a(b"CanonicalDeathReduceDamageRating"): f"Death Resist",
    _fnv_1a(b"CanonicalFireReduceDamageRating"): f"Fire Resist",
    _fnv_1a(b"CanonicalIceReduceDamageRating"): f"Ice Resist",
    _fnv_1a(b"CanonicalLifeReduceDamageRating"): f"Life Resist",
    _fnv_1a(b"CanonicalMythReduceDamageRating"): f"Myth Resist",
    _fnv_1a(b"CanonicalStormReduceDamageRating"): f"Storm Resist",
    _fnv_1a(b"CanonicalShadowReduceDamageRating"): f"Shadow Resist",
    _fnv_1a(b"CanonicalBalanceMastery"): f"Allows Power Pip With Balance Spells",
    _fnv_1a(b"CanonicalDeathMastery"): f"Allows Power Pip With Death Spells",
    _fnv_1a(b"CanonicalFireMastery"): f"Allows Power Pip With Fire Spells",
    _fnv_1a(b"CanonicalIceMastery"): f"Allows Power Pip With Ice Spells",
    _fnv_1a(b"CanonicalLifeMastery"): f"Allows Power Pip With Life Spells",
    _fnv_1a(b"CanonicalMythMastery"): f"Allows Power Pip With Myth Spells",
    _fnv_1a(b"CanonicalStormMastery"): f"Allows Power Pip With Storm Spells",
    _fnv_1a(b"CanonicalStunResistance"): f"Stun Resist",
    _fnv_1a(b"ReduceDamageInvunerable"): f"Invulnerable To Damage",
    _fnv_1a(b"CanonicalShadowPip"): f"Shadow Pip Rating",
    _fnv_1a(b"CanonicalAllFlatReduceDamage"): f"Flat Resist",
    _fnv_1a(b"CanonicalLifeFlatReduceDamage"): f"Life Flat Resist",
    _fnv_1a(b"CanonicalDeathFlatReduceDamage"): f"Death Flat Resist",
    _fnv_1a(b"CanonicalMythFlatReduceDamage"): f"Myth Flat Resist",
    _fnv_1a(b"CanonicalStormFlatReduceDamage"): f"Storm Flat Resist",
    _fnv_1a(b"CanonicalIceFlatReduceDamage"): f"Ice Flat Resist",
    _fnv_1a(b"CanonicalFireFlatReduceDamage"): f"Fire Flat Resist",
    _fnv_1a(b"CanonicalBalanceFlatReduceDamage"): f"Balance Flat Resist",
    _fnv_1a(b"CanonicalShadowFlatReduceDamage"): f"Shadow Flat Resist",
    _fnv_1a(b"CanonicalSunFlatReduceDamage"): f"Sun Flat Resist",
    _fnv_1a(b"CanonicalStarFlatReduceDamage"): f"Star Flat Resist",
    _fnv_1a(b"CanonicalMoonFlatReduceDamage"): f"Moon Flat Resist",
    _fnv_1a(b"CanonicalWispBonus"): f"Wisp Bonus",
    _fnv_1a(b"CanonicalAllPipConversion"): f"Pip Conversion Rating",
    _fnv_1a(b"CanonicalFirePipConversion"): f"Fire Pip Conversion Rating",
    _fnv_1a(b"CanonicalIcePipConversion"): f"Ice Pip Conversion Rating",
    _fnv_1a(b"CanonicalLifePipConversion"): f"Life Pip Conversion Rating",
    _fnv_1a(b"CanonicalDeathPipConversion"): f"Death Pip Conversion Rating",
    _fnv_1a(b"CanonicalMythPipConversion"): f"Myth Pip Conversion Rating",
    _fnv_1a(b"CanonicalBalancePipConversion"): f"Balance Pip Conversion Rating",
    _fnv_1a(b"CanonicalStormPipConversion"): f"Storm Pip Conversion Rating",
    _fnv_1a(b"CanonicalShadowPipConversion"): f"Shadow Pip Conversion Rating",
    _fnv_1a(b"CanonicalSunPipConversion"): f"Sun Pip Conversion Rating",
    _fnv_1a(b"CanonicalStarPipConversion"): f"Star Pip Conversion Rating",
    _fnv_1a(b"CanonicalMoonPipConversion"): f"Moon Pip Conversion Rating",
    _fnv_1a(b"CanonicalShadowPipRating"): f"Shadow Pip Stat Rating",
    _fnv_1a(b"CanonicalAllArchmastery"): f"Archmastery Rating",
}

def translate_stat(stat: int) -> Tuple[int, str, bool]:
    display_stat = _STAT_DISPLAY_TABLE[stat]
    return display_stat

def unpack_stat_value(value: int) -> float:
    raw = value.to_bytes(4, "little")
    return unpack("<f", raw)[0]

def unpack_int_list(value: int) -> List[int]:
    raw = value.to_bytes(88, "little")
    return unpack("<22i", raw)

def translate_rarity(rarity: int) -> str:
    match rarity:
        case -1:
            return "Unknown"
        case 0:
            return "Common"
        case 1:
            return "Uncommon"
        case 2:
            return "Rare"
        case 3:
            return "Ultra-rare"
        case 4:
            return "Epic"


def translate_equip_school(school: int) -> str:
    if school & (1 << 31) != 0:
        school = _SCHOOLS_STR[school - (1 << 31)]
        return f"All schools except {school}"
    else:
        school = _SCHOOLS_STR[school]
        return f"{school}"

def get_item_str(item: ItemKind) -> str:
    bit_index = item.value.bit_length() - 1
    return _ITEMS_STR[bit_index]

def format_sockets(jewels: int) -> str:
    sockets = []

    while jewels != 0:
        socket = jewels & 0xF

        match socket >> 1:
            case 0:
                description = "???"
            case 1:
                description = "Tear"
            case 2:
                description = "Circle"
            case 3:
                description = "Square"
            case 4:
                description = "Triangle"
            case 5:
                description = "Power"
            case 6:
                description = "Shield"
            case 7:
                description = "Sword"

            case _:
                raise ValueError("Unknown emoji type")

        sockets.append(f"{description}")

        jewels >>= 4

    return sockets


def translate_pet_level(level: int) -> str:
    return _PET_LEVELS[level - 1]




