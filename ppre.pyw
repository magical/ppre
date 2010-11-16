#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import os,sys
import array
import struct
import string
import ui_ppremain
import ui_pprepokeedit
import ui_ppremapedit
import ui_ppretmhmedit
import ui_ppremoveedit
import ui_ppreitemedit
import ui_ppreabilityedit
import ui_pprescripts
import ui_ppretredit
import ui_open
import texttopoke
import narc
import roms
import execute
import poketext
import romerror
import ascript as scripts
import locationindex
import bytereader
import unicodeparser
import subprocess
import cPickle as pickle

def readByte(a,i):
    return a[i]
def readUInt16(a,i):
    return (a[i]|(a[i+1]<<8))
def readUInt32(a,i):
    return (a[i]|(a[i+1]<<8)|(a[i+2]<<16)|(a[i+3]<<24))
def readInt32(a,i):
    temp=(a[i]|(a[i+1]<<8)|(a[i+2]<<16)|(a[i+3]<<24))
    if temp>>31==1:
        temp=temp-0x100000000
    return temp
def writeByte(a,i, val):
    a[i]=val&0xFF
def writeUInt16(a,i, val):
    a[i]=val&0xFF
    a[i+1]=(val>>8)&0xFF
def writeUInt32(a,i, val):
    a[i]=val&0xFF
    a[i+1]=(val>>8)&0xFF
    a[i+2]=(val>>16)&0xFF
    a[i+3]=(val>>24)&0xFF
def writeInt32(a,i, val):
    if val<0:
        val+=0x100000000
    a[i]=val&0xFF
    a[i+1]=(val>>8)&0xFF
    a[i+2]=(val>>16)&0xFF
    a[i+3]=(val>>24)&0xFF
class ScriptException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
class MainWindow(QMainWindow, ui_ppremain.Ui_MainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)
        self.updateUi()
        self.romname=""
        #print scripts.cmd
        #self.Of =(map table offset,invalid script begin, invalid script end,pl tutmoves ofset, types)
        #self.TN=(locations,type,ability,items,moves,pokenames,height,weight, description,flavor text,forms, class names, trainer names, trainer text
        #self.DT=Descriptive Text Nums
    def updateUi(self):
        self.nameLabel.text="ROM Name:"
    def createPatch(self):
        if not self.nameEdit.text():
            return romerror.noValue()
        if not self.patchNameEdit.text():
            return romerror.noValue()
        if not self.outputNameEdit.text():
            return romerror.noROM2Patch()
        self.statusbar.showMessage("Creating Patch....")
        if os.name == 'nt':
            subprocess.call(["xdelta"] + ["delta", str(self.nameEdit.text()), str(self.outputNameEdit.text()),str(self.patchNameEdit.text())])
        if os.name == "posix":
            os.system("wine xdelta.exe "+"delta "+str(self.nameEdit.text())+" "+str(self.outputNameEdit.text())+" "+str(self.patchNameEdit.text()))

        self.statusbar.showMessage("Patch '%s' has been created."%self.patchNameEdit.text(),3000)

    def applyPatch(self):
        if not self.nameEdit.text():
            return romerror.noValue()
        if not self.patchNameEdit.text():
            return romerror.noValue()
        if not self.outputNameEdit.text():
            return romerror.noValue()
        self.statusbar.showMessage("Creating Patch....")
        if os.name == 'nt':
            subprocess.call(["xdelta"] + ["delta", str(self.nameEdit.text()), str(self.outputNameEdit.text()),str(self.patchNameEdit.text())])
        if os.name == "posix":
            os.system("wine xdelta.exe "+"delta "+str(self.nameEdit.text())+" "+str(self.outputNameEdit.text())+" "+str(self.patchNameEdit.text()))

        self.statusbar.showMessage("Press Open ROM to load the new ROM.",4000)
        self.nameEdit.setText(self.outputNameEdit.text())
        self.outputNameEdit.setText("")
    def writeROM(self):
        if not self.outputNameEdit.text():
            return romerror.noROM2Write()
        if self.outputNameEdit.text()==self.nameEdit.text():
            if(QMessageBox.question(self, 'Message', "Are you sure want to write a ROM with the same name as the original ROM? This will make it very hard to patch.", QMessageBox.Yes, QMessageBox.No)==QMessageBox.Yes):
                self.statusbar.showMessage("Writing ROM....")
                self.rom.create(unicode(self.outputNameEdit.text()))
                self.statusbar.showMessage("Finished Writing ROM.",3000)
            else:
                return
        else:
            self.statusbar.showMessage("Writing ROM....")
            self.rom.create(unicode(self.outputNameEdit.text()))
            self.statusbar.showMessage("Finished Writing ROM.",3000)
    def openROM(self):
        if not self.nameEdit.text():
            return romerror.noROM()
        self.rom = execute.NDSFILES(unicode(self.nameEdit.text()))
        self.rom.dump()
        try:
            self.ID=getROMID()
        except IOError:
            romerror.noData(self)
            del(self.rom)
            return
        self.lang = getLang()
        self.other=("Pokemon Center", "Mart", "GYM")
        self.rominfo = roms.getInfo(self.ID, self.lang)

        # Backward compatibility
        self.romname = self.rominfo.romname
        self.Of = self.rominfo.offsets
        self.TN = self.rominfo.textnums
        self.DT = {"type": self.rominfo.textnums.types,
                   "move": self.rominfo.textnums.moves,
                   "contest": self.rominfo.textnums.contest}

        self.defMNIndex()
        """self.archive = ReadMsgNarc()
        binary=poketext.PokeTextData(self.archive.gmif.files[self.TN[0]])
        binary.decrypt()
        sf=QFile("locations.txt")
        sf.open(QIODevice.WriteOnly | QIODevice.Append)
        ts=QTextStream(sf)
        ts.setCodec("UTF-8")
        for i in range(0, len(binary.strlist)):
            ts<<binary.strlist[i]<<"\n"
        binary=poketext.PokeTextData(self.archive.gmif.files[self.TN[0]+1])
        binary.decrypt()
        for i in range(0, len(binary.strlist)):
            ts<<binary.strlist[i]<<"\n"
        binary=poketext.PokeTextData(self.archive.gmif.files[self.TN[0]+2])
        binary.decrypt()
        for i in range(0, len(binary.strlist)):
            ts<<binary.strlist[i]<<"\n"
        sf.close()"""
    def chooseROM(self):
        p=LoadDlg(self)
        p.exec_()
        return
    def openPokeEdit(self):
        if not mw.romname:
            return mw.loadFail()
        p=PokeEditDlg(self)
        p.exec_()
    def openMapEdit(self):
        if not mw.romname:
            return mw.loadFail()
        p=MapDlg(self)
        p.exec_()
    def openTmHmEdit(self):
        if not mw.romname:
            return mw.loadFail()
        p=TmHmDlg(self)
        p.exec_()
    def openMoveEdit(self):
        if not mw.romname:
            return mw.loadFail()
        p=MoveDlg(self)
        p.exec_()
    def openItemEdit(self):
        if not mw.romname:
            return mw.loadFail()
        p=ItemDlg(self)
        p.exec_()
    def openAbilityEdit(self):
        if not mw.romname:
            return mw.loadFail()
        p=AbilityDlg(self)
        p.exec_()
    def openScriptEdit(self):
        if not mw.romname:
            return mw.loadFail()
        p=ScriptDlg(self)
        p.exec_()
    def openTrEdit(self):
        if not mw.romname:
            return mw.loadFail()
        p=TrainerEditDlg(self)
        p.exec_()
    def defMNIndex(self):
        locationindex.index(self)
    def loadFail(self):
        QMessageBox.critical(self,"Critical","ROM has not been loaded. Please place your ROM in the same folder as PPRE, type in the name of your ROM (with '.nds'), and click 'Open ROM'.")
def getROMID():
    # The header starts out with the name of the game, so the ID is actually 
    # just the two characters after "POKEMON ".
    if not os.path.isfile(mw.rom.getFolder()+"/header.bin"):
        raise IOError
    filename = mw.rom.getFolder()+"/header.bin"
    fh=QFile(filename)
    fh.open(QIODevice.ReadOnly)
    ds=QDataStream(fh)
    ds.setByteOrder(QDataStream.LittleEndian)
    fh.seek(8)
    id=ds.readUInt16()
    fh.close()
    return id
def getLang():
    # Bytes 12-15 in the header are the serial number of the game, as assigned
    # by nintendo. The last character seems to indicate the language.
    filename = mw.rom.getFolder()+"/header.bin"
    fh=QFile(filename)
    fh.open(QIODevice.ReadOnly)
    ds=QDataStream(fh)
    ds.setByteOrder(QDataStream.LittleEndian)
    fh.seek(15)
    id=ds.readUInt16()&0xFF
    fh.close()
    return id
def ReadMapName():
    mapnamefilename=mw.rom.getFolder()+"/root/fielddata/maptable/mapname.bin"
    fh=QFile(mapnamefilename)
    fh.open(QIODevice.ReadOnly)
    size=fh.size()
    size/=0x10
    fh.close()
    filename = mw.rom.getFolder()+"/root/fielddata/maptable/mapname.bin"
    codenames=[]
    f = open(filename, "rb")
    for j in range(0, size):
        name=""
        for i in range(0, 16):
            ch= f.read(1)
            if ord(ch)!=0:
                name+=ch
        codenames.append(name)
    f.close()
    return codenames
def ReadMsgNarc():
    #print mw.ID
    if mw.ID== 0x5353 or mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/2/7"
    elif mw.ID== 0x4C50:
        filename = mw.rom.getFolder()+"/root/msgdata/pl_msg.narc"
    else:
        filename = mw.rom.getFolder()+"/root/msgdata/msg.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadPersonalNarc():
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/0/2"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/0/2"
    elif mw.ID== 0x4c50:
        filename = mw.rom.getFolder()+"/root/poketool/personal/pl_personal.narc"
    elif mw.ID == 0x44:
        filename = mw.rom.getFolder()+"/root/poketool/personal/personal.narc"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/personal_pearl/personal.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadTrNarc():
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/5/5"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/5/5"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/trainer/trdata.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadTrPokeNarc():
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/5/6"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/5/6"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/trainer/trpoke.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadWOTblNarc():
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/3/3"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/3/3"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/personal/wotbl.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadEvoNarc():
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/3/4"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/3/4"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/personal/evo.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadWazaNarc():
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/1/1"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/1/1"
    elif mw.ID==0x4C50:
        filename = mw.rom.getFolder()+"/root/poketool/waza/pl_waza_tbl.narc"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/waza/waza_tbl.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadEncNarc():
    if mw.ID==0x4C50:
        filename = mw.rom.getFolder()+"/root/fielddata/encountdata/pl_enc_data.narc"
    elif mw.ID==0x50:
        filename = mw.rom.getFolder()+"/root/fielddata/encountdata/p_enc_data.narc"
    elif mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/1/3/6"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/3/7"
    else:
        filename = mw.rom.getFolder()+"/root/fielddata/encountdata/d_enc_data.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadEventNarc():
    if mw.ID==0x4C50:
        filename = mw.rom.getFolder()+"/root/fielddata/eventdata/zone_event.narc"
    elif mw.ID in (0x5353,0x4748):
        filename = mw.rom.getFolder()+"/root/a/0/3/2"
    else:
        filename = mw.rom.getFolder()+"/root/fielddata/eventdata/zone_event_release.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def ReadScriptNarc():
    if mw.ID== 0x5353 or mw.ID==0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/1/2"
    elif mw.ID==0x4C50  or mw.lang==0x4A:
        filename = mw.rom.getFolder()+"/root/fielddata/script/scr_seq.narc"
    else:
        filename = mw.rom.getFolder()+"/root/fielddata/script/scr_seq_release.narc"
    f = open(filename, "rb")
    d = f.read()
    f.close()
    return narc.NARC(d)
def WriteScriptNarc(archive):
    if mw.ID== 0x5353 or mw.ID==0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/1/2"
    elif mw.ID==0x4C50 or mw.lang==0x4A:
        filename = mw.rom.getFolder()+"/root/fielddata/script/scr_seq.narc"
    else:
        filename = mw.rom.getFolder()+"/root/fielddata/script/scr_seq_release.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
def WriteEncNarc(archive):
    if mw.ID==0x4C50:
        filename = mw.rom.getFolder()+"/root/fielddata/encountdata/pl_enc_data.narc"
    elif mw.ID==0x50:
        filename = mw.rom.getFolder()+"/root/fielddata/encountdata/p_enc_data.narc"
    elif mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/1/3/6"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/3/7"
    else:
        filename = mw.rom.getFolder()+"/root/fielddata/encountdata/d_enc_data.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
def WriteEventNarc(archive):
    if mw.ID==0x4C50:
        filename = mw.rom.getFolder()+"/root/fielddata/eventdata/zone_event.narc"
    elif mw.ID in (0x5353,0x4748):
        filename = mw.rom.getFolder()+"/root/a/0/3/2"
    else:
        filename = mw.rom.getFolder()+"/root/fielddata/eventdata/zone_event_release.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
def WriteWOTblNarc(archive):
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/3/3"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/3/3"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/personal/wotbl.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
def WriteMsgNarc(archive):
    if mw.ID== 0x5353 or mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/2/7"
    elif mw.ID== 0x4C50:
        filename = mw.rom.getFolder()+"/root/msgdata/pl_msg.narc"
    else:
        filename = mw.rom.getFolder()+"/root/msgdata/msg.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
def WriteTrNarc(archive):
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/5/5"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/5/5"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/trainer/trdata.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
def WriteTrPokeNarc(archive):
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/5/6"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/5/6"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/trainer/trpoke.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
def WriteEvoNarc(archive):
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/3/4"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/3/4"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/personal/evo.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
def WritePersonalNarc(archive):
    if mw.ID== 0x5353:
        filename = mw.rom.getFolder()+"/root/a/0/0/2"
    elif mw.ID== 0x4748:
        filename = mw.rom.getFolder()+"/root/a/0/0/2"
    elif mw.ID== 0x4c50:
        filename = mw.rom.getFolder()+"/root/poketool/personal/pl_personal.narc"
    elif mw.ID == 0x44:
        filename = mw.rom.getFolder()+"/root/poketool/personal/personal.narc"
    else:
        filename = mw.rom.getFolder()+"/root/poketool/personal_pearl/personal.narc"
    f = open(filename, "wb")
    archive.ToFile(f)
    f.close()
class PokeEditDlg(QDialog, ui_pprepokeedit.Ui_PokeEditDlg):
    def __init__(self,parent=None):
        super(PokeEditDlg,self).__init__(parent)
        self.setupUi(self)
        self.personal = ReadPersonalNarc()
        self.archive = ReadMsgNarc()
        self.moves = ReadWOTblNarc()
        self.evos = ReadEvoNarc()
        self.temp = [0] * 82
        self.dataids = []

        self.tmlist = [getattr(self, "tm" + str(i+1)) for i in range(92)]
        self.hmlist = [getattr(self, "hm" + str(i+1)) for i in range(8)]
        self.movelist = [getattr(self, "move" + str(i + 1)) for i in range(10)]
        self.movelvllist = [getattr(self, "moveLvl" + str(i + 1)) for i in range(10)]
        self.evotypes = [getattr(self, "evoType" + str(i + 1)) for i in range(7)]
        self.evopkms = [getattr(self, "evoPkm" + str(i + 1)) for i in range(7)]

        for i, tm in enumerate(self.tmlist):
            tm.setText(tm.text() + str(i + 1))

        binary=poketext.PokeTextData(self.archive.gmif.files[mw.TN[1]])
        binary.decrypt()
        self.type1.addItems(binary.strlist)
        self.type2.addItems(binary.strlist)

        binary=poketext.PokeTextData(self.archive.gmif.files[mw.TN[2]])
        binary.decrypt()
        self.ability1.addItems(binary.strlist)
        self.ability2.addItems(binary.strlist)

        binary=poketext.PokeTextData(self.archive.gmif.files[mw.TN[3]])
        binary.decrypt()
        self.heldItem1.addItems(binary.strlist)
        self.heldItem2.addItems(binary.strlist)
        self.evoItem1.addItems(binary.strlist)
        self.evoItem2.addItems(binary.strlist)
        self.evoItem3.addItems(binary.strlist)
        self.evoItem4.addItems(binary.strlist)
        self.evoItem5.addItems(binary.strlist)
        self.evoItem6.addItems(binary.strlist)
        self.evoItem7.addItems(binary.strlist)

        binary=poketext.PokeTextData(self.archive.gmif.files[mw.TN[4]])
        binary.decrypt()
        for move in self.movelist:
            move.addItems(binary.strlist)
        self.evoAtk1.addItems(binary.strlist)
        self.evoAtk2.addItems(binary.strlist)
        self.evoAtk3.addItems(binary.strlist)
        self.evoAtk4.addItems(binary.strlist)
        self.evoAtk5.addItems(binary.strlist)
        self.evoAtk6.addItems(binary.strlist)
        self.evoAtk7.addItems(binary.strlist)

        binary=poketext.PokeTextData(self.archive.gmif.files[mw.TN[5]])
        binary.decrypt()
        self.choosePokemon.addItems(binary.strlist)
        for evoPkm in self.evopkms:
            evoPkm.addItems(binary.strlist)
        self.evoReqPkm1.addItems(binary.strlist)
        self.evoReqPkm2.addItems(binary.strlist)
        self.evoReqPkm3.addItems(binary.strlist)
        self.evoReqPkm4.addItems(binary.strlist)
        self.evoReqPkm5.addItems(binary.strlist)
        self.evoReqPkm6.addItems(binary.strlist)
        self.evoReqPkm7.addItems(binary.strlist)

        self.romname=self.romnameLabel.text()+mw.romname
        self.romnameLabel.setText(self.romname)
        self.choosePokemon.setCurrentIndex(0)
        #self.updateUi()
    def changedPokemon(self,event):
        self.pokeid=self.choosePokemon.currentIndex()
        self.pokeName.setText(self.choosePokemon.currentText())
        if self.pokeid < 494:
            temptext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[6]])
            temptext.decrypt()
            self.height.setText(temptext.strlist[self.pokeid].replace("\\x01E2","").replace("\\x0001", ""))
            temptext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[7]])
            temptext.decrypt()
            self.weight.setText(temptext.strlist[self.pokeid].replace("\\x01E2","").replace("\\x0001", ""))
            temptext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[8]])
            temptext.decrypt()
            self.description.setText(temptext.strlist[self.pokeid])
            temptext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[9]])
            temptext.decrypt()
            self.flavorText.setPlainText(temptext.strlist[self.pokeid])
        self.chooseForm.clear()
        formtext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[10]])
        formtext.decrypt()
        if mw.ID == 0x5353 or mw.ID==0x4748:
            if self.pokeid == 386:
                self.dataids=[self.pokeid,496,497,498]
                self.chooseForm.addItem(formtext.strlist[145])
                self.chooseForm.addItem(formtext.strlist[146])
                self.chooseForm.addItem(formtext.strlist[147])
                self.chooseForm.addItem(formtext.strlist[148])
            elif self.pokeid == 413:
                self.dataids=[self.pokeid,499,500]
                self.chooseForm.addItem(formtext.strlist[118])
                self.chooseForm.addItem(formtext.strlist[119])
                self.chooseForm.addItem(formtext.strlist[120])
            elif self.pokeid == 479:
                self.dataids=[self.pokeid,503,504,505,506,507]
                self.chooseForm.addItem(formtext.strlist[153])
                self.chooseForm.addItem(formtext.strlist[154])
                self.chooseForm.addItem(formtext.strlist[155])
                self.chooseForm.addItem(formtext.strlist[156])
                self.chooseForm.addItem(formtext.strlist[157])
                self.chooseForm.addItem(formtext.strlist[158])
            elif self.pokeid == 487:
                self.dataids=[self.pokeid,501]
                self.chooseForm.addItem(formtext.strlist[151])
                self.chooseForm.addItem(formtext.strlist[152])
            elif self.pokeid == 492:
                self.dataids=[self.pokeid,502]
                self.chooseForm.addItem(formtext.strlist[149])
                self.chooseForm.addItem(formtext.strlist[150])
            else:
                self.dataids=[self.pokeid]
                self.chooseForm.addItem("")
        elif mw.ID == 0x4C50:
            if self.pokeid == 386:
                self.dataids=[self.pokeid,496,497,498]
                self.chooseForm.addItem(formtext.strlist[111])
                self.chooseForm.addItem(formtext.strlist[112])
                self.chooseForm.addItem(formtext.strlist[113])
                self.chooseForm.addItem(formtext.strlist[114])
            elif self.pokeid == 413:
                self.dataids=[self.pokeid,499,500]
                self.chooseForm.addItem(formtext.strlist[17])
                self.chooseForm.addItem(formtext.strlist[18])
                self.chooseForm.addItem(formtext.strlist[19])
            elif self.pokeid == 479:
                self.dataids=[self.pokeid,503,504,505,506,507]
                self.chooseForm.addItem(formtext.strlist[119])
                self.chooseForm.addItem(formtext.strlist[120])
                self.chooseForm.addItem(formtext.strlist[121])
                self.chooseForm.addItem(formtext.strlist[122])
                self.chooseForm.addItem(formtext.strlist[123])
                self.chooseForm.addItem(formtext.strlist[124])
            elif self.pokeid == 487:
                self.dataids=[self.pokeid,501]
                self.chooseForm.addItem(formtext.strlist[117])
                self.chooseForm.addItem(formtext.strlist[118])
            elif self.pokeid == 492:
                self.dataids=[self.pokeid,502]
                self.chooseForm.addItem(formtext.strlist[115])
                self.chooseForm.addItem(formtext.strlist[116])
            else:
                self.dataids=[self.pokeid]
                self.chooseForm.addItem("")
        else:
            if self.pokeid == 386:
                self.dataids=[self.pokeid,496,497,498]
                self.chooseForm.addItem(formtext.strlist[110])
                self.chooseForm.addItem(formtext.strlist[111])
                self.chooseForm.addItem(formtext.strlist[112])
                self.chooseForm.addItem(formtext.strlist[113])
            elif self.pokeid == 413:
                self.dataids=[self.pokeid,499,500]
                self.chooseForm.addItem(formtext.strlist[17])
                self.chooseForm.addItem(formtext.strlist[18])
                self.chooseForm.addItem(formtext.strlist[19])
            else:
                self.dataids=[self.pokeid]
                self.chooseForm.addItem("")
    def changedForm(self,event):
        file=self.personal.gmif.files[self.dataids[self.chooseForm.currentIndex()]]
        self.temp[0]=ord(file[0])
        self.temp[1]=ord(file[1])
        self.temp[2]=ord(file[2])
        self.temp[3]=ord(file[3])
        self.temp[4]=ord(file[4])
        self.temp[5]=ord(file[5])
        self.temp[6]=ord(file[6])
        self.temp[7]=ord(file[7])
        self.temp[8]=ord(file[8])
        self.temp[9]=ord(file[9])
        self.temp[10]=ord(file[10])&3
        self.temp[11]=(ord(file[10])&0xC)>>2
        self.temp[12]=(ord(file[10])&0x30)>>4
        self.temp[13]=(ord(file[10])&0xC0)>>6
        self.temp[14]=ord(file[11])&0x3
        self.temp[15]=(ord(file[11])&0xC)>>2
        self.temp[16]=ord(file[12])|(ord(file[13])<<8)
        self.temp[17]=ord(file[14])|(ord(file[15])<<8)
        self.temp[18]=ord(file[16])
        self.temp[19]=ord(file[17])
        self.temp[20]=ord(file[18])
        self.temp[21]=ord(file[19])
        self.temp[22]=ord(file[20])-1
        self.temp[23]=ord(file[21])-1
        self.temp[24]=ord(file[22])
        self.temp[25]=ord(file[23])
        self.temp[26]=ord(file[24])
        self.temp[27]=ord(file[25])
        self.temp[28]=ord(file[28])
        self.temp[29]=ord(file[29])
        self.temp[30]=ord(file[30])
        self.temp[31]=ord(file[31])
        self.temp[32]=ord(file[32])
        self.temp[33]=ord(file[33])
        self.temp[34]=ord(file[34])
        self.temp[35]=ord(file[35])
        self.temp[36]=ord(file[36])
        self.temp[37]=ord(file[37])
        self.temp[38]=ord(file[38])
        self.temp[39]=ord(file[39])
        self.temp[40]=ord(file[40])
        #Start Moveset
        self.reachedFFFF=False
        self.nummoves=0
        file=self.moves.gmif.files[self.dataids[self.chooseForm.currentIndex()]]
        cF = 0
        cT = 41
        cN = 0
        for t in range(0,20):
            if not self.reachedFFFF:
                temp1=ord(file[cF])|(ord(file[cF+1])<<8)
                if temp1==0xFFFF:
                    self.reachedFFFF=True
                    self.temp[cT]=0
                    self.nummoves=cN
                else:
                    self.temp[cT]=temp1
            else:
                self.temp[cT]=0
            cF += 2
            cN += 1
            cT += 1
        #Start Evo
        file=self.evos.gmif.files[self.dataids[self.chooseForm.currentIndex()]]
        self.temp[61]=ord(file[0])|(ord(file[1])<<8)
        self.temp[62]=ord(file[2])|(ord(file[3])<<8)
        self.temp[63]=ord(file[4])|(ord(file[5])<<8)
        self.temp[64]=ord(file[6])|(ord(file[7])<<8)
        self.temp[65]=ord(file[8])|(ord(file[9])<<8)
        self.temp[66]=ord(file[10])|(ord(file[11])<<8)
        self.temp[67]=ord(file[12])|(ord(file[13])<<8)
        self.temp[68]=ord(file[14])|(ord(file[15])<<8)
        self.temp[69]=ord(file[16])|(ord(file[17])<<8)
        self.temp[70]=ord(file[18])|(ord(file[19])<<8)
        self.temp[71]=ord(file[20])|(ord(file[21])<<8)
        self.temp[72]=ord(file[22])|(ord(file[23])<<8)
        self.temp[73]=ord(file[24])|(ord(file[25])<<8)
        self.temp[74]=ord(file[26])|(ord(file[27])<<8)
        self.temp[75]=ord(file[28])|(ord(file[29])<<8)
        self.temp[76]=ord(file[30])|(ord(file[31])<<8)
        self.temp[77]=ord(file[32])|(ord(file[33])<<8)
        self.temp[78]=ord(file[34])|(ord(file[35])<<8)
        self.temp[79]=ord(file[36])|(ord(file[37])<<8)
        self.temp[80]=ord(file[38])|(ord(file[39])<<8)
        self.temp[81]=ord(file[40])|(ord(file[41])<<8)
        self.evoparams=(self.temp[62],self.temp[65],self.temp[68],self.temp[71],self.temp[74],self.temp[77],self.temp[80])
        #UpdateUi
        self.updateUi()
    def savePokemon(self):
        if self.dataids[self.chooseForm.currentIndex()] < 1:
            print "No Pokemon Selected"
            return
        writer = bytereader.byteWriter()
        stats = ["hp","atk","def","spd","spatk","spdef"]
        for s in stats:
            eval("writer.WriteByte(self."+s+"spinBox.value())")
        writer.WriteByte(self.type1.currentIndex())
        writer.WriteByte(self.type2.currentIndex())
        writer.WriteByte(self.catchRate.value())
        writer.WriteByte(self.baseExp.value())
        ev = 0
        e = 0
        for s in stats:
            ev += (eval("self."+s+"Evs.value()")&3) << e
            e += 2
        writer.WriteUInt16(ev)
        writer.WriteUInt16(self.heldItem1.currentIndex())
        writer.WriteUInt16(self.heldItem2.currentIndex())
        writer.WriteByte(self.genderVal.value())
        writer.WriteByte(self.stepsMultiplier.value())
        writer.WriteByte(self.baseHappiness.value())
        writer.WriteByte(self.maxExp.currentIndex())
        writer.WriteByte(self.eggGroup1.currentIndex()+1)
        writer.WriteByte(self.eggGroup2.currentIndex()+1)
        writer.WriteByte(self.ability1.currentIndex())
        writer.WriteByte(self.ability2.currentIndex())
        writer.WriteByte(self.runChance.value())
        writer.WriteByte(self.colorVal.value())
        writer.WriteUInt16(0)
        tmByte = []
        b = 1
        tmB = "tm"
        e = 0
        broke = False
        byte = 0
        for i in range(0,13):
            for j in range(0,8):
                if (b+j) == 93:
                    b = -7
                    tmB = "hm"
                    broke = True
                    break
                #print tmB+str(b+j)
                byte += (eval("self."+tmB+str(b+j)+".isChecked()") << e)
                if (b+j) == 8 and tmB == "hm":
                    break
                e += 1
            b += 8
            if broke:
                broke = False
                continue
            e = 0
            #print byte
            if byte > 255:
                writer.WriteUInt16(byte)
            else:
                writer.WriteByte(byte)
            byte = 0
        while len(writer.ReturnData()) < 44:
            writer.WriteByte(0)
        wPoke = ""
        for w in writer.ReturnData():
            wPoke+=chr(int(w))
        self.personal.replaceFile(self.dataids[self.chooseForm.currentIndex()], wPoke)
        WritePersonalNarc(self.personal)
        print "Saved Personal NARC"
        self.saveEvo()
        self.saveMoves()
        print "Saving Text... ",
        temptext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[6]])
        temptext.decrypt()
        temptext.strlist[self.pokeid] = unicode(self.height.text())
        p=texttopoke.Makefile(temptext.strlist)
        encrypt = poketext.PokeTextData(p)
        encrypt.SetKey(0xD00E)
        encrypt.encrypt()
        self.archive.replaceFile(mw.TN[6], encrypt.getStr())
        print "Height",
        temptext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[7]])
        temptext.decrypt()
        temptext.strlist[self.pokeid] = unicode(self.weight.text())
        p=texttopoke.Makefile(temptext.strlist)
        encrypt = poketext.PokeTextData(p)
        encrypt.SetKey(0xD00E)
        encrypt.encrypt()
        self.archive.replaceFile(mw.TN[7], encrypt.getStr())
        print "Weight",
        temptext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[8]])
        temptext.decrypt()
        temptext.strlist[self.pokeid] = unicode(self.description.text())
        p=texttopoke.Makefile(temptext.strlist)
        encrypt = poketext.PokeTextData(p)
        encrypt.SetKey(0xD00E)
        encrypt.encrypt()
        self.archive.replaceFile(mw.TN[8], encrypt.getStr())
        print "Description",
        temptext=poketext.PokeTextData(self.archive.gmif.files[mw.TN[9]])
        temptext.decrypt()
        temptext.strlist[self.pokeid] = unicode(self.flavorText.toPlainText().replace("\n","\\n"))
        p=texttopoke.Makefile(temptext.strlist)
        encrypt = poketext.PokeTextData(p)
        encrypt.SetKey(0xD00E)
        encrypt.encrypt()
        self.archive.replaceFile(mw.TN[9], encrypt.getStr())
        print "Flavor Text"
        WriteMsgNarc(self.archive)
        print "Saved Text NARC"

        return
    def saveMoves(self):
        reachedFFFF = False
        writer = bytereader.byteWriter()
        for m in range(1,21):
            lvl = 0
            move = 0
            lvl = getattr(self, 'moveLvl' + str(m)).value()
            move = getattr(self, 'move' + str(m)).currentIndex()
            byte = ((lvl << 9)|move)
            if byte == 0:
                reachedFFFF = True
            if not reachedFFFF:
                writer.WriteUInt16(byte)
            else:
                writer.WriteUInt16(0xFFFF)
                break
        wPoke = ""
        for w in writer.ReturnData():
            wPoke+=chr(int(w))
        self.moves.replaceFile(self.dataids[self.chooseForm.currentIndex()], wPoke)
        WriteWOTblNarc(self.moves)
        print "Saved Moveset NARC"
    def saveEvo(self):
        writer = bytereader.byteWriter()
        for i in range(1,8):
            evo = getattr(self, 'evoType'+str(i)).currentIndex()
            param = 0
            if evo in (4,8,9,10,11,12,13,14,21,22):
                param = getattr(self, 'evoLvl'+str(i)).value()
            elif evo in (6,7,16,17,18,19):
                param = getattr(self, 'evoItem' + str(i)).currentIndex()
            elif evo==0x14:
                param = getattr(self, 'evoAtk' + str(i)).currentIndex()
            elif evo==0x15:
                param = getattr(self, 'evoReqPkm' + str(i)).currentIndex()
            poke = getattr(self, 'evoPkm' + str(i)).currentIndex()
            writer.WriteUInt16(evo)
            writer.WriteUInt16(param)
            writer.WriteUInt16(poke)
        while len(writer.ReturnData()) < 44:
            writer.WriteByte(0)
        wPoke = ""
        for w in writer.ReturnData():
            wPoke+=chr(int(w))
        self.evos.replaceFile(self.dataids[self.chooseForm.currentIndex()], wPoke)
        WriteEvoNarc(self.evos)
        print "Saved Evolution NARC"
    def updateUi(self):
        self.hpspinBox.setValue(self.temp[0])
        self.atkspinBox.setValue(self.temp[1])
        self.defspinBox.setValue(self.temp[2])
        self.spdspinBox.setValue(self.temp[3])
        self.spatkspinBox.setValue(self.temp[4])
        self.spdefspinBox.setValue(self.temp[5])
        self.type1.setCurrentIndex(self.temp[6])
        self.type2.setCurrentIndex(self.temp[7])
        self.catchRate.setValue(self.temp[8])
        self.baseExp.setValue(self.temp[9])
        self.hpEvs.setValue(self.temp[10])
        self.atkEvs.setValue(self.temp[11])
        self.defEvs.setValue(self.temp[12])
        self.spdEvs.setValue(self.temp[13])
        self.spatkEvs.setValue(self.temp[14])
        self.spdefEvs.setValue(self.temp[15])
        self.heldItem1.setCurrentIndex(self.temp[16])
        self.heldItem2.setCurrentIndex(self.temp[17])
        self.genderVal.setValue(self.temp[18])
        self.stepsMultiplier.setValue(self.temp[19])
        self.baseHappiness.setValue(self.temp[20])
        self.maxExp.setCurrentIndex(self.temp[21])
        self.eggGroup1.setCurrentIndex(self.temp[22])
        self.eggGroup2.setCurrentIndex(self.temp[23])
        self.ability1.setCurrentIndex(self.temp[24])
        self.ability2.setCurrentIndex(self.temp[25])
        self.runChance.setValue(self.temp[26])
        self.colorVal.setValue(self.temp[27])
        for i, tm in enumerate(self.tmlist):
            self.checkBoxHandle(tm, (self.temp[28 + (i // 8)] >> (i % 8)) & 1)
        self.checkBoxHandle(self.hm1,(self.temp[39]>>4)&1)
        self.checkBoxHandle(self.hm2,(self.temp[39]>>5)&1)
        self.checkBoxHandle(self.hm3,(self.temp[39]>>6)&1)
        self.checkBoxHandle(self.hm4,(self.temp[39]>>7)&1)
        self.checkBoxHandle(self.hm5,(self.temp[40])&1)
        self.checkBoxHandle(self.hm6,(self.temp[40]>>1)&1)
        self.checkBoxHandle(self.hm7,(self.temp[40]>>2)&1)
        self.checkBoxHandle(self.hm8,(self.temp[40]>>3)&1)
        for i, moveLvl in enumerate(self.movelvllist):
            moveLvl.setValue(self.temp[41 + i] >> 9)
        for i, move in enumerate(self.movelist):
            move.setCurrentIndex(self.temp[41 + i] & 0x1ff)

        evoreqs = ["evoAtk","evoItem","evoLvl","evoReqPkm"]
        for e in evoreqs:
            for i in range(1,8):
                getattr(self, e + str(i)).setEnabled(False)

        self.evoType1.setCurrentIndex(self.temp[61])
        if self.temp[61] in (4,8,9,10,11,12,13,14,21,22):
            self.evoLvl1.setEnabled(True)
            self.evoLvl1.setValue(self.temp[62])
        elif self.temp[61] in (6,7,16,17,18,19):
            self.evoItem1.setEnabled(True)
            self.evoItem1.setCurrentIndex(self.temp[62])
        elif self.temp[61]==0x14:
            self.evoAtk1.setEnabled(True)
            self.evoAtk1.setCurrentIndex(self.temp[62])
        elif self.temp[61]==0x15:
            self.evoReqPkm1.setEnabled(True)
            self.evoReqPkm1.setCurrentIndex(self.temp[62])
        self.evoPkm1.setCurrentIndex(self.temp[63])
        self.evoType2.setCurrentIndex(self.temp[64])
        if self.temp[64] in (4,8,9,10,11,12,13,14,21,22):
            self.evoLvl2.setEnabled(True)
            self.evoLvl2.setValue(self.temp[65])
        elif self.temp[64] in (6,7,16,17,18,19):
            self.evoItem2.setEnabled(True)
            self.evoItem2.setCurrentIndex(self.temp[65])
        elif self.temp[64]==0x14:
            self.evoAtk2.setEnabled(True)
            self.evoAtk2.setCurrentIndex(self.temp[65])
        elif self.temp[64]==0x15:
            self.evoReqPkm2.setEnabled(True)
            self.evoReqPkm2.setCurrentIndex(self.temp[65])
        self.evoPkm2.setCurrentIndex(self.temp[66])
        self.evoType3.setCurrentIndex(self.temp[67])
        if self.temp[67] in (4,8,9,10,11,12,13,14,21,22):
            self.evoLvl3.setEnabled(True)
            self.evoLvl3.setValue(self.temp[68])
        elif self.temp[67] in (6,7,16,17,18,19):
            self.evoItem3.setEnabled(True)
            self.evoItem3.setCurrentIndex(self.temp[68])
        elif self.temp[67]==0x14:
            self.evoAtk3.setEnabled(True)
            self.evoAtk3.setCurrentIndex(self.temp[68])
        elif self.temp[67]==0x15:
            self.evoReqPkm3.setEnabled(True)
            self.evoReqPkm3.setCurrentIndex(self.temp[68])
        self.evoPkm3.setCurrentIndex(self.temp[69])
        self.evoType4.setCurrentIndex(self.temp[70])
        if self.temp[70] in (4,8,9,10,11,12,13,14,21,22):
            self.evoLvl4.setEnabled(True)
            self.evoLvl4.setValue(self.temp[71])
        elif self.temp[70] in (6,7,16,17,18,19):
            self.evoItem4.setEnabled(True)
            self.evoItem4.setCurrentIndex(self.temp[71])
        elif self.temp[70]==0x14:
            self.evoAtk4.setEnabled(True)
            self.evoAtk4.setCurrentIndex(self.temp[71])
        elif self.temp[70]==0x15:
            self.evoReqPkm4.setEnabled(True)
            self.evoReqPkm4.setCurrentIndex(self.temp[71])
        self.evoPkm4.setCurrentIndex(self.temp[72])
        self.evoType5.setCurrentIndex(self.temp[73])
        if self.temp[73] in (4,8,9,10,11,12,13,14,21,22):
            self.evoLvl5.setEnabled(True)
            self.evoLvl5.setValue(self.temp[74])
        elif self.temp[73] in (6,7,16,17,18,19):
            self.evoItem5.setEnabled(True)
            self.evoItem5.setCurrentIndex(self.temp[74])
        elif self.temp[73]==0x14:
            self.evoAtk5.setEnabled(True)
            self.evoAtk5.setCurrentIndex(self.temp[74])
        elif self.temp[73]==0x15:
            self.evoReqPkm5.setEnabled(True)
            self.evoReqPkm5.setCurrentIndex(self.temp[74])
        self.evoPkm5.setCurrentIndex(self.temp[75])
        self.evoType6.setCurrentIndex(self.temp[76])
        if self.temp[76] in (4,8,9,10,11,12,13,14,21,22):
            self.evoLvl6.setEnabled(True)
            self.evoLvl6.setValue(self.temp[77])
        elif self.temp[76] in (6,7,16,17,18,19):
            self.evoItem6.setEnabled(True)
            self.evoItem6.setCurrentIndex(self.temp[77])
        elif self.temp[76]==0x14:
            self.evoAtk6.setEnabled(True)
            self.evoAtk6.setCurrentIndex(self.temp[77])
        elif self.temp[76]==0x15:
            self.evoReqPkm6.setEnabled(True)
            self.evoReqPkm6.setCurrentIndex(self.temp[77])
        self.evoPkm6.setCurrentIndex(self.temp[78])
        self.evoType7.setCurrentIndex(self.temp[79])
        if self.temp[79] in (4,8,9,10,11,12,13,14,21,22):
            self.evoLvl7.setEnabled(True)
            self.evoLvl7.setValue(self.temp[80])
        elif self.temp[79] in (6,7,16,17,18,19):
            self.evoItem7.setEnabled(True)
            self.evoItem7.setCurrentIndex(self.temp[80])
        elif self.temp[79]==0x14:
            self.evoAtk7.setEnabled(True)
            self.evoAtk7.setCurrentIndex(self.temp[80])
        elif self.temp[79]==0x15:
            self.evoReqPkm7.setEnabled(True)
            self.evoReqPkm7.setCurrentIndex(self.temp[80])
        self.evoPkm7.setCurrentIndex(self.temp[81])
    def checkBoxHandle(self,checkbox, bit):
        if bit == 0:
            checkbox.setCheckState(Qt.Unchecked)
        else:
            checkbox.setCheckState(Qt.Checked)
    def updatehp(self,event=""):
        self.temp[0]=self.hpspinBox.value
    def updateatk(self,event=""):
        self.temp[1]=self.atkspinBox.value
    def updatedef(self,event=""):
        self.temp[2]=self.defspinBox.value
    def updatespd(self,event=""):
        self.temp[3]=self.spdspinBox.value
    def updatespatk(self,event=""):
        self.temp[4]=self.spatkspinBox.value
    def updatespdef(self,event=""):
        self.temp[5]=self.spdefspinBox.value
    def getOffset(self, natid,form):
        r0=form
        r4=natid
        r2=natid

        r1=0x1DF
        if r4 > r1:
            r3=r1
            r3+=8
            if r4>r3:
                r3=r1
                r3+=0xD
                if r4==r3:
                    if r0==1:
                        r2=r1
                        r2+=0x15
            else:
                r3=r1
                r3+=8
                if r4==r3:
                    if r0==1:
                        r2=r1
                        r2+=0x14
        elif r4==r1:
            if r0==1:
                r2=r1
                r2+=0x16
            elif r0==2:
                r2=r1
                r2+=0x17
            elif r0==3:
                r2=r1
                r2+=0x18
            elif r0==4:
                r2=r1
                r2+=0x19
            elif r0==5:
                r2=r1
                r2+=0x1A
        else:
            r3=r1+0
            r3-=0x5D
            if r4>r3:
                r3=r1
                r3-=0x42
                if r4==r3:
                    if r0==1:
                        r2=r1
                        r2+=0x12
                    elif r0==2:
                        r2=r1
                    r2+=0x13
            else:
                r3=r1
                r3-=0x5D
                if r3==r4:
                    if r0==1:
                        r2=r1
                        r2+=0xF
                    elif r0==2:
                        r2=r1
                        r2+=0x10
                    elif r0==3:
                        r2=r1
                        r2+=0x11
        r1=r2-1
        r0=r1<<2
        r1=r1+r0
        return r1
class MapDlg(QDialog, ui_ppremapedit.Ui_mapDlg):
    def __init__(self,parent=None):
        super(MapDlg,self).__init__(parent)
        if mw.ID== 0x5353 or mw.ID== 0x4748:
            self.setupUi_gs(self)
        else:
            self.setupUi(self)
        self.ID = mw.ID
        self.tmpFolder = mw.rom.getFolder()
        #for i in range(1,3):
        #   eval("self.rockSmash"+str(i)+".setStyleSheet('background-color:#ff0000;')")
        self.loading=True
        self.navMode = False
        self.scriptNarc=ReadScriptNarc()
        self.msgNarc=ReadMsgNarc()
        self.encNarc=ReadEncNarc()
        self.eventNarc=ReadEventNarc()
        self.scriptTabs = {}
        self.iToName=[]
        self.mapNames=[]
        self.uMapNames=[]
        self.nameToI=[]
        try:
            mapfile = open(mw.rom.getFolder()+"/mapinfo.bin","r")
            mapinfo = pickle.load(mapfile)
            self.mapNames = mapinfo["mapnames"]
            self.iToName = mapinfo["iToName"]
            self.nameToI = mapinfo["nameToI"]
            self.codes = mapinfo["codes"]
            self.size=len(self.codes)
            mapfile.close()
        except:
            self.codes=ReadMapName()
            self.size=len(self.codes)
            for i in range(0,self.size):
                name=self.getDescriptiveName(self.codes[i])
                """if "Pokemon Center" in name and "Floor" not in name:
                    print "<tr><td>%s</td><td>%s</td></tr>" % (name,i)"""
                self.uMapNames.append(name)
                self.mapNames.append(name)
            self.mapNames.sort()
            for i in range(0,  self.size):
                self.nameToI.append(0)
                self.iToName.append(0)
            for i in range(0,  self.size):
                for j in range(0, self.size):
                    if self.mapNames[i]==self.uMapNames[j]:
                        self.nameToI[i]=j
                        self.iToName[j]=i
            mapfile = open(mw.rom.getFolder()+"/mapinfo.bin","w")
            mapinfo = {"mapnames":self.mapNames,"iToName":self.iToName,"nameToI":self.nameToI,"codes":self.codes}
            pickle.dump(mapinfo,mapfile)
            mapfile.close()
        self.chooseMapName.addItems(self.mapNames)
        for i in range(0,self.size):
            self.chooseMap.addItem(unicode(i))
        self.scr = scripts.script(self)
        self.setupEncUi()
        self.chooseMapName.setCurrentIndex(self.iToName[0])
        self.setupEvent()
        self.navScript.setExpandsOnDoubleClick(False)
        self.navFunc.setExpandsOnDoubleClick(False)
        self.navMov.setExpandsOnDoubleClick(False)
        self.updateNav.setText("Update Navigator")
        self.tabWidget.removeTab(3)
        self.mapTab.setCurrentIndex(3)
        del(self.variableTab)
        self.loading=False

    def updateIndex(self, n):
        if not self.loading:
            self.chooseMap.setCurrentIndex(self.nameToI[self.chooseMapName.currentIndex()])
    def navigatorMode(self,flag):
        for tab in self.scriptTabs:
            for t in self.scriptTabs[tab]:
                t[1].setReadOnly(flag)
        self.navMode = flag
    def compile(self):
        # compile the scripts now...
        self.scr.parseNavigation()
        #scripts.compile(self)
        return
    def dump(self):
        self.scr.readScript()
        QtCore.QMetaObject.connectSlotsByName(self)
        return
    def addScript(self):
        # add a new script + tab to the ui
        self.appendTab("scr")
        c = len(self.scriptTabs["scr"])
        self.scriptOrdList.addItem("Script %i"%c)
    def appendTab(self,tab):
        self.tabnames = {
"scr":[self.scriptTabWidget],
"func":[self.funcTabWidget],
"mov":[self.movTabWidget]}
        c = len(self.scriptTabs[tab])
        self.scriptTabs[tab].append([])
        self.scriptTabs[tab][c].append(QtGui.QWidget())
        self.scriptTabs[tab][c][0].setObjectName("%s_tab_%i"%(tab,c))
        self.scriptTabs[tab][c].append(QtGui.QTextBrowser(self.scriptTabs[tab][c][0]))
        self.scriptTabs[tab][c][1].setUndoRedoEnabled(True)
        self.scriptTabs[tab][c][1].setReadOnly(self.navMode)
        self.scriptTabs[tab][c][1].setOpenLinks(False)
        self.scriptTabs[tab][c][1].setOpenExternalLinks(False)
        self.scriptTabs[tab][c][1].setGeometry(QtCore.QRect(24, 24, 513, 345))
        self.scriptTabs[tab][c][1].setObjectName("%s_browser_%i"%(tab,c))
        self.tabnames[tab][0].addTab(self.scriptTabs[tab][c][0],"%s_%i"%(tab,c+1))
        QtCore.QObject.connect(self.scriptTabs[tab][c][1], QtCore.SIGNAL("anchorClicked(QUrl)"), self.handleScriptUrl)
        QtCore.QMetaObject.connectSlotsByName(self)
    def addFunction(self):
        self.appendTab("func")
    def addMovement(self):
        self.appendTab("mov")
    # goto respective tabs and blah
    def gotoNavScript(self, tree, s):
        tabs = tree.text(s).split(" ")
        self.gotoMapTab(str(tabs[0]),int(tabs[1]))
        return False
    def gotoNavFunc(self, tree, f):
        tabs = tree.text(f).split(" ")
        self.gotoMapTab(str(tabs[0]),int(tabs[1]))
        return False
    def gotoNavMov(self, tree, m):
        tabs = tree.text(m).split(" ")
        self.gotoMapTab(str(tabs[0]),int(tabs[1]))
        return False
    def gotoCompileOutput(self):
        self.tabWidget.setCurrentIndex(5)
        pass
    def gotoMapTab(self,tab,subtab):
        tabs = {"Script":[0,"script"],"Function":[1,"func"],"Movement":[2,"mov"]}
        self.tabWidget.setCurrentIndex(tabs[tab][0])
        eval("self.%sTabWidget.setCurrentIndex(%i)"%(tabs[tab][1],subtab-1))
    def handleScriptUrl(self,url):
        #using QUrl
        self.gotoMapTab(str(url.scheme()).capitalize(),int(url.authority()))
    def updateMapData(self,n):
        if not self.loading:
            num=self.chooseMap.currentIndex()
            self.mapCodeName.setText(self.codes[num])
            self.chooseMapName.setCurrentIndex(self.iToName[num])
            num=mw.Of[0]+num*0x18
            #Of=(0xE601C,501, 1050 )
            arm9filename=mw.rom.getFolder()+"/arm9.bin"
            fh=QFile(arm9filename)
            fh.open(QIODevice.ReadOnly)
            ds=QDataStream(fh)
            ds.setByteOrder(QDataStream.LittleEndian)
            fh.seek(num)
            self.spinBox.setValue(ds.readUInt16())
            self.spinBox_2.setValue(ds.readUInt16())
            self.spinBox_3.setValue(ds.readUInt16())
            self.spinBox_4.setValue(ds.readUInt16())
            self.spinBox_5.setValue(ds.readUInt16())
            self.spinBox_6.setValue(ds.readUInt16())
            self.spinBox_7.setValue(ds.readUInt16())
            self.spinBox_8.setValue(ds.readUInt16())
            self.spinBox_9.setValue(ds.readUInt16())
            self.spinBox_10.setValue(ds.readUInt16())
            self.spinBox_11.setValue(ds.readUInt16())
            self.spinBox_12.setValue(ds.readUInt16())
            fh.close()
            if mw.ID== 0x5353 or mw.ID== 0x4748:
                if mw.lang == 0x4a:
                    try:
                        import alpha_assoc
                    except:
                        pass
                else:
                    try:
                        import alpha_assoc_u as alpha_assoc
                    except:
                        pass

                aa = alpha_assoc.AAssoc()
                self.spinBox_3.setValue(aa.returnScript(self.chooseMap.currentIndex()))
                self.spinBox_5.setValue(aa.returnText(self.chooseMap.currentIndex()))
                self.spinBox_8.setValue(aa.returnEnc(self.chooseMap.currentIndex()))
                self.spinBox_9.setValue(aa.returnEvent(self.chooseMap.currentIndex()))
            buff = None
            """
            self.scriptErrorLevel = 0
            try:
                self.scr=scripts.scriptFile(self.scriptNarc.gmif.files[self.spinBox_3.value()], mw.ID)
                self.scriptEdit.setPlainText(self.scr.getScript())
                self.orderEdit.setPlainText(self.scr.getOrders())
            except:
                print "Script error"
                self.scriptEdit.setPlainText("Script Error")
                self.scriptErrorLevel = 1#no other ones yet...
                print sys.exc_info()"""
            self.dump()
            self.compile()
            self.textFile=poketext.PokeTextData(self.msgNarc.gmif.files[self.spinBox_5.value()])
            self.textFile.decrypt()
            self.text=""
            for i in range(0, len(self.textFile.strlist)):
                self.text+="text_"+str(i)+"=\""+self.textFile.strlist[i]+"\"\n"
            self.textEdit.setPlainText(self.text)
            self.updateEnc()
            self.setupEvent()
            self.checkBox.setChecked(False)
    def setupEvent(self):
        eventd = self.eventNarc.gmif.files[self.spinBox_9.value()]
        self.ev=[]
        currentTabIndex = self.mapTab.currentIndex()
        for i in eventd:
            self.ev.append(ord(i))

        self.mapTab.removeTab(4)
        self.mapTab.removeTab(4)
        del(self.tab)
        del(self.tab_3)
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")

        event = bytereader.byteReader(self.ev)
        self.eventCont = QtGui.QTabWidget(self.tab)
        self.eventCont.setGeometry(QtCore.QRect(18, 10, 883, 515))
        self.eventCont.setObjectName("eventCont")
        self.evTypes = ("furniture","overworlds","warps","triggers")
        self.evLens = (10,16,6,8)
        self.textEv = {
    "furniture" : {0:"Script+1",2:"X-coordinate",4:"Y-coordinate"},#1:"Activate w/o Click Flag",
    "overworlds" : {
    0: "ID", 1: "sprite", 2: "movement",4:"Flag", 5: "script", 7: "Line of Sight", 12: "X-coordinate", 13: "Y-coordinate", 14: "Z-coordinate"},
    "warps" : {
    0: "X-coordinate",1: "Y-coordinate", 2: "Map ID", 3: "Map Anchor"},
    "triggers": {0:"Script+1",1:"X-coordinate",2:"Y-coordinate",3:"Width",4:"Length",7:"Flag"}}

        self.tabEv = {}
        self.spinLenEv = {}
        self.toolboxEv = {}
        self.pageEv = {}
        self.gridEv = {}
        self.spinEv = {}
        self.labelEv = {}
        self.trainers = []
        for L in range(0,4):
            item = self.evTypes[L]
            numItems = event.ReadUInt32()
            self.tabEv[item] = QtGui.QWidget()
            self.tabEv[item].setObjectName(item)
            self.toolboxEv[item] = QtGui.QTabWidget(self.tabEv[item])#QToolBox(self.tabEv[item])
            self.toolboxEv[item].setGeometry(QtCore.QRect(50, 50, 825, 425))
            self.toolboxEv[item].setObjectName(item+"_toolbox")
            self.spinLenEv[item] = QtGui.QSpinBox(self.tabEv[item])
            self.spinLenEv[item].setGeometry(QtCore.QRect(10, 5, 50, 20))
            self.spinLenEv[item].setObjectName(item+"_spinLenEv")
            self.spinLenEv[item].setMaximum(255)
            self.spinLenEv[item].setValue(numItems)
            QtCore.QObject.connect(self.spinLenEv[item], QtCore.SIGNAL("valueChanged(int)"), self.setEventNum)
            self.pageEv[item] = {}
            self.gridEv[item] = {}
            self.spinEv[item] = {}
            self.labelEv[item] = {}
            for M in range(0, numItems):
                self.pageEv[item][M] = QtGui.QWidget()
                self.pageEv[item][M].setGeometry(QtCore.QRect(0, 0, 800, 400))
                self.pageEv[item][M].setObjectName(item+"_page_"+str(M))
                self.gridEv[item][M] = QtGui.QGridLayout(self.pageEv[item][M])
                self.gridEv[item][M].setObjectName(item+"_grid_"+str(M))
                self.spinEv[item][M] = {}
                self.labelEv[item][M] = {}
                for N in range(0, self.evLens[L]):
                    self.labelEv[item][M][N] = QtGui.QLabel(self.pageEv[item][M])
                    self.labelEv[item][M][N].setObjectName(item+"_page"+str(M)+"_l"+str(N))
                    self.gridEv[item][M].addWidget(self.labelEv[item][M][N], N, 0)
                    self.spinEv[item][M][N] = QtGui.QSpinBox(self.pageEv[item][M])
                    self.spinEv[item][M][N].setObjectName(item+"_page"+str(M)+"_s"+str(N))
                    self.spinEv[item][M][N].setMaximum(65535)
                    self.spinEv[item][M][N].setValue(event.ReadUInt16())
                    self.gridEv[item][M].addWidget(self.spinEv[item][M][N], N, 1)
                    if N in self.textEv[item]:
                        self.labelEv[item][M][N].setText(self.textEv[item][N])
                        if self.textEv[item][N] == "script":
                            if (self.spinEv[item][M][N].value() in range(0xbb8, 0xf0a)):
                                self.trainers.append(self.spinEv[item][M][N].value()-0xbb7)
                self.toolboxEv[item].addTab(self.pageEv[item][M], "pg_"+str(M))
            self.eventCont.addTab(self.tabEv[item] ,item)
        self.mapTab.addTab(self.tab, "Events")
        self.mapTab.setCurrentIndex(currentTabIndex)
        #print self.trainers
        self.trButtons = {}
        self.pageTr = QtGui.QWidget(self.tab_3)
        self.pageTr.setGeometry(QtCore.QRect(0, 0, 800, 400))
        self.pageTr.setObjectName("pageTr")
        self.gridTr = QtGui.QGridLayout(self.pageTr)
        trMap = QtCore.QSignalMapper(self)
        v = 0
        for t in self.trainers:
            self.trButtons[t] = QtGui.QPushButton(self.pageTr)
            self.trButtons[t].setGeometry(QtCore.QRect(0, 0, 100, 30))
            opentext = "Open Trainer %i" % t
            self.trButtons[t].setText(opentext)
            self.gridTr.addWidget(self.trButtons[t],v/3,v%3)
            v += 1
            trMap.setMapping(self.trButtons[t],t)
            QtCore.QObject.connect(self.trButtons[t], QtCore.SIGNAL("clicked()"), trMap, QtCore.SLOT("map()"))
        self.mapTab.addTab(self.tab_3, "Trainers")
        QtCore.QObject.connect(trMap, QtCore.SIGNAL("mapped(int)"), self.openTrDlg)
        QtCore.QMetaObject.connectSlotsByName(self)
    def openTrDlg(self, trNum):
        p=TrainerEditDlg(self)
        p.chooseTrainer.setCurrentIndex(trNum)
        p.exec_()
    def setEventNum(self):
        cTab = self.eventCont.currentIndex()
        item = self.evTypes[cTab]
        numItems = self.spinLenEv[item].value()
        if numItems > self.toolboxEv[item].count():
            for M in range(self.toolboxEv[item].count(), numItems):
                self.pageEv[item][M] = QtGui.QWidget()
                self.pageEv[item][M].setGeometry(QtCore.QRect(0, 0, 800, 400))
                self.pageEv[item][M].setObjectName(item+"_page_"+str(M))
                self.gridEv[item][M] = QtGui.QGridLayout(self.pageEv[item][M])
                self.gridEv[item][M].setObjectName(item+"_grid_"+str(M))
                self.spinEv[item][M] = {}
                self.labelEv[item][M] = {}
                for N in range(0, self.evLens[cTab]):
                    self.labelEv[item][M][N] = QtGui.QLabel(self.pageEv[item][M])
                    self.labelEv[item][M][N].setObjectName(item+"_page"+str(M)+"_l"+str(N))
                    self.gridEv[item][M].addWidget(self.labelEv[item][M][N], N, 0)
                    if N in self.textEv[item]:
                        self.labelEv[item][M][N].setText(self.textEv[item][N])
                    self.spinEv[item][M][N] = QtGui.QSpinBox(self.pageEv[item][M])
                    self.spinEv[item][M][N].setObjectName(item+"_page"+str(M)+"_s"+str(N))
                    self.spinEv[item][M][N].setMaximum(65535)
                    self.spinEv[item][M][N].setValue(0)
                    self.gridEv[item][M].addWidget(self.spinEv[item][M][N], N, 1)
                self.toolboxEv[item].addTab(self.pageEv[item][M], "pg_"+str(M))
        return
    def saveEvent(self):
        eventwriter = bytereader.byteWriter()
        evTypes = ("furniture","overworlds","warps","triggers")
        evLens = (10,16,6,8)
        for L in range(0,4):
            item = evTypes[L]
            numItems = self.spinLenEv[item].value()
            eventwriter.WriteUInt32(numItems)
            for M in range(0, numItems):
                for N in range(0, evLens[L]):
                    eventwriter.WriteUInt16(self.spinEv[item][M][N].value())
        wEv = ""
        for w in eventwriter.ReturnData():
            wEv+=chr(int(w))
        self.eventNarc.replaceFile(self.spinBox_9.value(), wEv)
        WriteEventNarc(self.eventNarc)
        print "Event NARC written successfully!"
    def updateEnc(self):
        if ((mw.ID != 0x5353 and mw.ID != 0x4748 and self.spinBox_8.value() != 0xFFFF)
    or ((mw.ID== 0x5353 or mw.ID== 0x4748) and (self.spinBox_8.value() != 0xFF))):
            if (mw.ID== 0x5353 or mw.ID== 0x4748):
                en=self.encNarc.gmif.files[self.spinBox_8.value()]
                self.enc=[]
                for i in range(0, len(en)):
                    self.enc.append(ord(en[i]))
                encdata = bytereader.byteReader(self.enc)
                rates = ("walk","surf","rockSmash","oldRod","goodRod","superRod")
                for r in rates:
                    eval("self."+r+"Rate.setValue(encdata.ReadByte())")
                encdata.Accel(2)
                for i in range(0,12):
                    eval("self.walkPokeLvl"+str(i+1)+".setValue(encdata.ReadByte())")
                daytimes = ("Morning","Day","Night")
                for d in daytimes:
                    for i in range(0,12):
                        eval("self.chooseWalk"+d+str(i+1)+".setCurrentIndex(encdata.ReadUInt16())")



                timeLen = (("hoenn",2),
    ("sinnoh",2))
                for i in range(0, len(timeLen)):
                    for j in range(0, timeLen[i][1]):
                        eval("self."+(timeLen[i][0])+str(j+1)+".setCurrentIndex(encdata.ReadUInt16())")

                waters = ("surf","rockSmash","oldRod","goodRod","superRod")
                for i in range(0, len(waters)):
                    if waters[i] == "rockSmash":
                        waterRange = 2
                    else:
                        waterRange = 5
                    for j in range(0, waterRange):
                        eval("self."+waters[i]+"Min"+str(j+1)+".setValue(encdata.ReadByte())")
                        eval("self."+waters[i]+"Max"+str(j+1)+".setValue(encdata.ReadByte())")
                        if waters[i] == "rockSmash":
                            eval("self."+waters[i]+""+str(j+1)+".setCurrentIndex(encdata.ReadUInt16())")
                        else:
                            eval("self."+waters[i]+"Poke"+str(j+1)+".setCurrentIndex(encdata.ReadUInt16())")
                timeLen = [("radio",2)]
                for i in range(0, len(timeLen)):
                    for j in range(0, timeLen[i][1]):
                        eval("self."+(timeLen[i][0])+str(j+1)+".setCurrentIndex(encdata.ReadUInt16())")

            else:
                en=self.encNarc.gmif.files[self.spinBox_8.value()]
                self.enc=[]
                cE=0
                for i in range(0, len(en)):
                    self.enc.append(ord(en[i]))
                encdata = bytereader.byteReader(self.enc)

                self.walkRate.setValue(encdata.ReadUInt32())
                for i in range(1,13):
                    eval("self.walkPokeLvl"+str(i)+".setValue(encdata.ReadUInt32())")
                    eval("self.chooseWalkPoke"+str(i)+".setCurrentIndex(encdata.ReadUInt32())")
                timeLen = (("morning",2),
    ("day",2),
    ("night",2),
    ("radar",4),
    ("ruby",2),
    ("sapphire",2),
    ("emerald",2),
    ("red",2),
    ("green",2))

                for i in range(0, len(timeLen)):
                    for j in range(0, timeLen[i][1]):
                        eval("self."+(timeLen[i][0])+str(j+1)+".setCurrentIndex(encdata.ReadUInt32())")
                        if j == 3:
                            encdata.Accel(24)

                waters = ("surf","oldRod","goodRod","superRod")
                for i in range(0, len(waters)):
                    eval("self."+waters[i]+"Rate.setValue(encdata.ReadUInt32())")
                    for j in range(0, 5):
                        eval("self."+waters[i]+"Min"+str(j+1)+".setValue(encdata.ReadByte())")
                        eval("self."+waters[i]+"Max"+str(j+1)+".setValue(encdata.ReadByte())")
                        encdata.Accel(2)
                        eval("self."+waters[i]+"Poke"+str(j+1)+".setCurrentIndex(encdata.ReadUInt32())")

        else:

            if (mw.ID== 0x5353 or mw.ID== 0x4748):
                rates = ("walk","surf","rockSmash","oldRod","goodRod","superRod")
                for r in rates:
                    eval("self."+r+"Rate.setValue(0)")
                for i in range(0,12):
                    eval("self.walkPokeLvl"+str(i+1)+".setValue(0)")
                daytimes = ("Morning","Day","Night")
                for d in daytimes:
                    for i in range(0,12):
                        eval("self.chooseWalk"+d+str(i+1)+".setCurrentIndex(0)")



                timeLen = (("hoenn",2),
    ("sinnoh",2),
    ("radio",2))
                for i in range(0, len(timeLen)):
                    for j in range(0, timeLen[i][1]):
                        eval("self."+(timeLen[i][0])+str(j+1)+".setCurrentIndex(0)")

                waters = ("surf","rockSmash","oldRod","goodRod","superRod")
                for i in range(0, len(waters)):
                    eval("self."+waters[i]+"Rate.setValue(0)")
                    if waters[i] == "rockSmash":
                        waterRange = 2
                    else:
                        waterRange = 5
                    for j in range(0, waterRange):
                        if waters[i] == "rockSmash":
                            eval("self."+waters[i]+""+str(j+1)+".setCurrentIndex(0)")
                        else:
                            eval("self."+waters[i]+"Min"+str(j+1)+".setValue(0)")
                            eval("self."+waters[i]+"Max"+str(j+1)+".setValue(0)")
                            eval("self."+waters[i]+"Poke"+str(j+1)+".setCurrentIndex(0)")
                return

            self.walkRate.setValue(0)
            self.walkPokeLvl1.setValue(0)
            self.chooseWalkPoke1.setCurrentIndex(0)
            self.walkPokeLvl2.setValue(0)
            self.chooseWalkPoke2.setCurrentIndex(0)
            self.walkPokeLvl3.setValue(0)
            self.chooseWalkPoke3.setCurrentIndex(0)
            self.walkPokeLvl4.setValue(0)
            self.chooseWalkPoke4.setCurrentIndex(0)
            self.walkPokeLvl5.setValue(0)
            self.chooseWalkPoke5.setCurrentIndex(0)
            self.walkPokeLvl6.setValue(0)
            self.chooseWalkPoke6.setCurrentIndex(0)
            self.walkPokeLvl7.setValue(0)
            self.chooseWalkPoke7.setCurrentIndex(0)
            self.walkPokeLvl8.setValue(0)
            self.chooseWalkPoke8.setCurrentIndex(0)
            self.walkPokeLvl9.setValue(0)
            self.chooseWalkPoke9.setCurrentIndex(0)
            self.walkPokeLvl10.setValue(0)
            self.chooseWalkPoke10.setCurrentIndex(0)
            self.walkPokeLvl11.setValue(0)
            self.chooseWalkPoke11.setCurrentIndex(0)
            self.walkPokeLvl12.setValue(0)
            self.chooseWalkPoke12.setCurrentIndex(0)
            self.morning1.setCurrentIndex(0)
            self.morning2.setCurrentIndex(0)
            self.day1.setCurrentIndex(0)
            self.day2.setCurrentIndex(0)
            self.night1.setCurrentIndex(0)
            self.night2.setCurrentIndex(0)
            self.radar1.setCurrentIndex(0)
            self.radar2.setCurrentIndex(0)
            self.radar3.setCurrentIndex(0)
            self.radar4.setCurrentIndex(0)
            self.ruby1.setCurrentIndex(0)
            self.ruby2.setCurrentIndex(0)
            self.sapphire1.setCurrentIndex(0)
            self.sapphire2.setCurrentIndex(0)
            self.emerald1.setCurrentIndex(0)
            self.emerald2.setCurrentIndex(0)
            self.red1.setCurrentIndex(0)
            self.red2.setCurrentIndex(0)
            self.green1.setCurrentIndex(0)
            self.green2.setCurrentIndex(0)
            self.surfRate.setValue(0)
            self.surfMax1.setValue(0)
            self.surfMin1.setValue(0)
            self.surfPoke1.setCurrentIndex(0)
            self.surfMax2.setValue(0)
            self.surfMin2.setValue(0)
            self.surfPoke2.setCurrentIndex(0)
            self.surfMax3.setValue(0)
            self.surfMin3.setValue(0)
            self.surfPoke3.setCurrentIndex(0)
            self.surfMax4.setValue(0)
            self.surfMin4.setValue(0)
            self.surfPoke4.setCurrentIndex(0)
            self.surfMax5.setValue(0)
            self.surfMin5.setValue(0)
            self.surfPoke5.setCurrentIndex(0)
            self.oldRodRate.setValue(0)
            self.oldRodMax1.setValue(0)
            self.oldRodMin1.setValue(0)
            self.oldRodPoke1.setCurrentIndex(0)
            self.oldRodMax2.setValue(0)
            self.oldRodMin2.setValue(0)
            self.oldRodPoke2.setCurrentIndex(0)
            self.oldRodMax3.setValue(0)
            self.oldRodMin3.setValue(0)
            self.oldRodPoke3.setCurrentIndex(0)
            self.oldRodMax4.setValue(0)
            self.oldRodMin4.setValue(0)
            self.oldRodPoke4.setCurrentIndex(0)
            self.oldRodMax5.setValue(0)
            self.oldRodMin5.setValue(0)
            self.oldRodPoke5.setCurrentIndex(0)
            self.goodRodRate.setValue(0)
            self.goodRodMax1.setValue(0)
            self.goodRodMin1.setValue(0)
            self.goodRodPoke1.setCurrentIndex(0)
            self.goodRodMax2.setValue(0)
            self.goodRodMin2.setValue(0)
            self.goodRodPoke2.setCurrentIndex(0)
            self.goodRodMax3.setValue(0)
            self.goodRodMin3.setValue(0)
            self.goodRodPoke3.setCurrentIndex(0)
            self.goodRodMax4.setValue(0)
            self.goodRodMin4.setValue(0)
            self.goodRodPoke4.setCurrentIndex(0)
            self.goodRodMax5.setValue(0)
            self.goodRodMin5.setValue(0)
            self.goodRodPoke5.setCurrentIndex(0)
            self.superRodRate.setValue(0)
            self.superRodMax1.setValue(0)
            self.superRodMin1.setValue(0)
            self.superRodPoke1.setCurrentIndex(0)
            self.superRodMax2.setValue(0)
            self.superRodMin2.setValue(0)
            self.superRodPoke2.setCurrentIndex(0)
            self.superRodMax3.setValue(0)
            self.superRodMin3.setValue(0)
            self.superRodPoke3.setCurrentIndex(0)
            self.superRodMax4.setValue(0)
            self.superRodMin4.setValue(0)
            self.superRodPoke4.setCurrentIndex(0)
            self.superRodMax5.setValue(0)
            self.superRodMin5.setValue(0)
            self.superRodPoke5.setCurrentIndex(0)
    def updateMap(self):
        """try:
            if self.scriptErrorLevel == 1:
                raise ScriptException("Script Failed to load.")
            result=self.scr.getBinary(self.scriptEdit.toPlainText(),self.orderEdit.toPlainText())
            if result==False:
                raise ScriptException(self.scr.errorText)
            else:
                print "Script NARC written successfully!"
            self.scriptNarc.replaceFile(self.spinBox_3.value(), result)
            WriteScriptNarc(self.scriptNarc)
        except ScriptException as e:
            error = "The Script has the following error:\n%s: %s\n\nThe Script will not be Saved!" % (e.value[0],e.value[1])
            QMessageBox.critical(self,"Warning",error)
        except e:
            QMessageBox.critical(self,"Critical","A Critical Error has occurred while the Script was being compiled!")
            print e"""
        self.scr.writeScript()
        WriteScriptNarc(self.scriptNarc)
        self.saveEncounters()
        self.saveText()
        self.saveEvent()
    def saveText(self):
        #self.textFile
        texttopoke.allowErrors()
        if self.spinBox_5.value() == 3:
            return
        text = self.textEdit.toPlainText()
        textStrings = string.split(text, "text_")
        for t in textStrings:
            numS = ""
            for eq in t:
                if eq == "=":
                    break
                else:
                    numS += eq
            numT = int(numS)
            startS = False
            textStr = ""
            for s in t:
                if (s == "\"") and not startS:
                    textStr = ""
                    startS = True
                elif (s == "\"") and startS:
                    break
                else:
                    textStr += s
            if numT < len(self.textFile.strlist):
                self.textFile.strlist[numT] = unicode(textStr)
            else:
                self.textFile.strlist.append(unicode(textStr))
        p=texttopoke.Makefile(self.textFile.strlist,True)
        encrypt = poketext.PokeTextData(p)
        encrypt.SetKey(0xD00E)
        encrypt.encrypt()
        self.msgNarc.replaceFile(self.spinBox_5.value(), encrypt.getStr())
        WriteMsgNarc(self.msgNarc)
        print "Wrote Text NARC successfully!"
    def saveEncounters(self):
        if (self.spinBox_8.value() == 0xff and (mw.ID== 0x5353 or mw.ID== 0x4748)):
            return
        elif self.spinBox_8.value() == 0xffff:
            return
        writeenc = bytereader.byteWriter()

        if (mw.ID== 0x5353 or mw.ID== 0x4748):
            rates = ("walk","surf","rockSmash","oldRod","goodRod","superRod")
            for r in rates:
                writeenc.WriteByte(eval("self."+r+"Rate.value()"))
            writeenc.WriteUInt16(0)
            for i in range(0,12):
                writeenc.WriteByte(eval("self.walkPokeLvl"+str(i+1)+".value()"))
            daytimes = ("Morning","Day","Night")
            for d in daytimes:
                for i in range(0,12):
                    writeenc.WriteUInt16(eval("self.chooseWalk"+d+str(i+1)+".currentIndex()"))
            timeLen = (("hoenn",2),
    ("sinnoh",2))
            for i in range(0, len(timeLen)):
                for j in range(0, timeLen[i][1]):
                    writeenc.WriteUInt16(eval("self."+(timeLen[i][0])+str(j+1)+".currentIndex()"))

            waters = ("surf","rockSmash","oldRod","goodRod","superRod")
            for i in range(0, len(waters)):
                if waters[i] == "rockSmash":
                    waterRange = 2
                else:
                    waterRange = 5
                for j in range(0, waterRange):
                    writeenc.WriteByte(eval("self."+waters[i]+"Min"+str(j+1)+".value()"))
                    writeenc.WriteByte(eval("self."+waters[i]+"Max"+str(j+1)+".value()"))
                    if waters[i] == "rockSmash":
                        writeenc.WriteUInt16(eval("self."+waters[i]+""+str(j+1)+".currentIndex()"))
                    else:
                        writeenc.WriteUInt16(eval("self."+waters[i]+"Poke"+str(j+1)+".currentIndex()"))
            timeLen = [("radio",2)]
            for i in range(0, len(timeLen)):
                for j in range(0, timeLen[i][1]):
                    writeenc.WriteUInt16(eval("self."+(timeLen[i][0])+str(j+1)+".currentIndex()"))

        else:
            writeenc.WriteUInt32(self.walkRate.value())
            for i in range(1,13):
                writeenc.WriteUInt32(eval("self.walkPokeLvl"+str(i)+".value()"))
                writeenc.WriteUInt32(eval("self.chooseWalkPoke"+str(i)+".currentIndex()"))
            timeLen = (("morning",2),
    ("day",2),
    ("night",2),
    ("radar",4),
    ("ruby",2),
    ("sapphire",2),
    ("emerald",2),
    ("red",2),
    ("green",2))

            for i in range(0, len(timeLen)):
                for j in range(0, timeLen[i][1]):
                    writeenc.WriteUInt32(eval("self."+(timeLen[i][0])+str(j+1)+".currentIndex()"))
                    if j == 3:
                        for a in range(0, 24):
                            writeenc.WriteByte(0)

            waters = ("surf","oldRod","goodRod","superRod")
            for i in range(0, len(waters)):
                writeenc.WriteUInt32(eval("self."+waters[i]+"Rate.value()"))
                for j in range(0, 5):
                    writeenc.WriteByte(eval("self."+waters[i]+"Min"+str(j+1)+".value()"))
                    writeenc.WriteByte(eval("self."+waters[i]+"Max"+str(j+1)+".value()"))
                    writeenc.WriteUInt16(0)
                    writeenc.WriteUInt32(eval("self."+waters[i]+"Poke"+str(j+1)+".currentIndex()"))

        wEnc = ""
        for w in writeenc.ReturnData():
            wEnc+=chr(int(w))
        self.encNarc.replaceFile(self.spinBox_8.value(), wEnc)
        WriteEncNarc(self.encNarc)
        print "Encounter NARC written successfully!"

    def getDescriptiveName(self, code):
        try:
            mN=poketext.PokeTextData(self.msgNarc.gmif.files[mw.TN[0]])
            #mN is the text data with map/location names
            mN.decrypt()
            name=""
            cC=[] #code Chars array, holds the characters in the map name code
            for chr in code:
                cC.append(chr)
            """if mw.ID== 0x5353 or mw.ID== 0x4748:
                gscode = ""
                for c in cC:
                    gscode += c
                return gscode
            #cC[0]"""
            if cC[0]=='C':
                num=10*int(cC[1])+int(cC[2])
                if mw.cities[num-1][0]!=0xFF:
                    name+=mN.strlist[mw.cities[num-1][0]]
                if len(cC)>3:
                    if cC[3]=='P':
                        name+=" "+mw.other[0]
                        if cC[8]=='2':
                            name+=" Bottom Floor"
                        elif cC[8]=='3':
                            name+=" Top Floor"
                    elif cC[3]=='F':
                        name+=" "+mw.other[1]
                    elif cC[3]=='G':
                        name+=" "+mw.other[2]
                    elif cC[3]=='R':
                        num2=10*int(cC[4])+int(cC[5])
                        if mw.cities[num-1][num2][0]!=0xFF:
                            name+=" "+mN.strlist[mw.cities[num-1][num2][0]]
                        else:
                            name+=" R"+str(num2)
                        name+="-"+cC[6]+cC[7]
            elif cC[0]=='T':
                num=10*int(cC[1])+int(cC[2])
                name+=mN.strlist[mw.towns[num-1][0]]
                if len(cC)>3:
                    if cC[3]=='P':
                        name+=" "+mw.other[0]
                        if cC[8]=='2':
                            name+=" Bottom Floor"
                        elif cC[8]=='3':
                            name+=" Top Floor"
                    elif cC[3]=='F':
                        name+=" "+mw.other[1]
                    elif cC[3]=='G':
                        name+=" "+mw.other[2]
                        if len(cC)>6:
                            name+="-"+cC[6]+str(cC[7])
                        if len(cC)>8:
                            name+="-"+cC[8]+str(cC[9])
                    elif cC[3]=='R':
                        num2=10*int(cC[4])+int(cC[5])
                        if mw.towns[num-1][num2][0]!=0xFF:
                            name+=" "+mN.strlist[mw.towns[num-1][num2][0]]
                        else:
                            name+=" R"+str(num2)
                        name+="-"+cC[6]+str(cC[7])
            elif cC[0]=='L':
                num=10*int(cC[1])+int(cC[2])
                if mw.lakes[num-1][0]!=0xFF:
                    name+=mN.strlist[mw.lakes[num-1][0]]
                else:
                    name+=code
                if len(cC)>3:
                    if cC[3]=='R':
                        num2=10*int(cC[4])+int(cC[5])
                        if mw.lakes[num-1][num2][0]!=0xFF:
                            name+=" "+mN.strlist[mw.lakes[num-1][num2][0]]
                        else:
                            name+=" R"+str(num2)
                        name+="-"+cC[6]+str(cC[7])
            elif cC[0]=='D'  and cC[1]>='0'and cC[1]<='9':
                num=10*int(cC[1])+int(cC[2])
                if mw.dungeons[num-1][0]!=0xFF:
                    name+=mN.strlist[mw.dungeons[num-1][0]]
                else:
                    name+=code
                if len(cC)>3:
                    if cC[3]=='P':
                        name+=" "+mw.other[0]
                        if cC[8]=='2':
                            name+=" Bottom Floor"
                        elif cC[8]=='3':
                            name+=" Top Floor"
                    elif cC[3]=='F':
                        name+=" "+mw.other[1]
                    elif cC[3]=='G':
                        name+=" "+mw.other[2]
                    elif cC[3]=='R':
                        num2=10*int(cC[4])+int(cC[5])
                        if mw.dungeons[num-1][num2][0]!=0xFF:
                            name+=" "+mN.strlist[mw.dungeons[num-1][num2][0]]
                        else:
                            name+=" R"+str(num2)
                        name+="-"+cC[6]+str(cC[7])
            elif (cC[0]=='R' or cC[0]=='W'):
                if cC[1]=='2':
                    if mw.ID== 0x5353 or mw.ID== 0x4748:
                        cP = 1
                        bound = 4
                    else:
                        cP=2
                        bound = 5
                else:
                    cP = 1
                    bound = 4
                num=10*int(cC[cP])+int(cC[cP+1])
                cP+=2
                if mw.routes[num-1][0]!=0xFF:
                    name+=mN.strlist[mw.routes[num-1][0]]
                else:
                    name+=code
                if len(cC)>bound:
                    pc = False
                    if cC[cP]=='P':
                        name+=" "+mw.other[0]
                        if cC[8]=='2':
                            name+=" Bottom Floor"
                        elif cC[8]=='3':
                            name+=" Top Floor"
                        pc = "True"
                    elif cC[3]=='F':
                        name+=" "+mw.other[1]
                        pc = "True"
                    elif cC[3]=='G':
                        name+=" "+mw.other[2]
                        pc = "True"
                    elif cC[cP] != 'R':
                        name+=" "+cC[cP]
                        cP+=1
                    if len(cC)>(bound+1) and not pc:
                        if cC[cP]=='R':
                            num2=10*int(cC[cP+1])+int(cC[cP+2])
                            if mw.routes[num-1][num2][0]!=0xFF:
                                name+=" "+mN.strlist[mw.routes[num-1][num2][0]]
                            else:
                                name+=" R"+str(num2)
                            name+="-"+cC[cP+3]+str(cC[cP+4])
            else:
                name+=code
        except:
            name = code
            print "Failed: %s" % name
        return name
    def setupEncUi(self):
        pokeNames=poketext.PokeTextData(self.msgNarc.gmif.files[mw.TN[5]])
        pokeNames.decrypt()
        self.pN=[]
        for i in range(0, 494):
            self.pN.append(pokeNames.strlist[i])
        if mw.ID== 0x5353 or mw.ID== 0x4748:
            self.chooseWalkMorning1.addItems(self.pN)
            self.chooseWalkMorning2.addItems(self.pN)
            self.chooseWalkMorning3.addItems(self.pN)
            self.chooseWalkMorning4.addItems(self.pN)
            self.chooseWalkMorning5.addItems(self.pN)
            self.chooseWalkMorning6.addItems(self.pN)
            self.chooseWalkMorning7.addItems(self.pN)
            self.chooseWalkMorning8.addItems(self.pN)
            self.chooseWalkMorning9.addItems(self.pN)
            self.chooseWalkMorning10.addItems(self.pN)
            self.chooseWalkMorning11.addItems(self.pN)
            self.chooseWalkMorning12.addItems(self.pN)
            self.chooseWalkDay1.addItems(self.pN)
            self.chooseWalkDay2.addItems(self.pN)
            self.chooseWalkDay3.addItems(self.pN)
            self.chooseWalkDay4.addItems(self.pN)
            self.chooseWalkDay5.addItems(self.pN)
            self.chooseWalkDay6.addItems(self.pN)
            self.chooseWalkDay7.addItems(self.pN)
            self.chooseWalkDay8.addItems(self.pN)
            self.chooseWalkDay9.addItems(self.pN)
            self.chooseWalkDay10.addItems(self.pN)
            self.chooseWalkDay11.addItems(self.pN)
            self.chooseWalkDay12.addItems(self.pN)
            self.chooseWalkNight1.addItems(self.pN)
            self.chooseWalkNight2.addItems(self.pN)
            self.chooseWalkNight3.addItems(self.pN)
            self.chooseWalkNight4.addItems(self.pN)
            self.chooseWalkNight5.addItems(self.pN)
            self.chooseWalkNight6.addItems(self.pN)
            self.chooseWalkNight7.addItems(self.pN)
            self.chooseWalkNight8.addItems(self.pN)
            self.chooseWalkNight9.addItems(self.pN)
            self.chooseWalkNight10.addItems(self.pN)
            self.chooseWalkNight11.addItems(self.pN)
            self.chooseWalkNight12.addItems(self.pN)
            self.hoenn1.addItems(self.pN)
            self.hoenn2.addItems(self.pN)
            self.sinnoh1.addItems(self.pN)
            self.sinnoh2.addItems(self.pN)
            self.radio1.addItems(self.pN)
            self.radio2.addItems(self.pN)
            self.rockSmash1.addItems(self.pN)
            self.rockSmash2.addItems(self.pN)
        else:
            self.chooseWalkPoke1.addItems(self.pN)
            self.chooseWalkPoke2.addItems(self.pN)
            self.chooseWalkPoke3.addItems(self.pN)
            self.chooseWalkPoke4.addItems(self.pN)
            self.chooseWalkPoke5.addItems(self.pN)
            self.chooseWalkPoke6.addItems(self.pN)
            self.chooseWalkPoke7.addItems(self.pN)
            self.chooseWalkPoke8.addItems(self.pN)
            self.chooseWalkPoke9.addItems(self.pN)
            self.chooseWalkPoke10.addItems(self.pN)
            self.chooseWalkPoke11.addItems(self.pN)
            self.chooseWalkPoke12.addItems(self.pN)
            self.morning1.addItems(self.pN)
            self.morning2.addItems(self.pN)
            self.day1.addItems(self.pN)
            self.day2.addItems(self.pN)
            self.night1.addItems(self.pN)
            self.night2.addItems(self.pN)
            self.radar1.addItems(self.pN)
            self.radar2.addItems(self.pN)
            self.radar3.addItems(self.pN)
            self.radar4.addItems(self.pN)
            self.ruby1.addItems(self.pN)
            self.ruby2.addItems(self.pN)
            self.sapphire1.addItems(self.pN)
            self.sapphire2.addItems(self.pN)
            self.emerald1.addItems(self.pN)
            self.emerald2.addItems(self.pN)
            self.red1.addItems(self.pN)
            self.red2.addItems(self.pN)
            self.green1.addItems(self.pN)
            self.green2.addItems(self.pN)
        self.surfPoke1.addItems(self.pN)
        self.surfPoke2.addItems(self.pN)
        self.surfPoke3.addItems(self.pN)
        self.surfPoke4.addItems(self.pN)
        self.surfPoke5.addItems(self.pN)
        self.oldRodPoke1.addItems(self.pN)
        self.oldRodPoke2.addItems(self.pN)
        self.oldRodPoke3.addItems(self.pN)
        self.oldRodPoke4.addItems(self.pN)
        self.oldRodPoke5.addItems(self.pN)
        self.goodRodPoke1.addItems(self.pN)
        self.goodRodPoke2.addItems(self.pN)
        self.goodRodPoke3.addItems(self.pN)
        self.goodRodPoke4.addItems(self.pN)
        self.goodRodPoke5.addItems(self.pN)
        self.superRodPoke1.addItems(self.pN)
        self.superRodPoke2.addItems(self.pN)
        self.superRodPoke3.addItems(self.pN)
        self.superRodPoke4.addItems(self.pN)
        self.superRodPoke5.addItems(self.pN)
class TmHmDlg(QDialog, ui_ppretmhmedit.Ui_TmHmEditDlg):
    def __init__(self,parent=None):
        super(TmHmDlg,self).__init__(parent)
        self.setupUi(self)
        self.archive=ReadMsgNarc()
        binary=poketext.PokeTextData(self.archive.gmif.files[392])
        binary.decrypt()
        self.chooseTm.addItems(binary.strlist[0x148:0x1AC])
        binary=poketext.PokeTextData(self.archive.gmif.files[647])
        binary.decrypt()
        self.chooseMove.addItems(binary.strlist)
        self.chooseTm.setCurrentIndex(1)
        self.chooseTm.setCurrentIndex(0)
    def changedTm(self,event):
        num=self.chooseTm.currentIndex()
        num=0xF0BFC+num*0x2
        arm9filename=mw.rom.getFolder()+"/arm9.bin"
        fh=QFile(arm9filename)
        fh.open(QIODevice.ReadOnly)
        ds=QDataStream(fh)
        ds.setByteOrder(QDataStream.LittleEndian)
        fh.seek(num)
        movenum=ds.readUInt16()
        fh.close()
        self.chooseMove.setCurrentIndex(movenum)
class MoveDlg(QDialog, ui_ppremoveedit.Ui_MoveEditDlg):
    def __init__(self,parent=None):
        super(MoveDlg,self).__init__(parent)
        self.setupUi(self)
        self.waza=ReadWazaNarc()
        self.archive=ReadMsgNarc()
        if mw.ID in (0x5353,0x4748):
            binary=poketext.PokeTextData(self.archive.gmif.files[mw.DT["move"]])
            binary.decrypt()
            self.chooseMove.addItems(binary.strlist)
            self.ctype.addItems(["Coolness","Beauty","Cuteness","Smartness","Toughness"])
            binary=poketext.PokeTextData(self.archive.gmif.files[mw.DT["type"]])
            binary.decrypt()
            self.type.addItems(binary.strlist)
        else:
            binary=poketext.PokeTextData(self.archive.gmif.files[mw.TN[4]])
            binary.decrypt()
            self.chooseMove.addItems(binary.strlist)
            if mw.ID==0x4C50:
                if mw.lang==0x4A:
                    binary=poketext.PokeTextData(self.archive.gmif.files[207])
                else:
                    binary=poketext.PokeTextData(self.archive.gmif.files[208])
            else:
                if mw.lang==0x4B:
                    binary=poketext.PokeTextData(self.archive.gmif.files[194])
                else:
                    binary=poketext.PokeTextData(self.archive.gmif.files[195])
            binary.decrypt()
            self.ctype.addItems(binary.strlist[2:7])
            if mw.ID==0x4C50:
                if mw.lang==0x4A:
                    binary=poketext.PokeTextData(self.archive.gmif.files[616])
                else:
                    binary=poketext.PokeTextData(self.archive.gmif.files[624])
            else:
                if mw.lang==0x4A:
                    binary=poketext.PokeTextData(self.archive.gmif.files[557])
                else:
                    binary=poketext.PokeTextData(self.archive.gmif.files[565])
            binary.decrypt()
            self.type.addItems(binary.strlist)
        for i in range (0,0x120):
            self.effect.addItem(unicode(i))
        self.cpower=(0,2,2,8,2,3,1,2,0,0,2,0,0,2,2,2,0,2,2,2,1,0,2,1)
    def moveChanged(self):
        if mw.ID==0x4C50:
            if mw.lang==0x4A:
                temptext=poketext.PokeTextData(self.archive.gmif.files[635])
            else:
                temptext=poketext.PokeTextData(self.archive.gmif.files[646])
        else:
            if mw.lang==0x4A:
                temptext=poketext.PokeTextData(self.archive.gmif.files[574])
            elif mw.lang==0x4B:
                temptext=poketext.PokeTextData(self.archive.gmif.files[576])
            else:
                temptext=poketext.PokeTextData(self.archive.gmif.files[587])
        temptext.decrypt()
        self.atkDesc.setPlainText(temptext.strlist[self.chooseMove.currentIndex()])
        file=self.waza.gmif.files[self.chooseMove.currentIndex()]
        if mw.ID==0x4C50:
            if mw.lang==0x4A:
                temptext=poketext.PokeTextData(self.archive.gmif.files[209])
            else:
                temptext=poketext.PokeTextData(self.archive.gmif.files[210])
        else:
            if mw.lang==0x4A:
                temptext=poketext.PokeTextData(self.archive.gmif.files[0])
            if mw.lang==0x4B:
                temptext=poketext.PokeTextData(self.archive.gmif.files[196])
            else:
                temptext=poketext.PokeTextData(self.archive.gmif.files[197])
        temptext.decrypt()
        self.catkDesc.setPlainText(temptext.strlist[45+ord(file[12])])
        self.cindex=ord(file[12])
        self.effect.setCurrentIndex(ord(file[0])|(ord(file[1])<<8))
        self.category.setCurrentIndex(ord(file[2]))
        self.basePower.setValue(ord(file[3]))
        self.accuracy.setValue(ord(file[5]))
        self.type.setCurrentIndex(ord(file[4]))
        self.ctype.setCurrentIndex(ord(file[13]))
        self.pp.setValue(ord(file[6]))
        self.effectChance.setValue(ord(file[7]))
        self.priority.setValue(ord(file[10]))
        num=0
        for i in range(0,8):
            if (ord(file[8])>>i)==1:
                num=i+1
        self.target.setCurrentIndex(num)
        self.unk1.setValue(ord(file[11]))
class ItemDlg(QDialog, ui_ppreitemedit.Ui_ItemEditDlg):
    def __init__(self,parent=None):
        super(ItemDlg,self).__init__(parent)
        self.setupUi(self)
        self.archive=ReadMsgNarc()
        if mw.ID==0x4C50:
            if mw.lang==0x4A:
                binary=poketext.PokeTextData(self.archive.gmif.files[390])
            else:
                binary=poketext.PokeTextData(self.archive.gmif.files[392])
        else:
            if mw.lang==0x4A:
                binary=poketext.PokeTextData(self.archive.gmif.files[340])
            elif mw.lang==0x4B:
                binary=poketext.PokeTextData(self.archive.gmif.files[342])
            else:
                binary=poketext.PokeTextData(self.archive.gmif.files[344])
        binary.decrypt()
        self.chooseItem.addItems(binary.strlist)
class AbilityDlg(QDialog, ui_ppreabilityedit.Ui_AbilityEditDlg):
    def __init__(self,parent=None):
        super(AbilityDlg,self).__init__(parent)
        self.setupUi(self)
        self.archive=ReadMsgNarc()
        if mw.ID==0x4C50:
            if mw.lang==0x4A:
                binary=poketext.PokeTextData(self.archive.gmif.files[604])
            else:
                binary=poketext.PokeTextData(self.archive.gmif.files[610])
        else:
            if mw.lang==0x4B:
                binary=poketext.PokeTextData(self.archive.gmif.files[546])
            else:
                binary=poketext.PokeTextData(self.archive.gmif.files[552])
        binary.decrypt()
        self.chooseAbility.addItems(binary.strlist)
class ScriptDlg(QDialog, ui_pprescripts.Ui_scriptDlg):
    def __init__(self,parent=None):
        super(ScriptDlg,self).__init__(parent)
        self.setupUi(self)
        self.scriptNarc=ReadScriptNarc()
        size=self.scriptNarc.btaf.getEntryNum()
        for i in range(0,size):
            self.chooseScript.addItem(unicode(i))
    def updateScript(self,n):
        num=self.chooseScript.currentIndex()
        if num < mw.Of[1] or num > mw.Of[2]:
            self.scr=scripts.scriptFile(self.scriptNarc.gmif.files[num], mw.ID)
            self.scriptEdit.setPlainText(self.scr.getScript())
            self.orderEdit.setPlainText(self.scr.getOrders())
        else:
            self.scriptEdit.setPlainText("Cannot Edit This File")
class TrainerEditDlg(QDialog, ui_ppretredit.Ui_TrainerEditDlg):
    def __init__(self,parent=None):
        super(TrainerEditDlg,self).__init__(parent)
        self.setupUi(self)
        self.msgNarc=ReadMsgNarc()
        self.trNarc=ReadTrNarc()
        self.trPokeNarc=ReadTrPokeNarc()
        size=self.trNarc.btaf.getEntryNum()
        trClasses=poketext.PokeTextData(self.msgNarc.gmif.files[mw.TN[11]])
        trClasses.decrypt()
        self.trNames=poketext.PokeTextData(self.msgNarc.gmif.files[mw.TN[12]])
        self.trNames.decrypt()
        self.class_2.addItems(trClasses.strlist)
        for i in range(0, len(self.trNames.strlist)):
            self.chooseTrainer.addItem(str(i)+"-"+self.trNames.strlist[i])
        pokeNames=poketext.PokeTextData(self.msgNarc.gmif.files[mw.TN[5]])
        pokeNames.decrypt()
        self.pN=[]
        for i in range(0, 494):
            self.pN.append(pokeNames.strlist[i])
        moveNames=poketext.PokeTextData(self.msgNarc.gmif.files[mw.TN[4]])
        moveNames.decrypt()
        self.mN = []
        for i in range(0, len(moveNames.strlist)):
            self.mN.append(moveNames.strlist[i])
        itemNames=poketext.PokeTextData(self.msgNarc.gmif.files[mw.TN[3]])
        itemNames.decrypt()
        self.iN=[]
        for i in range(0, len(itemNames.strlist)):
            self.iN.append(itemNames.strlist[i])
        self.item1.addItems(self.iN)
        self.item2.addItems(self.iN)
        self.item3.addItems(self.iN)
        self.item4.addItems(self.iN)
        self.maintab.setCurrentIndex(0)
        QtCore.QObject.connect(self.chooseTrainer, QtCore.SIGNAL("currentIndexChanged(int)"), self.changedTrainer)
        QtCore.QObject.connect(self.itemBool, QtCore.SIGNAL("clicked()"), self.changedTrType)
        QtCore.QObject.connect(self.attackBool, QtCore.SIGNAL("clicked()"), self.changedTrType)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.adjustPokes(0)
    def changedTrType(self):
        iBool = self.itemBool.isChecked()
        aBool = self.attackBool.isChecked()
        self.trtype = (iBool << 1)+(aBool)
    def adjustPokes(self, num):
        current = self.maintab.count()-2
        if num == current:
            return
        if num < current:
            for n in range(num,current):
                self.maintab.removeTab(self.maintab.count()-1)
                delattr(self, "tab" + str(n))
            return

        for n in range(current,num):
            setattr(self, "tab" + str(n), QtGui.QWidget())
            getattr(self, "tab" + str(n)).setObjectName("tab"+str(n))
            setattr(self, "gridLayoutWidget_" + str(n) + "_3", QtGui.QWidget(getattr(self, "tab" + str(n))))
            getattr(self, "gridLayoutWidget_" + str(n) + "_3").setGeometry(QtCore.QRect(50, 50, 536, 236))
            getattr(self, "gridLayoutWidget_" + str(n) + "_3").setObjectName("gridLayoutWidget_"+str(n)+"_3")
            setattr(self, "gridLayout_" + str(n) + "_3", QtGui.QGridLayout(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "gridLayout_" + str(n) + "_3").setObjectName("gridLayout_"+str(n)+"_3")
            setattr(self, "spec" + str(n), QtGui.QComboBox(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "spec" + str(n)).setObjectName("spec"+str(n))
            getattr(self, "spec" + str(n)).addItems(self.pN)
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "spec" + str(n)), 0, 1, 1, 1)
            setattr(self, "label_" + str(n) + "_15", QtGui.QLabel(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "label_" + str(n) + "_15").setObjectName("label_"+str(n)+"_15")
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "label_" + str(n) + "_15"), 0, 0, 1, 1)
            setattr(self, "label_" + str(n) + "_16", QtGui.QLabel(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "label_" + str(n) + "_16").setObjectName("label_"+str(n)+"_16")
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "label_" + str(n) + "_16"), 1, 0, 1, 1)
            setattr(self, "pokelvl" + str(n), QtGui.QSpinBox(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "pokelvl" + str(n)).setObjectName("pokelvl"+str(n))
            getattr(self, "pokelvl" + str(n)).setMaximum(255)
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "pokelvl" + str(n)), 1, 1, 1, 1)
            setattr(self, "label_" + str(n) + "_17", QtGui.QLabel(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "label_" + str(n) + "_17").setObjectName("label_"+str(n)+"_17")
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "label_" + str(n) + "_17"), 2, 0, 1, 1)
            setattr(self, "pokeItem" + str(n), QtGui.QComboBox(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "pokeItem" + str(n)).setObjectName("pokeItem"+str(n))
            getattr(self, "pokeItem" + str(n)).addItems(self.iN)
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "pokeItem" + str(n)), 2, 1, 1, 1)
            setattr(self, "pu0_" + str(n), QtGui.QSpinBox(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "pu0_" + str(n)).setMaximum(255)
            getattr(self, "pu0_" + str(n)).setObjectName("pu0_"+str(n))
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "pu0_" + str(n)), 4, 1, 1, 1)
            setattr(self, "form_" + str(n), QtGui.QSpinBox(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "form_" + str(n)).setMaximum(15)
            getattr(self, "form_" + str(n)).setObjectName("form_"+str(n))
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "form_" + str(n)), 5, 1, 1, 1)
            setattr(self, "label_" + str(n) + "_form", QtGui.QLabel(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "label_" + str(n) + "_form").setObjectName("label_"+str(n)+"_form")
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "label_" + str(n) + "_form"), 5, 0, 1, 1)
            setattr(self, "label_" + str(n) + "_18", QtGui.QLabel(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "label_" + str(n) + "_18").setObjectName("label_"+str(n)+"_18")
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "label_" + str(n) + "_18"), 3, 0, 1, 1)
            setattr(self, "label_" + str(n) + "_28", QtGui.QLabel(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "label_" + str(n) + "_28").setObjectName("label_"+str(n)+"_28")
            getattr(self, "gridLayout_" + str(n) + "_3").addWidget(getattr(self, "label_" + str(n) + "_28"), 4, 0, 1, 1)
            setattr(self, "gridLayout_" + str(n) + "_5", QtGui.QGridLayout())
            getattr(self, "gridLayout_" + str(n) + "_5").setObjectName("gridLayout_"+str(n)+"_5")
            setattr(self, "attack" + str(n) + "_1", QtGui.QComboBox(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "attack" + str(n) + "_1").setObjectName("attack"+str(n)+"_1")
            getattr(self, "attack" + str(n) + "_1").addItems(self.mN)
            getattr(self, "gridLayout_" + str(n) + "_5").addWidget(getattr(self, "attack" + str(n) + "_1"), 0, 0, 1, 1)
            setattr(self, "attack" + str(n) + "_2", QtGui.QComboBox(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "attack" + str(n) + "_2").setObjectName("attack"+str(n)+"_2")
            getattr(self, "attack" + str(n) + "_2").addItems(self.mN)
            getattr(self, "gridLayout_" + str(n) + "_5").addWidget(getattr(self, "attack" + str(n) + "_2"), 0, 1, 1, 1)
            setattr(self, "attack" + str(n) + "_3", QtGui.QComboBox(getattr(self, "gridLayoutWidget_" + str(n) + "_3")))
            getattr(self, "attack" + str(n) + "_3").setObjectName("attack"+str(n)+"_3")
            getattr(self, "attack" + str(n) + "_3").addItems(self.mN)
            getattr(self, "gridLayout_" + str(n) + "_5").addWidget(getattr(self, "attack"+str(n)+"_3"), 1, 0, 1, 1)
            setattr(self, "attack" + str(n) + "_4", QtGui.QComboBox(getattr(self, "gridLayoutWidget_"+str(n)+"_3")))
            getattr(self, "attack" + str(n) + "_4").setObjectName("attack" + str(n) + "_4")
            getattr(self, "attack" + str(n) + "_4").addItems(self.mN)
            getattr(self, "gridLayout_" + str(n) + "_5").addWidget(getattr(self, "attack" + str(n) + "_4"), 1, 1, 1, 1)
            getattr(self, "gridLayout_" + str(n) + "_3").addLayout(getattr(self, "gridLayout_" + str(n) + "_5"), 3, 1, 1, 1)
            getattr(self, "label_" + str(n) + "_15").setText("Pokemon")
            getattr(self, "label_" + str(n) + "_16").setText("Level")
            getattr(self, "label_" + str(n) + "_17").setText("Item")
            getattr(self, "label_" + str(n) + "_18").setText("Extra Attacks")
            getattr(self, "label_" + str(n) + "_28").setText("u0")
            getattr(self, "label_" + str(n) + "_form").setText("Form #")
            self.maintab.addTab(getattr(self, "tab" + str(n)), "Pokemon " + str(n + 1))
    def changedTrainer(self,n):
        num=self.chooseTrainer.currentIndex()
        bytes = []
        for chr in self.trNarc.gmif.files[num]:
            bytes.append(ord(chr))
        trainer = bytereader.byteReader(bytes)
        bytes = []
        for chr in self.trPokeNarc.gmif.files[num]:
            bytes.append(ord(chr))
        pokemon = bytereader.byteReader(bytes)
        currenttrainer = []
        for i in range(0,0x14):
            currenttrainer.append(trainer.ReadByte())

        self.trtype = currenttrainer[0]
        self.itemBool.setChecked((self.trtype&2)>>1)
        self.attackBool.setChecked(self.trtype&1)
        self.class_2.setCurrentIndex(currenttrainer[1]+(currenttrainer[2] << 8))
        self.pokenum.setValue(currenttrainer[0x3])
        self.numPokes = currenttrainer[0x3]
        self.uc.setValue(currenttrainer[0xc])
        self.ud.setValue(currenttrainer[0xd])
        self.ue.setValue(currenttrainer[0xe])
        self.uf.setValue(currenttrainer[0xf])
        self.doubleBool.setChecked(currenttrainer[0x10]/2)
        self.u11.setValue(currenttrainer[0x11])
        self.u12.setValue(currenttrainer[0x12])
        self.u13.setValue(currenttrainer[0x13])
        self.item1.setCurrentIndex(currenttrainer[4] + (currenttrainer[5] << 8))
        self.item2.setCurrentIndex(currenttrainer[6] + (currenttrainer[7] << 8))
        self.item3.setCurrentIndex(currenttrainer[8] + (currenttrainer[9] << 8))
        self.item4.setCurrentIndex(currenttrainer[0xa]+(currenttrainer[0xb]<<8))

        self.trname.setText(self.trNames.strlist[self.chooseTrainer.currentIndex()])
        self.adjustPokes(self.numPokes)
        gs = False
        pt = False
        if (mw.ID== 0x5353) or (mw.ID== 0x4748):
            gs = True
        elif mw.ID== 0x4c50:
            pt = True
        if self.trtype == 0:
            dsiz = 0x6
        elif self.trtype == 1:
            dsiz = 0xe
        elif self.trtype == 2:
            dsiz = 0x8
        elif self.trtype == 3:
            dsiz = 0x10
        if pt or gs:
            dsiz += 2
        pokes = []
        for i in range(0,self.numPokes):
            pokes.append([])
            for j in range(0,dsiz):
                try:
                    pokes[i].append(pokemon.ReadByte())
                except:
                    print "",
        for h in range(0,self.numPokes):
            cPoke = bytereader.byteReader(pokes[h])
            eval("self.pu0_"+str(h)+".setValue(cPoke.ReadByte())")
            cPoke.Seek(2)
            eval("self.pokelvl"+str(h)+".setValue(cPoke.ReadByte())")
            cPoke.Seek(4)
            pu1 = cPoke.ReadUInt16()
            eval("self.spec"+str(h)+".setCurrentIndex(pu1&1023)")
            eval("self.form_"+str(h)+".setValue(pu1>>10)")
            if (self.trtype == 3) or (self.trtype == 2):
                eval("self.pokeItem"+str(h)+".setEnabled(True)")
                eval("self.pokeItem"+str(h)+".setCurrentIndex(cPoke.ReadUInt16())")
            else:
                eval("self.pokeItem"+str(h)+".setCurrentIndex(0)")
                eval("self.pokeItem"+str(h)+".setEnabled(False)")
            if (self.trtype == 1) or (self.trtype == 3):
                for i in range(1,5):
                    eval("self.attack"+str(h)+"_"+str(i)+".setEnabled(True)")
                    eval("self.attack"+str(h)+"_"+str(i)+".setCurrentIndex(cPoke.ReadUInt16())")
            else:
                for i in range(1,5):
                    eval("self.attack"+str(h)+"_"+str(i)+".setCurrentIndex(0)")
                    eval("self.attack"+str(h)+"_"+str(i)+".setEnabled(False)")

    def saveTrainer(self):
        num=self.chooseTrainer.currentIndex()
        trainer = bytereader.byteWriter()
        pokemon = bytereader.byteWriter()


        trainer.WriteByte(self.itemBool.isChecked()*2 + self.attackBool.isChecked())
        trainer.WriteUInt16(self.class_2.currentIndex())
        trainer.WriteByte(self.pokenum.value())
        trainer.WriteUInt16(self.item1.currentIndex())
        trainer.WriteUInt16(self.item2.currentIndex())
        trainer.WriteUInt16(self.item3.currentIndex())
        trainer.WriteUInt16(self.item4.currentIndex())
        trainer.WriteByte(self.uc.value())
        trainer.WriteByte(self.ud.value())
        trainer.WriteByte(self.ue.value())
        trainer.WriteByte(self.uf.value())
        trainer.WriteByte(self.doubleBool.isChecked()*2)
        trainer.WriteByte(self.u11.value())
        trainer.WriteByte(self.u12.value())
        trainer.WriteByte(self.u13.value())

        gs = False
        pt = False
        if (mw.ID== 0x5353) or (mw.ID== 0x4748):
            gs = True
        elif mw.ID== 0x4c50:
            pt = True
        if self.trtype == 0:
            dsiz = 0x6
        elif self.trtype == 1:
            dsiz = 0xe
        elif self.trtype == 2:
            dsiz = 0x8
        elif self.trtype == 3:
            dsiz = 0x10
        if pt or gs:
            dsiz += 2

        for h in range(0,self.numPokes):
            start = len(pokemon.a)
            pu1 = eval("self.spec"+str(h)+".currentIndex()")+(eval("self.form_"+str(h)+".value()")<<10)
            eval("pokemon.WriteUInt16(self.pu0_"+str(h)+".value())")
            eval("pokemon.WriteUInt16(self.pokelvl"+str(h)+".value())")
            eval("pokemon.WriteUInt16(pu1)")
            if (self.trtype == 3) or (self.trtype == 2):
                eval("pokemon.WriteUInt16(self.pokeItem"+str(h)+".currentIndex())")
            if (self.trtype == 1) or (self.trtype == 3):
                for i in range(1,5):
                    eval("pokemon.WriteUInt16(self.attack"+str(h)+"_"+str(i)+".currentIndex())")
            csiz = len(pokemon.a)-start
            for c in range(0,dsiz-csiz):
                pokemon.WriteByte(0)
        tTr = ""
        pTr = ""
        for t in trainer.ReturnData():
            tTr+=chr(int(t))
        self.trNarc.replaceFile(num, tTr)
        for p in pokemon.ReturnData():
            pTr+=chr(int(p))
        self.trPokeNarc.replaceFile(num, pTr)
        WriteTrNarc(self.trNarc)
        print "Trainer Data NARC written successfully!"
        WriteTrPokeNarc(self.trPokeNarc)
        print "Trainer Pokemon NARC written successfully!"
        self.saveText()
    def saveText(self):
        textStr = self.trname.text()
        self.trNames.strlist[self.chooseTrainer.currentIndex()] = unicode(textStr)
        p=texttopoke.Makefile(self.trNames.strlist,False,True)
        encrypt = poketext.PokeTextData(p)
        encrypt.SetKey(0xD00E)
        encrypt.encrypt()
        self.msgNarc.replaceFile(mw.TN[12], encrypt.getStr())
        WriteMsgNarc(self.msgNarc)
        print "Wrote Trainer Name to Text NARC successfully!"#"""
class LoadDlg(QDialog, ui_open.Ui_Dialog):
    def __init__(self,parent=None):
        super(LoadDlg,self).__init__(parent)
        self.setupUi(self)
        self.loadable = []
        self.newload = []
        self.loads = {}
        for item in os.listdir(os.curdir):
            if item.startswith("tmp_"):
                self.loadable.append(item)
                self.loads[item] = strip_prefix(item, "tmp_") + ".nds"
            if ".nds" in item and item not in self.loads.values():
                self.newload.append(item)
                self.loads[item] = item
        self.romchoose.clear()
        for l in xrange(len(self.loadable)):
            self.loadable[l] = "(Saved) "+self.loads[self.loadable[l]]
        self.romchoose.addItems(self.loadable)
        self.romchoose.addItems(self.newload)
        return
    def accept(self):
        if not self.romchoose.currentItem():
            return romerror.noValue()
        else:
            mw.nameEdit.setText(
                strip_prefix(str(self.romchoose.currentItem().text()), "(Saved) "))
        self.close()
    def checkROM(self):
        self.choicename.setText(
            "ROM Name: " + strip_prefix(str(self.romchoose.currentItem().text()), "(Saved) "))

def strip_prefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s

app = QApplication(sys.argv)
mw = MainWindow()
mw.show()
app.exec_()
#else:
#   QMessageBox.warning(None,"Phone Log", QString("Database Error: %1").arg(db.lastError().text()))

