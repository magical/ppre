from collections import namedtuple

# map_table is the offset in the arm9.bin to the table which maps scripts,
#  maps, locations, encounters, and everything together
Offsets = namedtuple('Offsets',
    "map_table, invalid_script_begin, invalid_script_end")

# Indexes to files in the text dump
TextNums = namedtuple('TextNums',
    "locations, types, abilities, items, moves, pokemon, height, weight,"
    "description, flavor_text, forms, trainer_classes, trainers, trainer_text,"
    "contest")

class ROMInfo(object):
    def __init__(self, ID, version, romname, lang,
                 offsets=None, textnums=None):
        self.version = version
        self.romname = romname
        self.lang = lang
        self.ID = ID
        self.offsets = offsets
        self.textnums = textnums
        self.romname

# language codes are ISO 639-1
langcodes = {
    "en": ord("E"),
    "es": ord("S"),
    "de": ord("D"),
    "it": ord("I"),
    "fr": ord("F"),
    "jp": ord("J"),
    "ko": ord("K"), #???
    "zh": ord("H"), #????
}

rev_langcodes = dict((v, k) for k, v in langcodes.iteritems())

def getInfo(ID, lang):
    """Get the rom info, given the ID and lang of the rom."""
    for r in rominfo:
        if r.ID == ID and r.lang == lang:
            return r

# ID is actually the last two letters of the game name stored in the rom, and
# lang is the last letter of the serial number.
# XXX possibly just use the serial number?
# XXX maybe each game should be a subclass instead of an instance
rominfo = [
    #Diamond
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x4A,
        offsets=Offsets(0xF0C28, None, None),
        textnums=TextNums(
            374,555,544,341,575,356,606,605,607,601,600,560,559,555,None),#change tr
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x45,
        offsets=Offsets(0xEEDBC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x44,
        offsets=Offsets(0xEEDCC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x46,
        offsets=Offsets(0xEEDFC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x49,
        offsets=Offsets(0xEED70, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x53,
        offsets=Offsets(0xEEE08, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x4B,
        offsets=Offsets(0xEA408, None, None),
        textnums=TextNums(
            376,557,546,342,577,357,608,606,609,603,602,560,559,555,None),#change tr
    ),

    #Pearl
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x4A,
        offsets=Offsets(0xF0C2C, None, None),
        textnums=TextNums(
            374,555,544,341,575,356,606,605,607,602,600,560,559,555,None),#change tr
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x45,
        offsets=Offsets(0xEEDBC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x44,
        offsets=Offsets(0xEEDCC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x46,
        offsets=Offsets(0xEEDFC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None)
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x49,
        offsets=Offsets(0xEED70, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x53,
        offsets=Offsets(0xEEE08, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x4B,
        offsets=Offsets(0xEA408, None, None),
        textnums=TextNums(
            376,557,546,342,577,357,608,606,609,603,602,560,559,555,None)#change tr
    ),

    #Platinum
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x44,
        offsets=Offsets(0xE6074, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,720,706,697,619,618,613,208),
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x45,
        offsets=Offsets(0xE601C, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,718,706,697,619,618,613,208),
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x46,
        offsets=Offsets(0xE60A4, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,719,706,697,619,618,613,208),
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x49,
        offsets=Offsets(0xE6038, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,721,706,697,619,618,613,208),
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x4A,
        offsets=Offsets(0xE56F0, 501, 1050),
        textnums=TextNums(
            427,616,604,390,636,408,696,694,698,693,685,619,618,613,207),#change tr
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x4B,
        offsets=Offsets(0xE6AA4, 501, 1050),
        textnums=TextNums(
            428,617,605,390,637,408,699,697,696,701,687,619,618,613,208),#change tr
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x53,
        offsets=Offsets(0xE60B0, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,722,706,697,619,618,613,208),
    ),

    #HeartGold
    ROMInfo(
        version="heartgold",
        romname="Heart Gold",
        ID=0x4748,
        lang=0x4A,
        offsets=Offsets(0xE56F0, 501, 1050),
        textnums=TextNums(
            427,724,711,219,739,232,801,799,803,791,790,720,719,None,207),
    ),
    ROMInfo(
        version="heartgold",
        romname="Heart Gold",
        ID=0x4748,
        lang=0x45,
        offsets=Offsets(0xE56F0, 10000, 0),
        textnums=TextNums(
            279,735,720,222,750,237,814,812,803,823,802,730,729,None,207),#location names = 279?
    ),

    #SoulSilver
    ROMInfo(
        version="soulsilver",
        romname="Soul Silver",
        ID=0x5353,
        lang=0x4A,
        offsets=Offsets(0xE56F0, 10000, 0),
        textnums=TextNums(
            427,724,711,219,739,232,801,799,803,792,790,720,719,None,207),
    ),
    ROMInfo(
        version="soulsilver",
        romname="Soul Silver",
        ID=0x5353,
        lang=0x45,
        offsets=Offsets(0xE56F0, 10000, 0),
        textnums=TextNums(
            279,735,720,222,750,237,814,812,803,823,802,730,729,None,207),
    ),
]

