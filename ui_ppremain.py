# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ppremain.ui'
#
# Created: Mon Jun 21 14:56:20 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(290, 489)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("PPRE.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.openROMButton = QtGui.QPushButton(self.centralwidget)
        self.openROMButton.setGeometry(QtCore.QRect(150, 50, 105, 28))
        self.openROMButton.setObjectName("openROMButton")
        self.nameLabel = QtGui.QLabel(self.centralwidget)
        self.nameLabel.setGeometry(QtCore.QRect(30, 20, 81, 19))
        self.nameLabel.setObjectName("nameLabel")
        self.nameEdit = QtGui.QLineEdit(self.centralwidget)
        self.nameEdit.setGeometry(QtCore.QRect(152, 10, 101, 29))
        self.nameEdit.setObjectName("nameEdit")
        self.pokemoneditButton = QtGui.QPushButton(self.centralwidget)
        self.pokemoneditButton.setGeometry(QtCore.QRect(30, 100, 105, 28))
        self.pokemoneditButton.setObjectName("pokemoneditButton")
        self.mapeditButton = QtGui.QPushButton(self.centralwidget)
        self.mapeditButton.setGeometry(QtCore.QRect(150, 100, 105, 28))
        self.mapeditButton.setObjectName("mapeditButton")
        self.moveeditButton = QtGui.QPushButton(self.centralwidget)
        self.moveeditButton.setGeometry(QtCore.QRect(30, 140, 105, 28))
        self.moveeditButton.setObjectName("moveeditButton")
        self.tmhmeditButton = QtGui.QPushButton(self.centralwidget)
        self.tmhmeditButton.setGeometry(QtCore.QRect(150, 140, 105, 28))
        self.tmhmeditButton.setObjectName("tmhmeditButton")
        self.itemEdit = QtGui.QPushButton(self.centralwidget)
        self.itemEdit.setGeometry(QtCore.QRect(30, 180, 105, 28))
        self.itemEdit.setObjectName("itemEdit")
        self.abilityButton = QtGui.QPushButton(self.centralwidget)
        self.abilityButton.setGeometry(QtCore.QRect(150, 180, 105, 28))
        self.abilityButton.setObjectName("abilityButton")
        self.scriptButton = QtGui.QPushButton(self.centralwidget)
        self.scriptButton.setGeometry(QtCore.QRect(30, 220, 105, 27))
        self.scriptButton.setObjectName("scriptButton")
        self.trainerButton = QtGui.QPushButton(self.centralwidget)
        self.trainerButton.setGeometry(QtCore.QRect(150, 220, 105, 27))
        self.trainerButton.setObjectName("trainerButton")
        self.outputNameEdit = QtGui.QLineEdit(self.centralwidget)
        self.outputNameEdit.setGeometry(QtCore.QRect(150, 270, 103, 29))
        self.outputNameEdit.setObjectName("outputNameEdit")
        self.writeROMButton = QtGui.QPushButton(self.centralwidget)
        self.writeROMButton.setGeometry(QtCore.QRect(150, 310, 105, 28))
        self.writeROMButton.setObjectName("writeROMButton")
        self.chooseROMButton = QtGui.QPushButton(self.centralwidget)
        self.chooseROMButton.setGeometry(QtCore.QRect(30, 50, 105, 28))
        self.chooseROMButton.setObjectName("chooseROMButton")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 280, 111, 17))
        self.label.setObjectName("label")
        self.createPatchButton = QtGui.QPushButton(self.centralwidget)
        self.createPatchButton.setGeometry(QtCore.QRect(30, 400, 105, 28))
        self.createPatchButton.setObjectName("createPatchButton")
        self.applyPathButton = QtGui.QPushButton(self.centralwidget)
        self.applyPathButton.setGeometry(QtCore.QRect(150, 400, 105, 28))
        self.applyPathButton.setObjectName("applyPathButton")
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 80, 291, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(10, 250, 291, 20))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtGui.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(10, 340, 291, 20))
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.patchNameEdit = QtGui.QLineEdit(self.centralwidget)
        self.patchNameEdit.setGeometry(QtCore.QRect(150, 360, 103, 29))
        self.patchNameEdit.setObjectName("patchNameEdit")
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 370, 111, 17))
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 290, 25))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setEnabled(False)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_ROM = QtGui.QAction(MainWindow)
        self.actionOpen_ROM.setObjectName("actionOpen_ROM")
        self.menuFile.addAction(self.actionOpen_ROM)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.openROMButton, QtCore.SIGNAL("clicked()"), MainWindow.openROM)
        QtCore.QObject.connect(self.nameEdit, QtCore.SIGNAL("returnPressed()"), MainWindow.openROM)
        QtCore.QObject.connect(self.pokemoneditButton, QtCore.SIGNAL("clicked()"), MainWindow.openPokeEdit)
        QtCore.QObject.connect(self.mapeditButton, QtCore.SIGNAL("pressed()"), MainWindow.openMapEdit)
        QtCore.QObject.connect(self.tmhmeditButton, QtCore.SIGNAL("clicked()"), MainWindow.openTmHmEdit)
        QtCore.QObject.connect(self.moveeditButton, QtCore.SIGNAL("clicked()"), MainWindow.openMoveEdit)
        QtCore.QObject.connect(self.abilityButton, QtCore.SIGNAL("clicked()"), MainWindow.openAbilityEdit)
        QtCore.QObject.connect(self.itemEdit, QtCore.SIGNAL("clicked()"), MainWindow.openItemEdit)
        QtCore.QObject.connect(self.scriptButton, QtCore.SIGNAL("clicked()"), MainWindow.openScriptEdit)
        QtCore.QObject.connect(self.outputNameEdit, QtCore.SIGNAL("returnPressed()"), MainWindow.writeROM)
        QtCore.QObject.connect(self.writeROMButton, QtCore.SIGNAL("clicked()"), MainWindow.writeROM)
        QtCore.QObject.connect(self.trainerButton, QtCore.SIGNAL("clicked()"), MainWindow.openTrEdit)
        QtCore.QObject.connect(self.chooseROMButton, QtCore.SIGNAL("clicked()"), MainWindow.chooseROM)
        QtCore.QObject.connect(self.createPatchButton, QtCore.SIGNAL("pressed()"), MainWindow.createPatch)
        QtCore.QObject.connect(self.applyPathButton, QtCore.SIGNAL("clicked()"), MainWindow.applyPatch)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "PPRE beta 0.14", None, QtGui.QApplication.UnicodeUTF8))
        self.openROMButton.setText(QtGui.QApplication.translate("MainWindow", "Set ROM", None, QtGui.QApplication.UnicodeUTF8))
        self.nameLabel.setText(QtGui.QApplication.translate("MainWindow", "ROM Name: ", None, QtGui.QApplication.UnicodeUTF8))
        self.pokemoneditButton.setText(QtGui.QApplication.translate("MainWindow", "Pokemon", None, QtGui.QApplication.UnicodeUTF8))
        self.mapeditButton.setText(QtGui.QApplication.translate("MainWindow", "Maps", None, QtGui.QApplication.UnicodeUTF8))
        self.moveeditButton.setText(QtGui.QApplication.translate("MainWindow", "Moves", None, QtGui.QApplication.UnicodeUTF8))
        self.tmhmeditButton.setText(QtGui.QApplication.translate("MainWindow", "TM/HM", None, QtGui.QApplication.UnicodeUTF8))
        self.itemEdit.setText(QtGui.QApplication.translate("MainWindow", "Items", None, QtGui.QApplication.UnicodeUTF8))
        self.abilityButton.setText(QtGui.QApplication.translate("MainWindow", "Abilities", None, QtGui.QApplication.UnicodeUTF8))
        self.scriptButton.setText(QtGui.QApplication.translate("MainWindow", "Scripts", None, QtGui.QApplication.UnicodeUTF8))
        self.trainerButton.setText(QtGui.QApplication.translate("MainWindow", "Trainers", None, QtGui.QApplication.UnicodeUTF8))
        self.writeROMButton.setText(QtGui.QApplication.translate("MainWindow", "Write ROM", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseROMButton.setText(QtGui.QApplication.translate("MainWindow", "Choose ROM", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "New ROM Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.createPatchButton.setText(QtGui.QApplication.translate("MainWindow", "Create Patch", None, QtGui.QApplication.UnicodeUTF8))
        self.applyPathButton.setText(QtGui.QApplication.translate("MainWindow", "Apply Patch", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Patch Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_ROM.setText(QtGui.QApplication.translate("MainWindow", "Open ROM", None, QtGui.QApplication.UnicodeUTF8))

