# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/SCV/Desktop/PPRE/ppreitemedit.ui'
#
# Created: Fri Apr 17 18:34:39 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ItemEditDlg(object):
    def setupUi(self, ItemEditDlg):
        ItemEditDlg.setObjectName("ItemEditDlg")
        ItemEditDlg.resize(400, 300)
        self.itemDesc = QtGui.QPlainTextEdit(ItemEditDlg)
        self.itemDesc.setGeometry(QtCore.QRect(30, 110, 104, 64))
        self.itemDesc.setObjectName("itemDesc")
        self.chooseItem = QtGui.QComboBox(ItemEditDlg)
        self.chooseItem.setGeometry(QtCore.QRect(30, 60, 84, 27))
        self.chooseItem.setObjectName("chooseItem")

        self.retranslateUi(ItemEditDlg)
        QtCore.QMetaObject.connectSlotsByName(ItemEditDlg)

    def retranslateUi(self, ItemEditDlg):
        ItemEditDlg.setWindowTitle(QtGui.QApplication.translate("ItemEditDlg", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

