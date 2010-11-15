#!/usr/bin/env python
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
		self.rom=execute.NDSFILES(unicode(self.nameEdit.text()))
		self.rom.dump()
		try:
			self.ID=getROMID()
		except IOError:
			romerror.noData(self)
			del(self.rom)
			return
		self.lang = getLang()
		self.other=("Pokemon Center","Mart", "GYM")
		self.DT={}
		if self.ID == 0x5353:
			self.romname="Soul Silver"
			if self.lang==0x4A:
				self.Of=(0xE56F0,10000 ,0)
				self.TN=(427,724,711,219,739,232,801,799,803,792,790,720,719)
				self.DT={"move":739,"contest":207,"type":724}
			else:
				self.Of=(0xE56F0,10000 ,0)
				self.TN=(279,735,720,222,750,237,814,812,803,823,802,730,729)
				self.DT={"move":750,"contest":207,"type":735}
		elif self.ID == 0x4748:
			self.romname="Heart Gold"
			if self.lang==0x4A:
				self.Of=(0xE56F0,501 ,1050 )
				self.TN=(427,724,711,219,739,232,801,799,803,791,790,720,719)
				self.DT={"move":739,"contest":207,"type":724}
			else:
				self.Of=(0xE56F0,10000 ,0)
				self.TN=(279,735,720,222,750,237,814,812,803,823,802,730,729)#location names = 279?
				self.DT={"move":750,"contest":207,"type":735}
		elif self.ID == 0x4C50:
			self.romname="Platinum"
			self.DT={"move":647,"contest":208,"type":624}
			if self.lang==0x44:
				self.Of=(0xE6074,501, 1050 )
				self.TN=(433,624,610,392,647,412,709,707,720,706,697,619,618,613)
			elif self.lang==0x45:#EN
				self.Of=(0xE601C,501, 1050 )
				self.TN=(433,624,610,392,647,412,709,707,718,706,697,619,618,613 )
				self.DT={"move":647,"contest":208,"type":624}
			elif self.lang==0x46:
				self.Of=(0xE60A4,501, 1050 )
				self.TN=(433,624,610,392,647,412,709,707,719,706,697,619,618,613)
			elif self.lang==0x49:
				self.Of=(0xE6038,501, 1050 )
				self.TN=(433,624,610,392,647,412,709,707,721,706,697,619,618,613)
			elif self.lang==0x4A:
				self.Of=(0xE56F0,501 ,1050 )
				self.TN=(427,616,604,390,636,408,696,694,698,693,685,619,618,613)#change tr
				self.DT={"move":636,"contest":207,"type":616}
			elif self.lang==0x4B:
				self.Of=(0xE6AA4,501, 1050 )
				self.TN=(428,617,605,390,637,408,699,697,696,701,687,619,618,613)#change tr
			elif self.lang==0x53:
				self.Of=(0xE60B0,501, 1050 )
				self.TN=(433,624,610,392,647,412,709,707,722,706,697,619,618,613 )
		elif self.ID== 0x50:
			self.romname="Pearl"
			if self.lang==0x4A:
				self.Of=(0xF0C2C, )
				self.TN=(374,555,544,341,575,356,606,605,607,602,600,560,559,555)#change tr
			elif self.lang==0x45:
				self.Of=(0xEEDBC, )
				self.TN=(382,565,552,344,588,362,620,619,621,616,614,560,559,555)
			elif self.lang==0x44:
				self.Of=(0xEEDCC, )
				self.TN=(382,565,552,344,588,362,620,619,621,616,614,560,559,555)
			elif self.lang==0x46:
				self.Of=(0xEEDFC, )
				self.TN=(382,565,552,344,588,362,620,619,621,616,614,560,559,555)
			elif self.lang==0x49:
				self.Of=(0xEED70, )
				self.TN=(382,565,552,344,588,362,620,619,621,616,614,560,559,555)
			elif self.lang==0x53:
				self.Of=(0xEEE08, )
				self.TN=(382,565,552,344,588,362,620,619,621,616,614,560,559,555)
			elif self.lang==0x4B:
				self.Of=(0xEA408, )
				self.TN=(376,557,546,342,577,357,608,606,609,603,602,560,559,555)#change tr
		elif self.ID==0x44:
			self.romname="Diamond"
			if self.lang==0x4A:
				self.Of=(0xF0C28, )
				self.TN=(374,555,544,341,575,356,606,605,607,601,600,560,559,555)#change tr
			elif self.lang==0x45:
				self.Of=(0xEEDBC, )
				self.TN=(382,565,552,344,588,362,620,619,621,615,614,560,559,555)
			elif self.lang==0x44:
				self.Of=(0xEEDCC, )
				self.TN=(382,565,552,344,588,362,620,619,621,615,614,560,559,555)
			elif self.lang==0x46:
				self.Of=(0xEEDFC, )
				self.TN=(382,565,552,344,588,362,620,619,621,615,614,560,559,555)
			elif self.lang==0x49:
				self.Of=(0xEED70, )
				self.TN=(382,565,552,344,588,362,620,619,621,615,614,560,559,555)
			elif self.lang==0x53:
				self.Of=(0xEEE08, )
				self.TN=(382,565,552,344,588,362,620,619,621,615,614,560,559,555)
			elif self.lang==0x4B:
				self.Of=(0xEA408, )
				self.TN=(376,557,546,342,577,357,608,606,609,603,602,560,559,555)#change tr
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
		self.personal=ReadPersonalNarc()
		self.archive = ReadMsgNarc()
		self.moves=ReadWOTblNarc()
		self.evos=ReadEvoNarc()
		self.temp=[]
		self.dataids=[]
		for i in range(0,82):
			self.temp.append(0)
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
		self.move1.addItems(binary.strlist)
		self.move2.addItems(binary.strlist)
		self.move3.addItems(binary.strlist)
		self.move4.addItems(binary.strlist)
		self.move5.addItems(binary.strlist)
		self.move6.addItems(binary.strlist)
		self.move7.addItems(binary.strlist)
		self.move8.addItems(binary.strlist)
		self.move9.addItems(binary.strlist)
		self.move10.addItems(binary.strlist)
		self.move11.addItems(binary.strlist)
		self.move12.addItems(binary.strlist)
		self.move13.addItems(binary.strlist)
		self.move14.addItems(binary.strlist)
		self.move15.addItems(binary.strlist)
		self.move16.addItems(binary.strlist)
		self.move17.addItems(binary.strlist)
		self.move18.addItems(binary.strlist)
		self.move19.addItems(binary.strlist)
		self.move20.addItems(binary.strlist)
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
		self.evoPkm1.addItems(binary.strlist)
		self.evoPkm2.addItems(binary.strlist)
		self.evoPkm3.addItems(binary.strlist)
		self.evoPkm4.addItems(binary.strlist)
		self.evoPkm5.addItems(binary.strlist)
		self.evoPkm6.addItems(binary.strlist)
		self.evoPkm7.addItems(binary.strlist)
		self.evoReqPkm1.addItems(binary.strlist)
		self.evoReqPkm2.addItems(binary.strlist)
		self.evoReqPkm3.addItems(binary.strlist)
		self.evoReqPkm4.addItems(binary.strlist)
		self.evoReqPkm5.addItems(binary.strlist)
		self.evoReqPkm6.addItems(binary.strlist)
		self.evoReqPkm7.addItems(binary.strlist)
		self.romname=self.romnameLabel.text()+mw.romname
		self.romnameLabel.setText(self.romname)
		self.tmlist=(self.tm1,self.tm2,self.tm3,self.tm4,self.tm5,self.tm6,self.tm7,self.tm8,self.tm9,self.tm10,self.tm11,self.tm12,self.tm13,self.tm14,self.tm15,self.tm16,self.tm17,self.tm18,self.tm19,self.tm20,self.tm21,self.tm22,self.tm23,self.tm24,self.tm25,self.tm26,self.tm27,self.tm28,self.tm29,self.tm30,self.tm31,self.tm32,self.tm33,self.tm34,self.tm35,self.tm36,self.tm37,self.tm38,self.tm39,self.tm40,self.tm41,self.tm42,self.tm43,self.tm44,self.tm45,self.tm46,self.tm47,self.tm48,self.tm49,self.tm50,self.tm51,self.tm52,self.tm53,self.tm54,self.tm55,self.tm56,self.tm57,self.tm58,self.tm59,self.tm60,self.tm61,self.tm62,self.tm63,self.tm64,self.tm65,self.tm66,self.tm67,self.tm68,self.tm69,self.tm70,self.tm71,self.tm72,self.tm73,self.tm74,self.tm75,self.tm76,self.tm77,self.tm78,self.tm79,self.tm80,self.tm81,self.tm82,self.tm83,self.tm84,self.tm85,self.tm86,self.tm87,self.tm88,self.tm89,self.tm90,self.tm91,self.tm92)
		self.hmlist=(self.hm1,self.hm2,self.hm3,self.hm4,self.hm5,self.hm6,self.hm7,self.hm8)
		self.movelist=(self.move1,self.move2,self.move3,self.move4,self.move5,self.move6,self.move7,self.move8,self.move9,self.move10,self.move11,self.move12,self.move13,self.move14,self.move15,self.move16,self.move17,self.move18,self.move19,self.move20)
		self.movelvllist=(self.moveLvl1,self.moveLvl2,self.moveLvl3,self.moveLvl4,self.moveLvl5,self.moveLvl6,self.moveLvl7,self.moveLvl8,self.moveLvl9,self.moveLvl10,self.moveLvl11,self.moveLvl12,self.moveLvl13,self.moveLvl14,self.moveLvl15,self.moveLvl16,self.moveLvl17,self.moveLvl18,self.moveLvl19,self.moveLvl20)
		self.evotypes=(self.evoType1,self.evoType2,self.evoType3,self.evoType4,self.evoType5,self.evoType6,self.evoType7)
		self.evopkms=(self.evoPkm1,self.evoPkm2,self.evoPkm3,self.evoPkm4,self.evoPkm5,self.evoPkm6,self.evoPkm7)
		self.choosePokemon.setCurrentIndex(0)
		#self.updateUi()
		#self.extractToSql()
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
			exec("lvl = self.moveLvl"+str(m)+".value()")
			exec("move = self.move"+str(m)+".currentIndex()")
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
			exec("evo = self.evoType"+str(i)+".currentIndex()")
			param = 0
			if evo in (4,8,9,10,11,12,13,14,21,22):
				exec("param = self.evoLvl"+str(i)+".value()")
			elif evo in (6,7,16,17,18,19):
				exec("param = self.evoItem"+str(i)+".currentIndex()")
			elif evo==0x14:
				exec("param = self.evoAtk"+str(i)+".currentIndex()")
			elif evo==0x15:
				exec("param = self.evoReqPkm"+str(i)+".currentIndex()")
			exec("poke = self.evoPkm"+str(i)+".currentIndex()") 
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
		self.checkBoxHandle(self.tm1,self.temp[28]&1) 
		self.checkBoxHandle(self.tm2,(self.temp[28]>>1)&1)
		self.checkBoxHandle(self.tm3,(self.temp[28]>>2)&1)
		self.checkBoxHandle(self.tm4,(self.temp[28]>>3)&1)
		self.checkBoxHandle(self.tm5,(self.temp[28]>>4)&1)
		self.checkBoxHandle(self.tm6,(self.temp[28]>>5)&1)
		self.checkBoxHandle(self.tm7,(self.temp[28]>>6)&1)
		self.checkBoxHandle(self.tm8,(self.temp[28]>>7)&1)
		self.checkBoxHandle(self.tm9,self.temp[29]&1) 
		self.checkBoxHandle(self.tm10,(self.temp[29]>>1)&1)
		self.checkBoxHandle(self.tm11,(self.temp[29]>>2)&1)
		self.checkBoxHandle(self.tm12,(self.temp[29]>>3)&1)
		self.checkBoxHandle(self.tm13,(self.temp[29]>>4)&1)
		self.checkBoxHandle(self.tm14,(self.temp[29]>>5)&1)
		self.checkBoxHandle(self.tm15,(self.temp[29]>>6)&1)
		self.checkBoxHandle(self.tm16,(self.temp[29]>>7)&1)
		self.checkBoxHandle(self.tm17,self.temp[30]&1) 
		self.checkBoxHandle(self.tm18,(self.temp[30]>>1)&1)
		self.checkBoxHandle(self.tm19,(self.temp[30]>>2)&1)
		self.checkBoxHandle(self.tm20,(self.temp[30]>>3)&1)
		self.checkBoxHandle(self.tm21,(self.temp[30]>>4)&1)
		self.checkBoxHandle(self.tm22,(self.temp[30]>>5)&1)
		self.checkBoxHandle(self.tm23,(self.temp[30]>>6)&1)
		self.checkBoxHandle(self.tm24,(self.temp[30]>>7)&1)
		self.checkBoxHandle(self.tm25,self.temp[31]&1) 
		self.checkBoxHandle(self.tm26,(self.temp[31]>>1)&1)
		self.checkBoxHandle(self.tm27,(self.temp[31]>>2)&1)
		self.checkBoxHandle(self.tm28,(self.temp[31]>>3)&1)
		self.checkBoxHandle(self.tm29,(self.temp[31]>>4)&1)
		self.checkBoxHandle(self.tm30,(self.temp[31]>>5)&1)
		self.checkBoxHandle(self.tm31,(self.temp[31]>>6)&1)
		self.checkBoxHandle(self.tm32,(self.temp[31]>>7)&1)
		self.checkBoxHandle(self.tm33,self.temp[32]&1) 
		self.checkBoxHandle(self.tm34,(self.temp[32]>>1)&1)
		self.checkBoxHandle(self.tm35,(self.temp[32]>>2)&1)
		self.checkBoxHandle(self.tm36,(self.temp[32]>>3)&1)
		self.checkBoxHandle(self.tm37,(self.temp[32]>>4)&1)
		self.checkBoxHandle(self.tm38,(self.temp[32]>>5)&1)
		self.checkBoxHandle(self.tm39,(self.temp[32]>>6)&1)
		self.checkBoxHandle(self.tm40,(self.temp[32]>>7)&1)
		self.checkBoxHandle(self.tm41,self.temp[33]&1) 
		self.checkBoxHandle(self.tm42,(self.temp[33]>>1)&1)
		self.checkBoxHandle(self.tm43,(self.temp[33]>>2)&1)
		self.checkBoxHandle(self.tm44,(self.temp[33]>>3)&1)
		self.checkBoxHandle(self.tm45,(self.temp[33]>>4)&1)
		self.checkBoxHandle(self.tm46,(self.temp[33]>>5)&1)
		self.checkBoxHandle(self.tm47,(self.temp[33]>>6)&1)
		self.checkBoxHandle(self.tm48,(self.temp[33]>>7)&1)
		self.checkBoxHandle(self.tm49,self.temp[34]&1) 
		self.checkBoxHandle(self.tm50,(self.temp[34]>>1)&1)
		self.checkBoxHandle(self.tm51,(self.temp[34]>>2)&1)
		self.checkBoxHandle(self.tm52,(self.temp[34]>>3)&1)
		self.checkBoxHandle(self.tm53,(self.temp[34]>>4)&1)
		self.checkBoxHandle(self.tm54,(self.temp[34]>>5)&1)
		self.checkBoxHandle(self.tm55,(self.temp[34]>>6)&1)
		self.checkBoxHandle(self.tm56,(self.temp[34]>>7)&1)
		self.checkBoxHandle(self.tm57,self.temp[35]&1) 
		self.checkBoxHandle(self.tm58,(self.temp[35]>>1)&1)
		self.checkBoxHandle(self.tm59,(self.temp[35]>>2)&1)
		self.checkBoxHandle(self.tm60,(self.temp[35]>>3)&1)
		self.checkBoxHandle(self.tm61,(self.temp[35]>>4)&1)
		self.checkBoxHandle(self.tm62,(self.temp[35]>>5)&1)
		self.checkBoxHandle(self.tm63,(self.temp[35]>>6)&1)
		self.checkBoxHandle(self.tm64,(self.temp[35]>>7)&1)
		self.checkBoxHandle(self.tm65,self.temp[36]&1) 
		self.checkBoxHandle(self.tm66,(self.temp[36]>>1)&1)
		self.checkBoxHandle(self.tm67,(self.temp[36]>>2)&1)
		self.checkBoxHandle(self.tm68,(self.temp[36]>>3)&1)
		self.checkBoxHandle(self.tm69,(self.temp[36]>>4)&1)
		self.checkBoxHandle(self.tm70,(self.temp[36]>>5)&1)
		self.checkBoxHandle(self.tm71,(self.temp[36]>>6)&1)
		self.checkBoxHandle(self.tm72,(self.temp[36]>>7)&1)
		self.checkBoxHandle(self.tm73,self.temp[37]&1) 
		self.checkBoxHandle(self.tm74,(self.temp[37]>>1)&1)
		self.checkBoxHandle(self.tm75,(self.temp[37]>>2)&1)
		self.checkBoxHandle(self.tm76,(self.temp[37]>>3)&1)
		self.checkBoxHandle(self.tm77,(self.temp[37]>>4)&1)
		self.checkBoxHandle(self.tm78,(self.temp[37]>>5)&1)
		self.checkBoxHandle(self.tm79,(self.temp[37]>>6)&1)
		self.checkBoxHandle(self.tm80,(self.temp[37]>>7)&1)
		self.checkBoxHandle(self.tm81,self.temp[38]&1) 
		self.checkBoxHandle(self.tm82,(self.temp[38]>>1)&1)
		self.checkBoxHandle(self.tm83,(self.temp[38]>>2)&1)
		self.checkBoxHandle(self.tm84,(self.temp[38]>>3)&1)
		self.checkBoxHandle(self.tm85,(self.temp[38]>>4)&1)
		self.checkBoxHandle(self.tm86,(self.temp[38]>>5)&1)
		self.checkBoxHandle(self.tm87,(self.temp[38]>>6)&1)
		self.checkBoxHandle(self.tm88,(self.temp[38]>>7)&1)
		self.checkBoxHandle(self.tm89,self.temp[39]&1) 
		self.checkBoxHandle(self.tm90,(self.temp[39]>>1)&1)
		self.checkBoxHandle(self.tm91,(self.temp[39]>>2)&1)
		self.checkBoxHandle(self.tm92,(self.temp[39]>>3)&1)
		self.checkBoxHandle(self.hm1,(self.temp[39]>>4)&1) 
		self.checkBoxHandle(self.hm2,(self.temp[39]>>5)&1)
		self.checkBoxHandle(self.hm3,(self.temp[39]>>6)&1)
		self.checkBoxHandle(self.hm4,(self.temp[39]>>7)&1)
		self.checkBoxHandle(self.hm5,(self.temp[40])&1)
		self.checkBoxHandle(self.hm6,(self.temp[40]>>1)&1)
		self.checkBoxHandle(self.hm7,(self.temp[40]>>2)&1)
		self.checkBoxHandle(self.hm8,(self.temp[40]>>3)&1)
		self.moveLvl1.setValue(self.temp[41]>>9)
		self.moveLvl2.setValue(self.temp[42]>>9)
		self.moveLvl3.setValue(self.temp[43]>>9)
		self.moveLvl4.setValue(self.temp[44]>>9)
		self.moveLvl5.setValue(self.temp[45]>>9)
		self.moveLvl6.setValue(self.temp[46]>>9)
		self.moveLvl7.setValue(self.temp[47]>>9)
		self.moveLvl8.setValue(self.temp[48]>>9)
		self.moveLvl9.setValue(self.temp[49]>>9)
		self.moveLvl10.setValue(self.temp[50]>>9)
		self.moveLvl11.setValue(self.temp[51]>>9)
		self.moveLvl12.setValue(self.temp[52]>>9)
		self.moveLvl13.setValue(self.temp[53]>>9)
		self.moveLvl14.setValue(self.temp[54]>>9)
		self.moveLvl15.setValue(self.temp[55]>>9)
		self.moveLvl16.setValue(self.temp[56]>>9)
		self.moveLvl17.setValue(self.temp[57]>>9)
		self.moveLvl18.setValue(self.temp[58]>>9)
		self.moveLvl19.setValue(self.temp[59]>>9)
		self.moveLvl20.setValue(self.temp[60]>>9)
		self.move1.setCurrentIndex(self.temp[41]&0x1FF)
		self.move2.setCurrentIndex(self.temp[42]&0x1FF)
		self.move3.setCurrentIndex(self.temp[43]&0x1FF)
		self.move4.setCurrentIndex(self.temp[44]&0x1FF)
		self.move5.setCurrentIndex(self.temp[45]&0x1FF)
		self.move6.setCurrentIndex(self.temp[46]&0x1FF)
		self.move7.setCurrentIndex(self.temp[47]&0x1FF)
		self.move8.setCurrentIndex(self.temp[48]&0x1FF)
		self.move9.setCurrentIndex(self.temp[49]&0x1FF)
		self.move10.setCurrentIndex(self.temp[50]&0x1FF)
		self.move11.setCurrentIndex(self.temp[51]&0x1FF)
		self.move12.setCurrentIndex(self.temp[52]&0x1FF)
		self.move13.setCurrentIndex(self.temp[53]&0x1FF)
		self.move14.setCurrentIndex(self.temp[54]&0x1FF)
		self.move15.setCurrentIndex(self.temp[55]&0x1FF)
		self.move16.setCurrentIndex(self.temp[56]&0x1FF)
		self.move17.setCurrentIndex(self.temp[57]&0x1FF)
		self.move18.setCurrentIndex(self.temp[58]&0x1FF)
		self.move19.setCurrentIndex(self.temp[59]&0x1FF)
		self.move20.setCurrentIndex(self.temp[60]&0x1FF)
		evoreqs = ["evoAtk","evoItem","evoLvl","evoReqPkm"]
		for e in evoreqs:
			for i in range(1,8):
				eval("self."+e+str(i)+".setEnabled(False)")
	
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
		self.temp[0]=self.hpspinBox.value
	def updatedef(self,event=""):
		self.temp[0]=self.hpspinBox.value
	def updatespd(self,event=""):
		self.temp[0]=self.hpspinBox.value
	def updatespatk(self,event=""):
		self.temp[0]=self.hpspinBox.value
	def updatespdef(self,event=""):
		self.temp[0]=self.hpspinBox.value
	def extractToSql(self):
		"""print "Success ",
		db=QSqlDatabase.addDatabase("QMYSQL")
		db.setHostName("dbs.projectpokemon.org")
		db.setDatabaseName("pporg_dex")
		db.setUserName("pporgadmin")
		db.setPassword("HackingRulez!@#")
		if not db.open():
			QMessageBox.warning(None,"Phone Log", QString("Database Error: %1").arg(db.lastError().text()))
		else:
			print "Success Again"
		query=QSqlQuery()
		query.exec_("CREATE TABLE poke (natid INTEGER PRIMARY KEY UNIQUE NOT NULL,name VARCHAR(10) NOT NULL UTF)")
		print db.lastError().text()"""
		iL=""
		if mw.ID==0x5353:
			iL+="hgss"
		elif mw.ID==0x4748:
			iL+="hgss"
		elif mw.ID==0x4C50:
			iL+="pl"
		elif mw.ID==0x50:
			iL+="dp"
		elif mw.ID==0x44:
			iL+="dp"
		lL=chr(mw.lang).lower()
		sf=QFile(iL+"dex"+lL+".sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		temptext=poketext.PokeTextData(self.archive.gmif.files[791])
		temptext.decrypt()
		ts<<"SET SQL_MODE=\"NO_AUTO_VALUE_ON_ZERO\";\n"
		ts<<"DROP TABLE IF EXISTS `"+iL+"poke"+lL+"`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `"+iL+"poke"+lL+"` (\n"
		ts<<"  `natid` SMALLINT UNSIGNED,\n"
		ts<<"  `name` VARCHAR(20),\n"
		ts<<"  `height` VARCHAR(20),\n"
		ts<<"  `weight` VARCHAR(20),\n"
		ts<<"  `desc` TEXT,\n"
		ts<<"  `dflavortext` TEXT,\n"
		ts<<"  `numforms` TINYINT,\n"
		ts<<"  `pflavortext` TEXT,\n"
		ts<<"  `stats` TINYINT,\n"
		ts<<"  PRIMARY KEY  (`natid`)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
	
		#Begin Inserting
		ts<<"INSERT INTO `"+iL+"poke"+lL+"` (`natid`,`name`,`height`,`weight`,`desc`,`dflavortext`,`numforms`, `pflavortext`,`stats`) VALUES\n"
		for i in range (1,494):
			self.choosePokemon.setCurrentIndex(i)
			ts<<"("<<i<<", '"<<unicode(self.pokeName.text()).title()<<"', '"<<self.height.text()<<"', '"<<self.weight.text()<<"', '"<<self.description.text()<<"', '"<<self.flavorText.toPlainText().replace("\\n"," ").replace("\\x0001", " ")<<"',"
			if i== 201:
				ts<<28<<","
			elif i== 412:
				ts<<3<<","
			elif i== 422 or i==423:
				ts<<2<<","
			else:
				ts<<self.chooseForm.count()<<","
			ts<<"'"+temptext.strlist[i].replace("\\n"," ").replace("\\x0001", " ")+"',"
			if i in (201, 412, 422, 423):
				ts<<1
			else:
				ts<<0	
			if i%50 == 0:
				print i
			if i==493:
				ts<<");"
			else:
				ts<<"),\n"
		sf.close() 
		sf=QFile(iL+"data"+lL)
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		#arm9filename=mw.rom.getFolder()+"/overlay/overlay_0005.bin"
		#mfh=QFile(arm9filename)
		#mfh.open(QIODevice.ReadOnly)
		#mds=QDataStream(mfh)
		#mds.setByteOrder(QDataStream.LittleEndian
		ts<<"DROP TABLE IF EXISTS `data"+iL+"`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `data"+iL+"` (\n"
		ts<<"  `dataid` SMALLINT UNSIGNED,\n"
		ts<<"  `natid` SMALLINT UNSIGNED,\n"
		ts<<"  `basehp` SMALLINT UNSIGNED,\n"
		ts<<"  `baseatk` SMALLINT UNSIGNED,\n"
		ts<<"  `basedef` SMALLINT UNSIGNED,\n"
		ts<<"  `basespd` SMALLINT UNSIGNED,\n"
		ts<<"  `basespatk` SMALLINT UNSIGNED,\n"
		ts<<"  `basespdef` SMALLINT UNSIGNED,\n"
		ts<<"  `type1` TINYINT,\n"
		ts<<"  `type2` TINYINT,\n"
		ts<<"  `item1` SMALLINT,\n"
		ts<<"  `item2` SMALLINT,\n"
		ts<<"  `ability1` SMALLINT,\n"
		ts<<"  `ability2` SMALLINT,\n"
		ts<<"  `steps` SMALLINT UNSIGNED,\n"
		ts<<"  `basehappiness` TINYINT UNSIGNED,\n"
		ts<<"  `runchance` TINYINT UNSIGNED,\n"
		ts<<"  `genderval` TINYINT UNSIGNED,\n"
		ts<<"  `maxexp` VARCHAR(20),\n"
		ts<<"  `baseexp` SMALLINT,\n"
		ts<<"  `egggroup1` TINYINT,\n"
		ts<<"  `egggroup2` TINYINT,\n"
		ts<<"  `catchrate` SMALLINT,\n"
		ts<<"  `hpev` TINYINT,\n"
		ts<<"  `atkev` TINYINT,\n"
		ts<<"  `defev` TINYINT,\n"
		ts<<"  `spdev` TINYINT,\n"
		ts<<"  `spatkev` TINYINT,\n"
		ts<<"  `spdefev` TINYINT,\n"
		ts<<"  `color` SMALLINT,\n"
		ts<<"  PRIMARY KEY  (`dataid`)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		
		#Begin Inserting Data
		ts<<"INSERT INTO `data"+iL+"` (`dataid`,`natid`,`basehp`,`baseatk`,`basedef`,`basespd`,`basespatk`,`basespdef`,`type1`,`type2`,`item1`,`item2`,`ability1`,`ability2`,`steps`,`basehappiness`,`runchance`,`genderval`,`maxexp`,`baseexp`,`egggroup1`, `egggroup2`,`catchrate`,`hpev`,`atkev`,`defev`,`spdev`,`spatkev`,`spdefev`,`color`) VALUES\n"
		for i in range (1,494):
			self.choosePokemon.setCurrentIndex(i)
			for j in range(0,len(self.dataids)):
				self.chooseForm.setCurrentIndex(j)
				ts<<"("<<self.dataids[j]<<","<<i<<","<<self.hpspinBox.value()
				ts<<","<<self.atkspinBox.value()<<","<<self.defspinBox.value()
				ts<<","<<self.spdspinBox.value()<<","<<self.spatkspinBox.value()
				ts<<","<<self.spdefspinBox.value()<<","
				ts<<self.type1.currentIndex()<<", "<<self.type2.currentIndex()<<", "
				ts<<self.heldItem1.currentIndex()<<", "<<self.heldItem2.currentIndex()<<","
				ts<<self.ability1.currentIndex()<<","<<self.ability2.currentIndex()<<","
				ts<<self.stepsMultiplier.value()*256<<","<<self.baseHappiness.value()<<","
				ts<<self.runChance.value()<<","<<self.genderVal.value()<<","
				ts<<"'"<<self.maxExp.currentText()<<"'"<<","<<self.baseExp.value()<<","
				ts<<self.eggGroup1.currentIndex()
				ts<<","<<self.eggGroup2.currentIndex()
				ts<<","<<self.catchRate.value()
				ts<<","<<self.hpEvs.value()<<","<<self.atkEvs.value()<<","<<self.defEvs.value()<<","<<self.spdEvs.value()<<","<<self.spatkEvs.value()<<","<<self.spdefEvs.value()
				ts<<","<<self.colorVal.value()
				if i%50 == 0:
					print i
				if i==493:
					ts<<");"
				else:
					ts<<"),\n"
		sf.close()
		sf=QFile(iL+"lvlmoves.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `lvlmv"+iL+"`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `lvlmv"+iL+"` (\n"
		ts<<"  `natid` SMALLINT UNSIGNED,\n"
		ts<<"  `form` TINYINT,\n"
		ts<<"  `lvl` TINYINT,\n"
		ts<<"  `moveid` SMALLINT\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
	
		#Begin Inserting
		ts<<"INSERT INTO `lvlmv"+iL+"` (`natid`,`form`, `lvl`, `moveid`) VALUES\n"
		for i in range (1,494):
			self.choosePokemon.setCurrentIndex(i)
			for j in range(0,len(self.dataids)):
				self.chooseForm.setCurrentIndex(j)
				for k in range(0,self.nummoves):
					ts<<"("<<i<<","<<j<<","<<self.movelvllist[k].value()<<","<<self.movelist[k].currentIndex()<<"),\n"
				if i%50 == 0:
					print i
				if i==493:
					print "done"
		sf.close()
		sf=QFile(iL+"forms"+lL+".sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `formnames"+iL+lL+"`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `formnames"+iL+lL+"` (\n"
		ts<<"  `natid` SMALLINT UNSIGNED,\n"
		ts<<"  `form` TINYINT,\n"
		ts<<"  `name` VARCHAR(30)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
	
		#Begin Inserting
		ts<<"INSERT INTO `formnamesdpkr` (`natid`,`form`, `name`) VALUES\n"
		binary=poketext.PokeTextData(self.archive.gmif.files[mw.TN[10]])
		binary.decrypt()
		for i in range (1,494):
			self.choosePokemon.setCurrentIndex(i)
			for j in range(0,len(self.dataids)):
				self.chooseForm.setCurrentIndex(j)
				if i not in (201, 412, 422, 423):
					ts<<"("<<i<<","<<j<<",'"<<self.chooseForm.currentText()<<"'),\n"
				else:
					if i in (422,  423):
						ts<<"("<<i<<","<<0<<",'"<<binary.strlist[15]<<"'),\n"
						ts<<"("<<i<<","<<1<<",'"<<binary.strlist[16]<<"'),\n"
					elif i == 412:
						ts<<"("<<i<<","<<0<<",'"<<binary.strlist[17]<<"'),\n"
						ts<<"("<<i<<","<<1<<",'"<<binary.strlist[18]<<"'),\n"
						ts<<"("<<i<<","<<2<<",'"<<binary.strlist[19]<<"'),\n"
					else:
						for k in range(0, 26):
							ts<<"("<<i<<","<<k<<",'"<<self.choosePokemon.currentText()+" "+chr(65+k)<<"'),\n"
						ts<<"("<<i<<","<<26<<",'"<<self.choosePokemon.currentText()+" !"<<"'),\n"
						ts<<"("<<i<<","<<27<<",'"<<self.choosePokemon.currentText()+" ?"<<"'),\n"
				if i%50 == 0:
					print i
				if i==493:
					print "done"
		sf.close()
		sf=QFile(iL+"tms.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `tms"+iL+"`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `tms"+iL+"` (\n"
		ts<<"  `natid` SMALLINT UNSIGNED,\n"
		ts<<"  `form` TINYINT,\n"
		ts<<"  `tm` TINYINT\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
	
		#Begin Inserting
		ts<<"INSERT INTO `tms"+iL+"` (`natid`,`form`, `tm`) VALUES\n"
		for i in range (1,494):
			self.choosePokemon.setCurrentIndex(i)
			for j in range(0,len(self.dataids)):
				self.chooseForm.setCurrentIndex(j)
				tempbool=False
				for k in range(0,92):
					if self.tmlist[k].isChecked():
						ts<<"("<<i<<","<<j<<","<<k+1<<"),\n"
				if i%50 == 0:
					print i
				if i==493:
					print "done"
		sf.close()
		#hm table
		sf=QFile(iL+"plhms.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `hms"+iL+"`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS hms"+iL+"` (\n"
		ts<<"  `natid` SMALLINT UNSIGNED,\n"
		ts<<"  `form` TINYINT,\n"
		ts<<"  `hm` TINYINT,\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
	
		#Begin Inserting
		ts<<"INSERT INTO `hms"+iL+"` (`natid`,`form`, `hm`) VALUES\n"
		for i in range (1,494):
			self.choosePokemon.setCurrentIndex(i)
			for j in range(0,len(self.dataids)):
				self.chooseForm.setCurrentIndex(j)
				for k in range(0,8):
					if self.hmlist[k].isChecked():
						ts<<"("<<i<<","<<j<<","<<k+1<<"),\n"
				if i%50 == 0:
					print i
				if i==493:
					print "done"
		sf.close()
		#Begin Platinum Tutor Moves
		"""tutorMoves=(0x123, 0xBD, 0xD2, 0xC4, 0xCD, 0x09, 0x07, 0x114, 0x8, 0x1BA, 0x191, 0x1D2, 0x17C, 0xAD, 0xB4, 0x13A, 0x10E, 0x11B, 0xC8, 0xF6, 0xEB, 0x144, 0x1AC, 0x19A, 0x19E, 0x1B9, 0xEF, 0x192, 0x14E, 0x189, 0x183, 0x154, 0x10F, 0x101, 0x11A, 0x185, 0x81, 0xFD)
		sf=QFile("pltutmvs.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		arm9filename=mw.rom.getFolder()+"/overlay/overlay_0005.bin"
		mfh=QFile(arm9filename)
		mfh.open(QIODevice.ReadOnly)
		mds=QDataStream(mfh)
		mds.setByteOrder(QDataStream.LittleEndian)
		ts<<"DROP TABLE IF EXISTS `tutormvspl`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `tutormvspl` (\n"
		ts<<"  `dataid` SMALLINT UNSIGNED,\n"
		ts<<"  `form` SMALLINT UNSIGNED,\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
	
		#Begin Inserting
		ts<<"INSERT INTO `tutormvspl` (`natid`,`form`, `hm`) VALUES\n"
		for i in range (1,494):
			self.choosePokemon.setCurrentIndex(i)
			for j in range(0,len(self.dataids)):
				self.chooseForm.setCurrentIndex(j)
				tutorMvs=[]
				num=self.getOffset(i,j)
				mfh.seek(num+0x3012C)
				tempnum=mds.readUInt32()
				tempnum2=mds.readUInt16()
				for l in range (0,32):
					if (tempnum>>l)&1==1:
						tutorMvs.append(tutorMoves[l])
				for l in range (0,6):
					if (tempnum2>>l)&1==1:
						tutorMvs.append(tutorMoves[32+l])
				for k in range(0,len(tutorMvs)):
					ts<<"("<<i<<","<<j<<","<<tutorMvs[k]<<"),\n"
		mfh.close()
		sf.close()"""
		"""sf=QFile("evodex.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `data`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `evo` (\n"
		ts<<"  `dataid` SMALLINT,\n"
		ts<<"  `evotype` SMALLINT,\n"
		ts<<"  `evotext` TEXT,\n"
		ts<<"  `evoparam` SMALLINT,\n"
		ts<<"  `evopkm` SMALLINT,\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		
		#Begin Inserting Data
		ts<<"INSERT INTO `evo` (`evotype`,`evotext`,`evoparam`,`evopkm`) VALUES\n"
		for i in range (1,494):\
			self.choosePokemon.setCurrentIndex(i)
			for j in range(0,len(self.dataids)):
				self.chooseForm.setCurrentIndex(j)
				for k in range(0,7):
					if self.evotypes[k].currentIndex()!=0:
						ts<<"("<<self.dataids[j]<<","
						ts<<self.evotypes[k].currentIndex()<<",'"
						ts<<self.evotypes[k].currentText()<<"',"
						ts<<self.evoparams[k]<<","
						ts<<self.evopkms[k].currentIndex()<<"),\n"
				if i%50 == 0:
					print i
			
		sf.close()
		"""
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
		#	eval("self.rockSmash"+str(i)+".setStyleSheet('background-color:#ff0000;')")
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
		#self.extractToSql()

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
	def extractToSql(self):
		lT="loc"
		iL=""
		if mw.ID==0x4C50:
			iL+="pl"
		elif mw.ID==0x50:
			iL+="p"
		elif mw.ID==0x44:
			iL+="d"
		iL+=chr(mw.lang).lower()
		lT+=iL
		sf=QFile(lT+".sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `"+lT+"`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `"+lT+"` (\n"
		ts<<"  `mapid` SMALLINT,\n"
		ts<<"  `mapname` TEXT,\n"
		ts<<"  PRIMARY KEY  (`mapid`)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		ts<<"INSERT INTO `"+lT+"` (`mapid`,`mapname`) VALUES\n"
		ef=QFile("enc"+iL+".sql")
		ef.open(QIODevice.WriteOnly)
		ets=QTextStream(ef)
		ets.setCodec("UTF-8")
		ets<<"DROP TABLE IF EXISTS `enc"+iL+"`;\n"
		ets<<"CREATE TABLE IF NOT EXISTS `enc"+iL+"` (\n"
		ets<<"  `mapid` SMALLINT,\n"
		ets<<"  `natid` SMALLINT,\n"
		ets<<"  `raritytype` TINYINT,\n"
		ets<<"  `type` TINYINT, \n"
		ets<<"  `lvl1` TINYINT,\n"
		ets<<"  `lvl2` TINYINT\n"
		ets<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		ets<<"INSERT INTO `enc"+iL+"` (`mapid`,`natid`,`raritytype`,`type`,`lvl1`,`lvl2`) VALUES\n"
		
		for i in range(0, self.size):
			self.chooseMap.setCurrentIndex(i)
			ts<<"("+str(i)+",'"+self.chooseMapName.currentText()+"'),\n"
			if self.spinBox_8.value()!=0xFFFF:
				if self.walkRate.value()!=0:
					ets<<"("+str(i)+","+str(self.chooseWalkPoke1.currentIndex())+",1,1,"+str(self.walkPokeLvl1.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke2.currentIndex())+",2,1,"+str(self.walkPokeLvl2.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke3.currentIndex())+",3,1,"+str(self.walkPokeLvl3.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke4.currentIndex())+",4,1,"+str(self.walkPokeLvl4.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke5.currentIndex())+",5,1,"+str(self.walkPokeLvl5.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke6.currentIndex())+",6,1,"+str(self.walkPokeLvl6.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke7.currentIndex())+",7,1,"+str(self.walkPokeLvl7.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke8.currentIndex())+",8,1,"+str(self.walkPokeLvl8.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke9.currentIndex())+",9,1,"+str(self.walkPokeLvl9.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke10.currentIndex())+",10,1,"+str(self.walkPokeLvl10.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke11.currentIndex())+",11,1,"+str(self.walkPokeLvl11.value())+",0),\n"
					ets<<"("+str(i)+","+str(self.chooseWalkPoke12.currentIndex())+",12,1,"+str(self.walkPokeLvl12.value())+",0),\n"
					if self.morning1.currentIndex() !=self.chooseWalkPoke1.currentIndex():
						ets<<"("+str(i)+","+str(self.morning1.currentIndex())+",1,2,"+str(self.walkPokeLvl1.value())+",0),\n"
					if self.morning2.currentIndex() !=self.chooseWalkPoke2.currentIndex():
						ets<<"("+str(i)+","+str(self.morning2.currentIndex())+",2,2,"+str(self.walkPokeLvl2.value())+",0),\n"
					if self.day1.currentIndex() !=self.chooseWalkPoke3.currentIndex():
						ets<<"("+str(i)+","+str(self.day1.currentIndex())+",3,3,"+str(self.walkPokeLvl3.value())+",0),\n"
					if self.day2.currentIndex() !=self.chooseWalkPoke4.currentIndex():
						ets<<"("+str(i)+","+str(self.day2.currentIndex())+",4,3,"+str(self.walkPokeLvl4.value())+",0),\n"
					if self.night1.currentIndex() !=self.chooseWalkPoke3.currentIndex():
						ets<<"("+str(i)+","+str(self.night1.currentIndex())+",3,4,"+str(self.walkPokeLvl3.value())+",0),\n"
					if self.night2.currentIndex() !=self.chooseWalkPoke4.currentIndex():
						ets<<"("+str(i)+","+str(self.night2.currentIndex())+",4,4,"+str(self.walkPokeLvl4.value())+",0),\n"
					if self.radar1.currentIndex() !=self.chooseWalkPoke7.currentIndex():
						ets<<"("+str(i)+","+str(self.radar1.currentIndex())+",7,5,"+str(self.walkPokeLvl7.value())+",0),\n"
					if self.radar2.currentIndex() !=self.chooseWalkPoke8.currentIndex():
						ets<<"("+str(i)+","+str(self.radar2.currentIndex())+",8,5,"+str(self.walkPokeLvl8.value())+",0),\n"
					if self.radar3.currentIndex() !=self.chooseWalkPoke11.currentIndex():
						ets<<"("+str(i)+","+str(self.radar3.currentIndex())+",11,5,"+str(self.walkPokeLvl11.value())+",0),\n"
					if self.radar4.currentIndex() !=self.chooseWalkPoke12.currentIndex():
						ets<<"("+str(i)+","+str(self.radar4.currentIndex())+",12,5,"+str(self.walkPokeLvl12.value())+",0),\n"
					if self.ruby1.currentIndex() !=self.chooseWalkPoke9.currentIndex():
						ets<<"("+str(i)+","+str(self.ruby1.currentIndex())+",9,6,"+str(self.walkPokeLvl9.value())+",0),\n"
					if self.ruby2.currentIndex() !=self.chooseWalkPoke10.currentIndex():
						ets<<"("+str(i)+","+str(self.ruby2.currentIndex())+",10,6,"+str(self.walkPokeLvl10.value())+",0),\n"
					if self.sapphire1.currentIndex() !=self.chooseWalkPoke9.currentIndex():
						ets<<"("+str(i)+","+str(self.sapphire1.currentIndex())+",9,7,"+str(self.walkPokeLvl9.value())+",0),\n"
					if self.sapphire2.currentIndex() !=self.chooseWalkPoke10.currentIndex():
						ets<<"("+str(i)+","+str(self.sapphire2.currentIndex())+",10,7,"+str(self.walkPokeLvl10.value())+",0),\n"
					if self.emerald1.currentIndex() !=self.chooseWalkPoke9.currentIndex():
						ets<<"("+str(i)+","+str(self.emerald1.currentIndex())+",9,8,"+str(self.walkPokeLvl9.value())+",0),\n"
					if self.emerald2.currentIndex() !=self.chooseWalkPoke10.currentIndex():
						ets<<"("+str(i)+","+str(self.emerald2.currentIndex())+",10,8,"+str(self.walkPokeLvl10.value())+",0),\n"
					if self.red1.currentIndex() !=self.chooseWalkPoke9.currentIndex():
						ets<<"("+str(i)+","+str(self.red1.currentIndex())+",9,9,"+str(self.walkPokeLvl9.value())+",0),\n"
					if self.red2.currentIndex() !=self.chooseWalkPoke10.currentIndex():
						ets<<"("+str(i)+","+str(self.red2.currentIndex())+",10,9,"+str(self.walkPokeLvl10.value())+",0),\n"
					if self.green1.currentIndex() !=self.chooseWalkPoke9.currentIndex():
						ets<<"("+str(i)+","+str(self.green1.currentIndex())+",9,10,"+str(self.walkPokeLvl9.value())+",0),\n"
					if self.green2.currentIndex() !=self.chooseWalkPoke10.currentIndex():
						ets<<"("+str(i)+","+str(self.green2.currentIndex())+",10,10,"+str(self.walkPokeLvl10.value())+",0),\n"
				if self.surfRate.value() !=0:
					ets<<"("+str(i)+","+str(self.surfPoke1.currentIndex())+",1,13,"+str(self.surfMin1.value())+","+str(self.surfMax1.value())+"),\n"
					ets<<"("+str(i)+","+str(self.surfPoke2.currentIndex())+",2,13,"+str(self.surfMin2.value())+","+str(self.surfMax2.value())+"),\n"
					ets<<"("+str(i)+","+str(self.surfPoke3.currentIndex())+",3,13,"+str(self.surfMin3.value())+","+str(self.surfMax3.value())+"),\n"
					ets<<"("+str(i)+","+str(self.surfPoke4.currentIndex())+",4,13,"+str(self.surfMin4.value())+","+str(self.surfMax4.value())+"),\n"
					ets<<"("+str(i)+","+str(self.surfPoke5.currentIndex())+",5,13,"+str(self.surfMin5.value())+","+str(self.surfMax5.value())+"),\n"
				if self.oldRodRate.value() !=0:
					ets<<"("+str(i)+","+str(self.oldRodPoke1.currentIndex())+",1,14,"+str(self.oldRodMin1.value())+","+str(self.oldRodMax1.value())+"),\n"
					ets<<"("+str(i)+","+str(self.oldRodPoke2.currentIndex())+",2,14,"+str(self.oldRodMin2.value())+","+str(self.oldRodMax2.value())+"),\n"
					ets<<"("+str(i)+","+str(self.oldRodPoke3.currentIndex())+",3,14,"+str(self.oldRodMin3.value())+","+str(self.oldRodMax3.value())+"),\n"
					ets<<"("+str(i)+","+str(self.oldRodPoke4.currentIndex())+",4,14,"+str(self.oldRodMin4.value())+","+str(self.oldRodMax4.value())+"),\n"
					ets<<"("+str(i)+","+str(self.oldRodPoke5.currentIndex())+",5,14,"+str(self.oldRodMin5.value())+","+str(self.oldRodMax5.value())+"),\n"
				if self.goodRodRate.value() !=0:
					ets<<"("+str(i)+","+str(self.goodRodPoke1.currentIndex())+",1,15,"+str(self.goodRodMin1.value())+","+str(self.goodRodMax1.value())+"),\n"
					ets<<"("+str(i)+","+str(self.goodRodPoke2.currentIndex())+",2,15,"+str(self.goodRodMin2.value())+","+str(self.goodRodMax2.value())+"),\n"
					ets<<"("+str(i)+","+str(self.goodRodPoke3.currentIndex())+",3,15,"+str(self.goodRodMin3.value())+","+str(self.goodRodMax3.value())+"),\n"
					ets<<"("+str(i)+","+str(self.goodRodPoke4.currentIndex())+",4,15,"+str(self.goodRodMin4.value())+","+str(self.goodRodMax4.value())+"),\n"
					ets<<"("+str(i)+","+str(self.goodRodPoke5.currentIndex())+",5,15,"+str(self.goodRodMin5.value())+","+str(self.goodRodMax5.value())+"),\n"
				if self.superRodRate.value() !=0:
					ets<<"("+str(i)+","+str(self.superRodPoke1.currentIndex())+",1,16,"+str(self.superRodMin1.value())+","+str(self.superRodMax1.value())+"),\n"
					ets<<"("+str(i)+","+str(self.superRodPoke2.currentIndex())+",2,16,"+str(self.superRodMin2.value())+","+str(self.superRodMax2.value())+"),\n"
					ets<<"("+str(i)+","+str(self.superRodPoke3.currentIndex())+",3,16,"+str(self.superRodMin3.value())+","+str(self.superRodMax3.value())+"),\n"
					ets<<"("+str(i)+","+str(self.superRodPoke4.currentIndex())+",4,16,"+str(self.superRodMin4.value())+","+str(self.superRodMax4.value())+"),\n"
					ets<<"("+str(i)+","+str(self.superRodPoke5.currentIndex())+",5,16,"+str(self.superRodMin5.value())+","+str(self.superRodMax5.value())+"),\n"
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
		#self.extractToSql()
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
	def extractToSql(self):
		sf=QFile("tmdex.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `tms`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `tms` (\n"
		ts<<"  `tmnum` TINYINT,"
		ts<<"  `movenum` SMALLINT,"
		ts<<"  PRIMARY KEY  (`tmnum`)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		
		#Begin Inserting Data
		ts<<"INSERT INTO `tms` (`tmnum`,`movenum`) VALUES\n"
		for i in range (0,100):
			self.chooseTm.setCurrentIndex(i)
			ts<<"("<<i<<","<<self.chooseMove.currentIndex()<<")"
			if i==99:
				ts<<";"
				print "done"
			else:
				ts<<",\n"
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
		#self.extractToSql()
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
	def extractToSql(self):
		sf=QFile("movedexdpkr.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `moveskr`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `moveskr` (\n"
		ts<<"  `moveid` SMALLINT,\n"
		ts<<"  `name` VARCHAR(20),\n"
		ts<<"  `power` SMALLINT,\n"
		ts<<"  `pp` TINYINT,\n"
		ts<<"  `type` TINYINT,\n"
		ts<<"  `acc` SMALLINT,\n"
		ts<<"  `target` TINYINT,\n"
		ts<<"  `effectchance` SMALLINT,\n"
		ts<<"  `category` TINYINT,\n"
		ts<<"  `ctype` TINYINT,\n"
		ts<<"  `cpoints` TINYINT,\n"
		ts<<"  `desc` TEXT,\n"
		ts<<"  `cdesc` TEXT,\n"
		ts<<"  `effect` SMALLINT,\n"
		ts<<"  PRIMARY KEY  (`moveid`)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		
		#Begin Inserting Data
		ts<<"INSERT INTO `moveskr` (`moveid`,`name`,`power`,`pp`,`type`,`acc`,`target`,`effectchance`,`category`,`ctype`,`cpoints`,`desc`,`cdesc`,`effect`) VALUES\n"
		for i in range (1,468):
			self.chooseMove.setCurrentIndex(i)
			ts<<"("<<i<<",'"<<self.chooseMove.currentText()<<"',"
			ts<<self.basePower.value()<<","<<self.pp.value()<<","
			ts<<self.type.currentIndex()<<","<<self.accuracy.value()<<","
			ts<<"'"<<self.target.currentIndex()<<"',"<<self.effectChance.value()<<","
			ts<<self.category.currentIndex()<<","<<self.ctype.currentIndex()<<","
			ts<<self.cpower[self.cindex]<<",'"<<self.atkDesc.toPlainText().replace("\\n"," ").replace("\\x0001", " ")<<"','"
			ts<<self.catkDesc.toPlainText().replace("\\n"," ").replace("\\x0001", " ")<<"',"
			ts<<self.effect.currentIndex()<<")"
			if i==467:
				ts<<";"
				print "done"
			else:
				ts<<",\n"
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
		#self.extractToSql()
	def extractToSql(self):
		sf=QFile("itemdexkr.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `itemskr`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `itemskr` (\n"
		ts<<"  `itemid` SMALLINT,"
		ts<<"  `name` VARCHAR(30),"
		ts<<"  PRIMARY KEY  (`itemid`)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		
		#Begin Inserting Data
		ts<<"INSERT INTO `itemskr` (`itemid`,`name`) VALUES\n"
		for i in range (0,465):
			self.chooseItem.setCurrentIndex(i)
			ts<<"("<<i<<",'"<<self.chooseItem.currentText()<<"')"
			if i==464:
				ts<<";"
				print "done"
			else:
				ts<<",\n"
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
		#self.extractToSql()
	def extractToSql(self):
		if mw.ID==0x4C50:
			if mw.lang==0x4A:
				binary=poketext.PokeTextData(self.archive.gmif.files[605])
			else:
				binary=poketext.PokeTextData(self.archive.gmif.files[612])
		else:
			if mw.lang==0x4B:
				binary=poketext.PokeTextData(self.archive.gmif.files[547])
			else:
				binary=poketext.PokeTextData(self.archive.gmif.files[554])
		binary.decrypt()
		sf=QFile("abilitydexkr.sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `abilitieskr`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `abilitieskr` (\n"
		ts<<"  `id` SMALLINT,\n"
		ts<<"  `name` VARCHAR(30),\n"
		ts<<"  `desc` TEXT,\n"
		ts<<"  PRIMARY KEY  (`id`)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		
		#Begin Inserting Data
		ts<<"INSERT INTO `abilitieskr` (`id`,`name`,`desc`) VALUES\n"
		for i in range (0,124):
			self.chooseAbility.setCurrentIndex(i)
			ts<<"("<<i<<",'"<<self.chooseAbility.currentText()<<"','"<<binary.strlist[i].replace("\\n"," ").replace("\\x0001", " ")<<"')"
			if i==123:
				ts<<";"
				print "done"
			else:
				ts<<",\n"
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
		#self.extractToSql()
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
				exec("del(self.tab"+str(n)+")")
			return
		
		for n in range(current,num):
			exec("self.tab"+str(n)+" = QtGui.QWidget()")
			exec("self.tab"+str(n)+".setObjectName(\"tab"+str(n)+"\")")
			exec("self.gridLayoutWidget_"+str(n)+"_3 = QtGui.QWidget(self.tab"+str(n)+")")
			exec("self.gridLayoutWidget_"+str(n)+"_3.setGeometry(QtCore.QRect(50, 50, 536, 236))")
			exec("self.gridLayoutWidget_"+str(n)+"_3.setObjectName(\"gridLayoutWidget_"+str(n)+"_3\")")
			exec("self.gridLayout_"+str(n)+"_3 = QtGui.QGridLayout(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.gridLayout_"+str(n)+"_3.setObjectName(\"gridLayout_"+str(n)+"_3\")")
			exec("self.spec"+str(n)+" = QtGui.QComboBox(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.spec"+str(n)+".setObjectName(\"spec"+str(n)+"\")")
			exec("self.spec"+str(n)+".addItems(self.pN)")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.spec"+str(n)+", 0, 1, 1, 1)")
			exec("self.label_"+str(n)+"_15 = QtGui.QLabel(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.label_"+str(n)+"_15.setObjectName(\"label_"+str(n)+"_15\")")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.label_"+str(n)+"_15, 0, 0, 1, 1)")
			exec("self.label_"+str(n)+"_16 = QtGui.QLabel(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.label_"+str(n)+"_16.setObjectName(\"label_"+str(n)+"_16\")")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.label_"+str(n)+"_16, 1, 0, 1, 1)")
			exec("self.pokelvl"+str(n)+" = QtGui.QSpinBox(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.pokelvl"+str(n)+".setObjectName(\"pokelvl"+str(n)+"\")")
			exec("self.pokelvl"+str(n)+".setMaximum(255)")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.pokelvl"+str(n)+", 1, 1, 1, 1)")
			exec("self.label_"+str(n)+"_17 = QtGui.QLabel(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.label_"+str(n)+"_17.setObjectName(\"label_"+str(n)+"_17\")")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.label_"+str(n)+"_17, 2, 0, 1, 1)")
			exec("self.pokeItem"+str(n)+" = QtGui.QComboBox(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.pokeItem"+str(n)+".setObjectName(\"pokeItem"+str(n)+"\")")
			exec("self.pokeItem"+str(n)+".addItems(self.iN)")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.pokeItem"+str(n)+", 2, 1, 1, 1)")
			exec("self.pu0_"+str(n)+" = QtGui.QSpinBox(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.pu0_"+str(n)+".setMaximum(255)")
			exec("self.pu0_"+str(n)+".setObjectName(\"pu0_"+str(n)+"\")")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.pu0_"+str(n)+", 4, 1, 1, 1)")
			exec("self.form_"+str(n)+" = QtGui.QSpinBox(self.gridLayoutWidget_"+str(n)+"_3)")#
			exec("self.form_"+str(n)+".setMaximum(15)")
			exec("self.form_"+str(n)+".setObjectName(\"form_"+str(n)+"\")")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.form_"+str(n)+", 5, 1, 1, 1)")#
			exec("self.label_"+str(n)+"_form = QtGui.QLabel(self.gridLayoutWidget_"+str(n)+"_3)")#
			exec("self.label_"+str(n)+"_form.setObjectName(\"label_"+str(n)+"_form\")")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.label_"+str(n)+"_form, 5, 0, 1, 1)")#
			exec("self.label_"+str(n)+"_18 = QtGui.QLabel(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.label_"+str(n)+"_18.setObjectName(\"label_"+str(n)+"_18\")")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.label_"+str(n)+"_18, 3, 0, 1, 1)")
			exec("self.label_"+str(n)+"_28 = QtGui.QLabel(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.label_"+str(n)+"_28.setObjectName(\"label_"+str(n)+"_28\")")
			exec("self.gridLayout_"+str(n)+"_3.addWidget(self.label_"+str(n)+"_28, 4, 0, 1, 1)")
			exec("self.gridLayout_"+str(n)+"_5 = QtGui.QGridLayout()")
			exec("self.gridLayout_"+str(n)+"_5.setObjectName(\"gridLayout_"+str(n)+"_5\")")
			exec("self.attack"+str(n)+"_1 = QtGui.QComboBox(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.attack"+str(n)+"_1.setObjectName(\"attack"+str(n)+"_1\")")
			exec("self.attack"+str(n)+"_1.addItems(self.mN)")
			exec("self.gridLayout_"+str(n)+"_5.addWidget(self.attack"+str(n)+"_1, 0, 0, 1, 1)")
			exec("self.attack"+str(n)+"_2 = QtGui.QComboBox(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.attack"+str(n)+"_2.setObjectName(\"attack"+str(n)+"_2\")")
			exec("self.attack"+str(n)+"_2.addItems(self.mN)")
			exec("self.gridLayout_"+str(n)+"_5.addWidget(self.attack"+str(n)+"_2, 0, 1, 1, 1)")
			exec("self.attack"+str(n)+"_3 = QtGui.QComboBox(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.attack"+str(n)+"_3.setObjectName(\"attack"+str(n)+"_3\")")
			exec("self.attack"+str(n)+"_3.addItems(self.mN)")
			exec("self.gridLayout_"+str(n)+"_5.addWidget(self.attack"+str(n)+"_3, 1, 0, 1, 1)")
			exec("self.attack"+str(n)+"_4 = QtGui.QComboBox(self.gridLayoutWidget_"+str(n)+"_3)")
			exec("self.attack"+str(n)+"_4.setObjectName(\"attack"+str(n)+"_4\")")
			exec("self.attack"+str(n)+"_4.addItems(self.mN)")
			exec("self.gridLayout_"+str(n)+"_5.addWidget(self.attack"+str(n)+"_4, 1, 1, 1, 1)")
			exec("self.gridLayout_"+str(n)+"_3.addLayout(self.gridLayout_"+str(n)+"_5, 3, 1, 1, 1)")
			exec("self.label_"+str(n)+"_15.setText(\"Pokemon\")")
			exec("self.label_"+str(n)+"_16.setText(\"Level\")")
			exec("self.label_"+str(n)+"_17.setText(\"Item\")")
			exec("self.label_"+str(n)+"_18.setText(\"Extra Attacks\")")
			exec("self.label_"+str(n)+"_28.setText(\"u0\")")
			exec("self.label_"+str(n)+"_form.setText(\"Form #\")")
			exec("self.maintab.addTab(self.tab"+str(n)+", \"Pokemon "+str(n+1)+"\")")
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
	def extractToSql(self):
		iL=""
		if mw.ID==0x5353:
			iL+="hgss"
		elif mw.ID==0x4748:
			iL+="hgss"
		elif mw.ID==0x4C50:
			iL+="pl"
		elif mw.ID==0x50:
			iL+="dp"
		elif mw.ID==0x44:
			iL+="dp"
		lL=chr(mw.lang).lower()
		sf=QFile(iL+"trainers"+lL+".sql")
		sf.open(QIODevice.WriteOnly)
		ts=QTextStream(sf)
		ts.setCodec("UTF-8")
		ts<<"DROP TABLE IF EXISTS `"+iL+"trainers"+lL+"`;\n"
		ts<<"CREATE TABLE IF NOT EXISTS `"+iL+"trainers"+lL+"` (\n"
		ts<<"  `id` SMALLINT,\n"
		ts<<"  `name` VARCHAR(32),\n"
		ts<<"  `class` VARCHAR(32),\n"
		ts<<"  `classid` SMALLINT,\n"
		ts<<"  `num_pokemon` SMALLINT,\n"
		ts<<"  `items` TEXT,\n"
		ts<<"  `flag` SMALLINT,\n"
		ts<<"  `double` TINYINT,\n"
		ts<<"  PRIMARY KEY  (`id`)\n"
		ts<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		
		#Begin Inserting Data
		ts<<"INSERT INTO `"+iL+"trainers"+lL+"` (`id`,`name`,`class`,`classid`,`num_pokemon`,`items`,`flag`,`double`) VALUES\n"

		sg=QFile(iL+"trpoke"+lL+".sql")
		sg.open(QIODevice.WriteOnly)
		tt=QTextStream(sg)
		tt.setCodec("UTF-8")
		tt<<"DROP TABLE IF EXISTS `"+iL+"trpoke"+lL+"`;\n"
		tt<<"CREATE TABLE IF NOT EXISTS `"+iL+"trpoke"+lL+"` (\n"
		tt<<"  `id` SMALLINT,\n"
		tt<<"  `trainerid` SMALLINT,\n"
		tt<<"  `natid` INT,\n"
		tt<<"  `form` SMALLINT,\n"
		tt<<"  `level` INT,\n"
		tt<<"  `item` TEXT,\n"
		tt<<"  `moves` TEXT,\n"
		tt<<"  PRIMARY KEY  (`id`)\n"
		tt<<") ENGINE=MyISAM  DEFAULT CHARSET=utf8;\n\n"
		
		#Begin Inserting Data
		tt<<"INSERT INTO `"+iL+"trpoke"+lL+"` (`id`,`trainerid`,`natid`,`form`,`level`,`item`,`moves`) VALUES\n"
		k = 0
		for i in range (0,len(self.trNames.strlist)):
			self.chooseTrainer.setCurrentIndex(i)
			ts<<"("<<i<<",'"<<self.trNames.strlist[i]<<"','"<<self.class_2.currentText()<<"','"<<str(self.class_2.currentIndex())<<"','"<<self.pokenum.value()<<"','"<<(str(self.item1.currentIndex())+","+str(self.item2.currentIndex())+","+str(self.item3.currentIndex())+","+str(self.item4.currentIndex()))<<"','"<<(self.itemBool.isChecked()*2 + self.attackBool.isChecked())<<"','"<<self.doubleBool.isChecked()<<"')"
			for h in range(0,self.pokenum.value()):
				tt<<"("<<k<<","<<i<<",'"
				k+=1
				tt<<eval("self.spec"+str(h)+".currentIndex()")<<"','"
				tt<<eval("self.form_"+str(h)+".value()")<<"','"
				tt<<eval("self.pokelvl"+str(h)+".value()")<<"','"
				tt<<eval("self.pokeItem"+str(h)+".currentIndex()")<<"','"
				tt<<""<<eval("self.attack"+str(h)+"_1.currentIndex()")<<""
				tt<<","<<eval("self.attack"+str(h)+"_2.currentIndex()")<<""
				tt<<","<<eval("self.attack"+str(h)+"_3.currentIndex()")<<""
				tt<<","<<eval("self.attack"+str(h)+"_4.currentIndex()")<<""
				tt<<"')"
				tt<<",\n"
			if i==len(self.trNames.strlist)-1:
				ts<<";"
				tt<<";"
				print "--done--"
			else:
				ts<<",\n"
class LoadDlg(QDialog, ui_open.Ui_Dialog):
	def __init__(self,parent=None):
		super(LoadDlg,self).__init__(parent)
		self.setupUi(self)
		self.loadable = []
		self.newload = []
		self.loads = {}
		for item in os.listdir("."):
			if item[:4] == "tmp_":
				self.loadable.append(item)
				self.loads[item] = item.lstrip("tmp_")+".nds"
		for item in os.listdir("."):
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
			mw.nameEdit.setText(str(self.romchoose.currentItem().text()).lstrip("(Saved) "))
		self.close()
	def checkROM(self):
		self.choicename.setText("ROM Name: "+str(self.romchoose.currentItem().text()).lstrip("(Saved) "))

app = QApplication(sys.argv)
mw = MainWindow()
mw.show()
app.exec_()
#else:
#	QMessageBox.warning(None,"Phone Log", QString("Database Error: %1").arg(db.lastError().text()))

