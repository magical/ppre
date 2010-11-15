# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/SCV/Desktop/PPRE/ppreabilityedit.ui'
#
# Created: Fri Apr 17 18:34:38 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AbilityEditDlg(object):
    def setupUi(self, AbilityEditDlg):
        AbilityEditDlg.setObjectName("AbilityEditDlg")
        AbilityEditDlg.resize(400, 300)
        self.chooseAbility = QtGui.QComboBox(AbilityEditDlg)
        self.chooseAbility.setGeometry(QtCore.QRect(30, 40, 84, 27))
        self.chooseAbility.setObjectName("chooseAbility")
        self.abilityDesc = QtGui.QPlainTextEdit(AbilityEditDlg)
        self.abilityDesc.setGeometry(QtCore.QRect(30, 110, 131, 64))
        self.abilityDesc.setObjectName("abilityDesc")

        self.retranslateUi(AbilityEditDlg)
        QtCore.QMetaObject.connectSlotsByName(AbilityEditDlg)

    def retranslateUi(self, AbilityEditDlg):
        AbilityEditDlg.setWindowTitle(QtGui.QApplication.translate("AbilityEditDlg", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

