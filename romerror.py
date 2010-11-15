#!/usr/bin/env python
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui


class BasicException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def noROM():
	QMessageBox.critical(None,"Critical","ROM has not been loaded. Please place your ROM in the same folder as PPRE, and choose it by clicking 'Choose ROM'.")
def noROM2Write():
	QMessageBox.critical(None,"Critical","ROM has not been written. Please choose a name for the ROM to be written.")
def noData(mw):
	QMessageBox.critical(None,"Critical","There is no data located within '"+mw.rom.getFolder()+"'.\nIf the ROM named '"+mw.rom.getFolder().lstrip("tmp_")+".nds' is in the same folder as PPRE, delete '"+mw.rom.getFolder()+"' and try to load it again.")
def noValue():
	QMessageBox.critical(None,"Critical","No value was chosen!")
def noPatch():
	QMessageBox.critical(None,"Critical","The Patch you have chosen does not exist. Please make sure your PPRE folder contains the patch and try again.")
def noROM2Patch():
	QMessageBox.critical(None,"Critical","A patch file could not be created. Please make sure that you have already pressed 'Write ROM'")
def unknownEscape(text):
	QMessageBox.critical(None,"Warning","Error Parsing Text: Unknown Escape: \\%s"%text)
def charNotFound(char):
	QMessageBox.critical(None,"Warning","Error Parsing Text: Char not found %s (\\x%02X)"%(char,ord(char)))






