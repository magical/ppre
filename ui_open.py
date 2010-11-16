# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'opendialog.ui'
#
# Created: Thu May  6 19:02:26 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-230, 260, 621, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.romchoose = QtGui.QListWidget(Dialog)
        self.romchoose.setGeometry(QtCore.QRect(10, 30, 371, 221))
        self.romchoose.setObjectName("romchoose")
        self.choicename = QtGui.QLabel(Dialog)
        self.choicename.setGeometry(QtCore.QRect(10, 266, 181, 21))
        self.choicename.setObjectName("choicename")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(100, 10, 171, 17))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QObject.connect(self.romchoose, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), Dialog.checkROM)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Choose ROM", None, QtGui.QApplication.UnicodeUTF8))
        self.choicename.setText(QtGui.QApplication.translate("Dialog", "ROM Name: ", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Choose a ROM", None, QtGui.QApplication.UnicodeUTF8))

