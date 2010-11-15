# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/SCV/Desktop/PPRE/ppretmhmedit.ui'
#
# Created: Wed Apr 15 10:17:42 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TmHmEditDlg(object):
    def setupUi(self, TmHmEditDlg):
        TmHmEditDlg.setObjectName("TmHmEditDlg")
        TmHmEditDlg.resize(320, 124)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("PPRE.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TmHmEditDlg.setWindowIcon(icon)
        self.chooseTm = QtGui.QComboBox(TmHmEditDlg)
        self.chooseTm.setGeometry(QtCore.QRect(20, 30, 84, 27))
        self.chooseTm.setObjectName("chooseTm")
        self.chooseMove = QtGui.QComboBox(TmHmEditDlg)
        self.chooseMove.setGeometry(QtCore.QRect(120, 30, 151, 27))
        self.chooseMove.setObjectName("chooseMove")

        self.retranslateUi(TmHmEditDlg)
        QtCore.QObject.connect(self.chooseTm, QtCore.SIGNAL("currentIndexChanged(int)"), TmHmEditDlg.changedTm)
        QtCore.QMetaObject.connectSlotsByName(TmHmEditDlg)

    def retranslateUi(self, TmHmEditDlg):
        TmHmEditDlg.setWindowTitle(QtGui.QApplication.translate("TmHmEditDlg", "TM HM Edit", None, QtGui.QApplication.UnicodeUTF8))

