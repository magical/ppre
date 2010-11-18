import os
from collections import namedtuple
from struct import pack, unpack

from narc import NARC

class ROM(object):
    """Represents a game image. It also implements a "virtual file system"."""

    def __init__(self, romname):
        name, ext = os.path.splitext(romname)
        self.romdir = "tmp_" + name
        self.info = None

    # This method exists only to work around the fact that the PPRE's
    # main window must have a rom object when the "no rom" error message
    # is displayed.
    # While RAII is an interesting pattern, it's not one you'll find often in
    # Python code.
    def _load(self):
        ID = self.readID()
        lang = self.readLang()
        self.info = getInfo(ID, lang)

    def open(self, filename, mode="rb"):
        """Open a virtual file, with the given mode."""
        real_path = self.getFullPath(filename)
        f = open(real_path, mode)
        return f

    def readNarc(self, filename):
        """Load a narc file. Returns a NARC object."""
        f = self.open(filename)
        data = f.read()
        f.close()
        return NARC(data)

    def writeNarc(self, filename, archive):
        f = self.open(filename, "wb")
        archive.ToFile(f)
        f.close()

    def getPath(self, filename):
        """Get the real file name which corresponds to a virtual one.

        If the rom does not define a virtual file mapping for the given path,
        it is assumed that the path is correct as is.
        """
        return self.info.filemap.get(filename, filename)

    def getFullPath(self, filename):
        """Get the full path to a virtual file."""
        real_filename = self.getPath(filename)
        real_filename = real_filename.lstrip('/\\')
        path = os.path.join(self.romdir, real_filename)
        return path

    # These two methods can't call self.open because self.info doesn't exist
    # yet!
    def readID(self):
        # The header starts out with the name of the game, so the ID is actually 
        # just the two characters after "POKEMON ".
        path = os.path.join(self.romdir, "header.bin")
        f = open(path, "rb")
        f.seek(8)
        ID = unpack("<H", f.read(2))[0]
        f.close()
        return ID

    def readLang(self):
        # Bytes 12-15 in the header are the serial number of the game, as assigned
        # by nintendo. The last character seems to indicate the language.
        path = os.path.join(self.romdir, "header.bin")
        f = open(path, "rb")
        f.seek(15)
        lang = unpack("<B", f.read(1))[0]
        f.close()
        return lang


    #backwards compatibily
    def getFolder(self):
        return self.romdir

    def create(self, filename):
        return

    def dump(self):
        return



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
                 offsets=None, textnums=None, filemap=None):
        if filemap is None:
            filemap = {}

        self.version = version
        self.romname = romname
        self.lang = lang
        self.ID = ID
        self.offsets = offsets
        self.textnums = textnums
        self.filemap = filemap

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

# These map a virtual file name to the actual name in the rom.
#
# Most of the virtual names come from DP. enc_data.narc is the only virtual
# file with a completely made up name, because the real names all contain the
# version.
filemaps = {
    "diamond": {
        "/root/fielddata/encountdata/enc_data.narc": "/root/fielddata/encountdata/d_enc_data.narc",
        "/root/fielddata/eventdata/zone_event.narc": "/root/fielddata/eventdata/zone_event_release.narc",
        "/root/fielddata/script/scr_seq.narc": "/root/fielddata/script/scr_seq_release.narc",
    },
    "pearl": {
        "/root/fielddata/encountdata/enc_data.narc": "/root/fielddata/encountdata/p_enc_data.narc",
        "/root/fielddata/eventdata/zone_event.narc": "/root/fielddata/eventdata/zone_event_release.narc",
        "/root/fielddata/script/scr_seq.narc": "/root/fielddata/script/scr_seq_release.narc",
        "/root/poketool/personal/personal.narc": "/root/poketool/personal_pearl/personal.narc",
    },
    "platinum": {
        "/root/fielddata/encountdata/enc_data.narc": "/root/fielddata/encountdata/pl_enc_data.narc",
        "/root/msgdata/msg.narc": "/root/msgdata/pl_msg.narc",
        "/root/poketool/personal/personal.narc": "/root/poketool/personal/pl_personal.narc",
        "/root/poketool/waza/waza_tbl.narc": "/root/poketool/waza/pl_waza_tbl.narc",
    },
    "heartgold": {
        "/root/msgdata/msg.narc": "/root/a/0/2/7",
        "/root/fielddata/encountdata/enc_data.narc": "/root/a/0/3/7",
        "/root/fielddata/eventdata/zone_event.narc": "/root/a/0/3/2",
        "/root/fielddata/script/scr_seq.narc": "/root/a/0/1/2",
        "/root/poketool/personal/evo.narc": "/root/a/0/3/4",
        "/root/poketool/personal/personal.narc": "/root/a/0/0/2",
        "/root/poketool/personal/wotbl.narc": "/root/a/0/3/3",
        "/root/poketool/trainer/trdata.narc": "/root/a/0/5/5",
        "/root/poketool/trainer/trpoke.narc": "/root/a/0/5/6",
        "/root/poketool/waza/waza_tbl.narc": "/root/a/0/1/1",
    },
}
filemaps["soulsilver"] = filemaps["heartgold"].copy()
filemaps["soulsilver"]["/root/fielddata/encountdata/enc_data.narc"] = "/root/a/1/3/6"

#XXX is this right?
filemaps["diamond_jp"] = filemaps["diamond"].copy()
filemaps["diamond_jp"]["/root/fielddata/script/scr_seq.narc"] = "/root/fielddata/script/scr_seq.narc"
filemaps["pearl_jp"] = filemaps["pearl"].copy()
filemaps["pearl_jp"]["/root/fielddata/script/scr_seq.narc"] = "/root/fielddata/script/scr_seq.narc"


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
        filemap=filemaps["diamond_jp"],
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x45,
        offsets=Offsets(0xEEDBC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
        filemap=filemaps["diamond"],
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x44,
        offsets=Offsets(0xEEDCC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
        filemap=filemaps["diamond"],
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x46,
        offsets=Offsets(0xEEDFC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
        filemap=filemaps["diamond"],
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x49,
        offsets=Offsets(0xEED70, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
        filemap=filemaps["diamond"],
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x53,
        offsets=Offsets(0xEEE08, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,615,614,560,559,555,None),
        filemap=filemaps["diamond"],
    ),
    ROMInfo(
        version="diamond",
        romname="Diamond",
        ID=0x44,
        lang=0x4B,
        offsets=Offsets(0xEA408, None, None),
        textnums=TextNums(
            376,557,546,342,577,357,608,606,609,603,602,560,559,555,None),#change tr
        filemap=filemaps["diamond"],
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
        filemap=filemaps["pearl_jp"],
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x45,
        offsets=Offsets(0xEEDBC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
        filemap=filemaps["pearl"],
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x44,
        offsets=Offsets(0xEEDCC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
        filemap=filemaps["pearl"],
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x46,
        offsets=Offsets(0xEEDFC, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
        filemap=filemaps["pearl"],
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x49,
        offsets=Offsets(0xEED70, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
        filemap=filemaps["pearl"],
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x53,
        offsets=Offsets(0xEEE08, None, None),
        textnums=TextNums(
            382,565,552,344,588,362,620,619,621,616,614,560,559,555,None),
        filemap=filemaps["pearl"],
    ),
    ROMInfo(
        version="pearl",
        romname="Pearl",
        ID=0x50,
        lang=0x4B,
        offsets=Offsets(0xEA408, None, None),
        textnums=TextNums(
            376,557,546,342,577,357,608,606,609,603,602,560,559,555,None),#change tr
        filemap=filemaps["pearl"],
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
        filemap=filemaps["platinum"],
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x45,
        offsets=Offsets(0xE601C, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,718,706,697,619,618,613,208),
        filemap=filemaps["platinum"],
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x46,
        offsets=Offsets(0xE60A4, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,719,706,697,619,618,613,208),
        filemap=filemaps["platinum"],
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x49,
        offsets=Offsets(0xE6038, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,721,706,697,619,618,613,208),
        filemap=filemaps["platinum"],
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x4A,
        offsets=Offsets(0xE56F0, 501, 1050),
        textnums=TextNums(
            427,616,604,390,636,408,696,694,698,693,685,619,618,613,207),#change tr
        filemap=filemaps["platinum"],
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x4B,
        offsets=Offsets(0xE6AA4, 501, 1050),
        textnums=TextNums(
            428,617,605,390,637,408,699,697,696,701,687,619,618,613,208),#change tr
        filemap=filemaps["platinum"],
    ),
    ROMInfo(
        version="platinum",
        romname="Platinum",
        ID=0x4C50,
        lang=0x53,
        offsets=Offsets(0xE60B0, 501, 1050),
        textnums=TextNums(
            433,624,610,392,647,412,709,707,722,706,697,619,618,613,208),
        filemap=filemaps["platinum"],
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
        filemap=filemaps["heartgold"],
    ),
    ROMInfo(
        version="heartgold",
        romname="Heart Gold",
        ID=0x4748,
        lang=0x45,
        offsets=Offsets(0xE56F0, 10000, 0),
        textnums=TextNums(
            279,735,720,222,750,237,814,812,803,823,802,730,729,None,207),#location names = 279?
        filemap=filemaps["heartgold"],
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
        filemap=filemaps["soulsilver"],
    ),
    ROMInfo(
        version="soulsilver",
        romname="Soul Silver",
        ID=0x5353,
        lang=0x45,
        offsets=Offsets(0xE56F0, 10000, 0),
        textnums=TextNums(
            279,735,720,222,750,237,814,812,803,823,802,730,729,None,207),
        filemap=filemaps["soulsilver"],
    ),
]

