# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/SCV/Desktop/PPRE/pprescripts.ui'
#
# Created: Fri May 15 10:46:52 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_scriptDlg(object):
    def setupUi(self, scriptDlg):
        scriptDlg.setObjectName("scriptDlg")
        scriptDlg.resize(887, 575)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("PPRE.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        scriptDlg.setWindowIcon(icon)
        self.chooseScript = QtGui.QComboBox(scriptDlg)
        self.chooseScript.setGeometry(QtCore.QRect(110, 10, 151, 26))
        self.chooseScript.setObjectName("chooseScript")
        self.scriptLabel = QtGui.QLabel(scriptDlg)
        self.scriptLabel.setGeometry(QtCore.QRect(10, 20, 101, 18))
        self.scriptLabel.setObjectName("scriptLabel")
        self.mapTab = QtGui.QTabWidget(scriptDlg)
        self.mapTab.setGeometry(QtCore.QRect(10, 80, 871, 491))
        self.mapTab.setObjectName("mapTab")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.orderEdit = QtGui.QPlainTextEdit(self.tab_2)
        self.orderEdit.setGeometry(QtCore.QRect(20, 20, 811, 381))
        self.orderEdit.setObjectName("orderEdit")
        self.mapTab.addTab(self.tab_2, "")
        self.scriptTab = QtGui.QWidget()
        self.scriptTab.setObjectName("scriptTab")
        self.scriptEdit = QtGui.QPlainTextEdit(self.scriptTab)
        self.scriptEdit.setGeometry(QtCore.QRect(20, 40, 811, 381))
        self.scriptEdit.setObjectName("scriptEdit")
        self.mapTab.addTab(self.scriptTab, "")

        self.retranslateUi(scriptDlg)
        self.mapTab.setCurrentIndex(1)
        QtCore.QObject.connect(self.chooseScript, QtCore.SIGNAL("currentIndexChanged(int)"), scriptDlg.updateScript)
        QtCore.QMetaObject.connectSlotsByName(scriptDlg)

    def retranslateUi(self, scriptDlg):
        scriptDlg.setWindowTitle(QtGui.QApplication.translate("scriptDlg", "Script Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.scriptLabel.setText(QtGui.QApplication.translate("scriptDlg", "Script Number", None, QtGui.QApplication.UnicodeUTF8))
        self.mapTab.setTabText(self.mapTab.indexOf(self.tab_2), QtGui.QApplication.translate("scriptDlg", "Script Order", None, QtGui.QApplication.UnicodeUTF8))
        self.mapTab.setTabText(self.mapTab.indexOf(self.scriptTab), QtGui.QApplication.translate("scriptDlg", "Scripts", None, QtGui.QApplication.UnicodeUTF8))

