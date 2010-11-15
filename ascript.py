import narc
import sys
import string
import codecs
import xml.dom.minidom
import bytereader
import struct
import re
#import varhandle
from PyQt4 import QtCore, QtGui

movs = [
    "SeeUp", 
    "SeeDown", 
    "SeeLeft", 
    "SeeRight", 
    "WalkUpVerySlow", 
    "WalkDownVerySlow", 
    "WalkLeftVerySlow", 
    "WalkRightVerySlow", 
    "WalkUpSlow", 
    "WalkDownSlow", 
    "WalkLeftSlow", 
    "WalkRightSlow", 
    "WalkUpNormal", 
    "WalkDownNormal", 
    "WalkLeftNormal", 
    "WalkRightNormal", 
    "WalkUpFast", 
    "WalkDownFast", 
    "WalkLeftFast", 
    "WalkRightFast", 
    "RunUp", 
    "RunDown", 
    "RunLeft", 
    "RunRight", 
    "MoveUpVerySlow", 
    "MoveDownVerySlow", 
    "MoveLeftVerySlow", 
    "MoveRightVerySlow", 
    "MoveUpSlow", 
    "MoveDownSlow", 
    "MoveLeftSlow", 
    "MoveRightSlow",
    "MoveUpNormal", 
    "MoveDownNormal", 
    "MoveLeftNormal", 
    "MoveRightNormal", 
    "MoveUpFast", 
    "MoveDownFast", 
    "MoveLeftFast", 
    "MoveRightFast", 
    "0028", 
    "0029", 
    "002A", 
    "002B", 
    "JumpFacingUpSlow", 
    "JumpFacingDownSlow", 
    "JumpFacingLeftSlow", 
    "JumpFacingRightSlow", 
    "JumpFacingUp", 
    "JumpFacingDown", 
    "JumpFacingLeft", 
    "JumpFacingRight", 
    "JumpUpOne", 
    "JumpDownOne", 
    "JumpLeftOne", 
    "JumpRightOne", 
    "JumpUpTwo", 
    "JumpDownTwo", 
    "JumpLeftTwo", 
    "JumpRightTwo", 
    "003C", 
    "003D", 
    "003E", 
    "003F", 
    "0040", 
    "0041", 
    "0042", 
    "0043", 
    "0044", 
    "0045", 
    "0046", 
    "0047", 
    "0048", 
    "0049", 
    "004A", 
    "Exclaim", 
    "PauseWalkUpSlow", 
    "PauseWalkDownSlow", 
    "PauseWalkLeftSlow", 
    "PauseWalkRightSlow", 
    "PauseWalkUp", 
    "PauseWalkDown", 
    "PauseWalkLeft", 
    "PauseWalkRight", 
    "PauseHoverUp", 
    "PauseHoverDown", 
    "PauseHoverLeft", 
    "PauseHoverRight", 
    "PauseReverseUp", 
    "PauseReverseDown", 
    "PauseReverseLeft", 
    "PauseReverseRight", 
    "PauseJumpLeftOne", 
    "PauseJumpRightOne", 
    "PauseJumpLeftTwo", 
    "PauseJumpRightTwo", 
    "0060", 
    "0061", 
    "0062", 
    "0063", 
    "0064", 
    "0065", 
    "0066", 
    "0067", 
    "0068", 
    "0069", 
    "006A", 
    "006B", 
    "006C", 
    "006D", 
    "006E", 
    "006F", 
    "0070", 
    "0071", 
    "0072", 
    "0073", 
    "0074", 
    "0075", 
    "0076", 
    "0077", 
    "0078", 
    "0079", 
    "007A", 
    "007B", 
    "007C", 
    "007D", 
    "007E", 
    "007F", 
    "0080", 
    "0081", 
    "0082", 
    "0083", 
    "0084", 
    "0085", 
    "0086", 
    "0087", 
    "0088", 
    "0089", 
    "008A", 
    "008B", 
    "008C", 
    "008D", 
    "008E", 
    "008F", 
    "0090", 
    "0091", 
    "0092", 
    "0093", 
    "0094", 
    "0095", 
    "0096", 
    "0097", 
    "0098", 
    "0099", 
    "009A", 
    "009B", 
    "009C", 
    "009D", 
    "009E", 
    "009F"]

def returnText(parentnode):
    for k in parentnode.childNodes:
        if k.nodeType == k.TEXT_NODE:
            return k.nodeValue.strip()

class commands:
    def __init__(self):
        self.dom = xml.dom.minidom.parse("cmds.xml")
        self.listName = {}
        self.listNum = {}
        self.attributes = ["name"]
        
    def returnText(self, parentnode):
        for k in parentnode.childNodes:
            if k.nodeType == k.TEXT_NODE:
                return k.nodeValue.strip()
     
    def getCommands(self, parentnode):
        for num, elem in enumerate(parentnode.getElementsByTagName("command")):
            name = self.returnText(elem.getElementsByTagName("name")[0])
            idnum = int(elem.getAttribute("id"))
            self.listName[name] = elem
            self.listNum[idnum] = elem
    def parse(self,game):
        for elem in self.dom.getElementsByTagName("scriptcmds"):
            if elem.getAttribute("game") == game:
                self.getCommands(elem)
                break
        self.listMov = movs
    def getListings(self):
        return self.listName,self.listNum,self.listMov

class script:
    def __init__(self,smap):
        self.dialog = smap
        self.game = "dp"
        if self.dialog.ID in (0x5353, 0x4748):
            self.game = "hgss"
        cmd = commands()
        cmd.parse(self.game)
        self.cmdsByName,self.cmdsByNum,self.movsByNum = cmd.getListings()
        #self.vars = varhandle.getVar(self.dialog.tmpFolder)
    def readArg(self,size):
        if size == 8:
            return self.reader.ReadByte()
        if size == 16:
            return self.reader.ReadUInt16()
        if size == 32:
            return self.reader.ReadInt32()
        print "Failed size: ",size
    def writeArg(self,writer,size,value):
        if size == 8:
            return writer.WriteByte(value)
        if size == 16:
            return writer.WriteUInt16(value)
        if size == 32:
            return writer.WriteInt32(value)
        print "Failed size: ",size
    def readScript(self):
        scriptfile = self.dialog.scriptNarc.gmif.files[self.dialog.spinBox_3.value()]
        self.scrlen = len(scriptfile)
        bytes = struct.unpack("B"*self.scrlen,scriptfile)
        self.reader = bytereader.byteReader(bytes)
        self.ords = []
        self.numscr = 0
        self.scrOffs = []
        self.funcOffs = []
        self.movOffs = []
        self.scripts = []
        self.functions = []
        self.movements = []
        self.maxcmd = len(self.cmdsByNum)
        self.maxmovcmd = len(self.movsByNum)
        self.keyset = {"func":[],"mov":[],"flag":[]}
        tmpOff = []
        tmpOrd = []
        while self.reader.Position() < self.scrlen:
            tmp = self.reader.ReadUInt32()
            if (tmp & 0xFFFF) == 0xFD13:
                break
            else:
                tmp2 = self.reader.Position()+tmp
                tmpOrd.append(tmp2)
                if tmp2 not in tmpOff:
                    tmpOff.append(tmp2)
        tmpOff.sort()
        for t in tmpOrd:
            self.ords.append(tmpOff.index(t))#ords are now stacked with  script numbers indexes (+1 to get script)
        self.scrOffs = tmpOff[:]
        self.dialog.scriptOrdList.clear()
        for i in self.ords:
            self.dialog.scriptOrdList.addItem("Script %i"%(i+1))
        self.numscr = len(self.scrOffs)

        #### SCRIPT PARSE ####
        self.functype = "scr"
        for self.s in range(0,self.numscr):
            self.reader.Seek(self.scrOffs[self.s])
            if self.s < (self.numscr-1):
                self.maxpos = self.scrOffs[self.s+1]
            else:
                self.maxpos = self.scrlen
            self.scripts.append(self.doReadCmds())
        self.s = 0
        self.maxpos = self.scrlen
        self.functype = "func"
        while True:
            if self.s == len(self.funcOffs):
                break
            self.reader.Seek(self.funcOffs[self.s])
            self.functions.append(self.doReadCmds())
            self.s += 1
        self.maxpos = self.scrlen
        for seek in self.movOffs:
            self.reader.Seek(seek)
            self.movements.append(self.doReadMovs())

        #### Key Associations ####
        keyassoc = {"func":self.funcOffs,"mov":self.movOffs}
        funcassoc = {"scr":self.scripts,"func":self.functions}
        for keytype in self.keyset:
            for slot in self.keyset[keytype]:
                f = slot[0]
                s = slot[1]
                cline = slot[2]
                arg = slot[3]
                indice = funcassoc[f][s][cline][arg][1]
                funcassoc[f][s][cline][arg] = keytype+"_"+str(keyassoc[keytype].index(indice)+1)
        #print self.scripts
        #print self.functions
        #print self.movements
        
        #### UI Setup ####
        self.tabnames = {
"scr":[self.dialog.scriptTabWidget,self.scripts,self.dialog.navScript],
"func":[self.dialog.funcTabWidget,self.functions,self.dialog.navFunc],
"mov":[self.dialog.movTabWidget,self.movements,self.dialog.navMov]}
        for tab in self.tabnames:
            while self.tabnames[tab][0].count() > 0:
                self.tabnames[tab][0].removeTab(0)
            self.dialog.scriptTabs[tab] = []
            t = 0
            for s in self.tabnames[tab][1]:
                self.dialog.scriptTabs[tab].append([])
                self.dialog.scriptTabs[tab][t].append(QtGui.QWidget())
                self.dialog.scriptTabs[tab][t][0].setObjectName("%s_tab_%i"%(tab,t))
                self.dialog.scriptTabs[tab][t].append(QtGui.QTextBrowser(self.dialog.scriptTabs[tab][t][0]))
                self.dialog.scriptTabs[tab][t][1].setUndoRedoEnabled(True)
                self.dialog.scriptTabs[tab][t][1].setReadOnly(False)
                self.dialog.scriptTabs[tab][t][1].setOpenLinks(False)
                self.dialog.scriptTabs[tab][t][1].setOpenExternalLinks(False)
                self.dialog.scriptTabs[tab][t][1].setGeometry(QtCore.QRect(24, 24, 513, 345))
                self.dialog.scriptTabs[tab][t][1].setObjectName("%s_browser_%i"%(tab,t))
                text = ""
                for line in s:
                    tmp = ""
                    for arg in line:
                        try:
                            if ((arg >> 8)&0xFF) in (0x40,0x80):
                                tmp += "%s "%hex(arg)
                            else:
                                raise Exception
                        except:
                            tmp += "%s "%str(arg)
                    text += "%s\n"%tmp
                self.dialog.scriptTabs[tab][t][1].setPlainText(text)
                self.tabnames[tab][0].addTab(self.dialog.scriptTabs[tab][t][0],"%s_%i"%(tab,t+1))
                QtCore.QObject.connect(self.dialog.scriptTabs[tab][t][1], QtCore.SIGNAL("anchorClicked(QUrl)"), self.dialog.handleScriptUrl)
                t += 1
    def parseNavigation(self):
        self.cs = 0
        self.tabnames = {
"scr":[self.dialog.scriptTabWidget,self.scripts,self.dialog.navScript,"Script"],
"func":[self.dialog.funcTabWidget,self.functions,self.dialog.navFunc,"Function"],
"mov":[self.dialog.movTabWidget,self.movements,self.dialog.navMov,"Movement"]}
        for self.ctab in self.tabnames:
            self.tabnames[self.ctab][2].clear()
            for self.ct in range(0,len(self.tabnames[self.ctab][1])):
                QtGui.QTreeWidgetItem(self.tabnames[self.ctab][2])
                self.tabnames[self.ctab][2].topLevelItem(self.ct).setText(0,"%s %i"%(self.tabnames[self.ctab][3],self.ct+1))
                text = self.dialog.scriptTabs[self.ctab][self.ct][1].toPlainText()
                html = re.sub(r'script_(\d+)',self.replScript,str(text))
                #html = re.sub(r'func_(\d+)',r'<a href="function://\1">func_\1</a>',html)
                html = re.sub(r'func_(\d+)',self.replFunc,html)
                html = re.sub(r'mov_(\d+)',self.replMov,html)
                html = html.replace("\n","<br>")
                self.dialog.scriptTabs[self.ctab][self.ct][1].setHtml(html)
                
    def replFunc(self,matchObj):
        tmp = QtGui.QTreeWidgetItem(self.tabnames[self.ctab][2].topLevelItem(self.ct))
        i = int(matchObj.group(1))
        tmp.setText(0,"Function %i"%i)
        return "<a href=\"function://%i\">func_%i</a>"%(i,i)
    def replScript(self,matchObj):#Why is this even necessary!?
        tmp = QtGui.QTreeWidgetItem(self.tabnames[self.ctab][2].topLevelItem(self.ct))
        i = int(matchObj.group(1))
        tmp.setText(0,"Script %i"%i)
        return "<a href=\"script://%i\">script_%i</a>"%(i,i)
    def replMov(self,matchObj):
        tmp = QtGui.QTreeWidgetItem(self.tabnames[self.ctab][2].topLevelItem(self.ct))
        i = int(matchObj.group(1))
        tmp.setText(0,"Movement %i"%i)
        return "<a href=\"movement://%i\">mov_%i</a>"%(i,i)

    def doReadCmds(self):
        curcmd = 0
        curpos = self.reader.Position()
        cline = 0
        tmpContainer = []
        while curcmd not in (2,0x16,0x1b) and curpos < self.maxpos:
            try:
                curcmd = self.reader.ReadUInt16()
            except:
                print "Left script bounds (cmd): Position: %i / %i"%(self.reader.Position(),self.maxpos)
                curpos = self.maxpos
                break
            if curcmd > self.maxcmd:
                print "Mismatch: No command: %i"%curcmd
                break
            tmpContainer.append([])
            curxml = self.cmdsByNum[curcmd]
            cmdname = returnText(curxml.getElementsByTagName("name")[0])
            tmpContainer[cline].append(cmdname)
            carg = 1
            for child in curxml.getElementsByTagName("arg"):
                argsize = int(child.getAttribute("size"))
                try:
                    arg = self.readArg(argsize)
                except:
                    print "Left script bounds (arg): Position: %i / %i"%(self.reader.Position(),self.maxpos)
                    curpos = self.maxpos
                    break
                key = ""
                try:
                    key = str(child.getAttribute("key"))
                    if not key: 
                        raise Exception
                    if key == "func":
                        keyOff = self.reader.Position()+arg
                        if keyOff not in self.funcOffs:
                            self.funcOffs.append(keyOff)
                        arg = keyOff
                    if key == "mov":
                        keyOff = self.reader.Position()+arg
                        if keyOff not in self.movOffs:
                            self.movOffs.append(keyOff)
                        arg = keyOff
                    tmpContainer[cline].append([key,arg])
                    self.keyset[key].append([self.functype,self.s,cline,carg])
                except:
                    tmpContainer[cline].append(arg)
                carg += 1
            cline += 1
            curpos = self.reader.Position()
        if curcmd not in (2,0x16,0x1b):
            print "Error: Script did not parse!! Position: (%i / %i)" % (curpos,self.maxpos)
            print tmpContainer
        return tmpContainer
    def doReadMovs(self):
        curcmd = 0
        curpos = self.reader.Position()
        tmpContainer = []
        while curpos < self.maxpos:
            curcmd = self.reader.ReadUInt16()
            if curcmd > self.maxmovcmd:#oddly this takes care of the end command 0xFE
                break
            cmdname = self.movsByNum[curcmd]
            arg = self.reader.ReadUInt16()
            tmpContainer.append([cmdname,arg])
            curpos = self.reader.Position()
        return tmpContainer
    def doError(self,text):
        self.dialog.compileOutput.append(text)
        #self.dialog.tabWidget.setCurrentIndex(self.dialog.tabWidget.count()-1)
        self.dialog.tabWidget.setCurrentIndex(5)
    def writeScript(self):
        writer = bytereader.byteWriter()
        self.offsets = {"scr":[],"func":[],"mov":[]}
        self.rOffs = {"scr":[],"func":[],"mov":[]}
        ## ORDS ##
        for i in range(0,self.dialog.scriptOrdList.count()):
            item = int(str(self.dialog.scriptOrdList.item(i).text()).lstrip("Script "))
            self.offsets["scr"].append([item,writer.Position()])
            writer.WriteUInt32(0)
        writer.WriteUInt16(0xFD13)
        #print "Created ORD block"
        ## SCRIPTS ##
        self.tabnames = {
"scr":[self.dialog.scriptTabWidget],
"func":[self.dialog.funcTabWidget]}
        for tab in ["scr","func"]:
            for t in range(0,self.tabnames[tab][0].count()):
                self.rOffs[tab].append(writer.Position())
                scriptText = self.dialog.scriptTabs[tab][t][1].toPlainText()
                lines = scriptText.split("\n")
                for line in lines:
                    words = line.split(" ")
                    cmdname = words[0]
                    if cmdname == " " or not cmdname:
                        break
                    try:
                        curxml = self.cmdsByName[str(cmdname)]
                    except:
                        return self.doError("Error: No such command named: %s\n>>> %s\n>>> In %s_%i"%(cmdname,line,tab,t+1))
                    cmd = int(curxml.getAttribute("id"))
                    writer.WriteUInt16(cmd)
        
                    carg = 1
                    for child in curxml.getElementsByTagName("arg"):
                        argsize = int(child.getAttribute("size"))
                        arg = str(words[carg])
                        key = ""
                        try:
                            key = str(child.getAttribute("key"))
                            if not key: 
                                raise KeyError
                            if key == "func":
                                if "func_" not in arg:
                                    return self.doError("Error: Expected a function as an arg for %s\n>>> %s\n>>> In %s_%i"%(cmdname,line,tab,t+1))
                                item = int(arg.lstrip("func_"))
                                self.offsets["func"].append([item,writer.Position()])
                            if key == "mov":
                                if "mov_" not in arg:
                                    return self.doError("Error: Expected a movement as an arg for %s\n>>> %s\n>>> In %s_%i"%(cmdname,line,tab,t+1))
                                item = int(arg.lstrip("mov_"))
                                self.offsets["mov"].append([item,writer.Position()])
                            writer.WriteUInt32(0)
                        except KeyError:
                            #print "Arg: ",arg
                            if str(arg)[:2] == "0x":
                                num = int(arg,16)
                            elif str(arg)[:2] == "0b":
                                num = int(arg,2)
                            else:
                                num = int(arg)
                            if argsize == 8:
                                writer.WriteByte(num)
                            elif argsize == 16:
                                writer.WriteUInt16(num)
                            elif argsize == 32:
                                writer.WriteUInt32(num)
                            else:
                                print "Did not write:",num," Size:",argsize
                        carg += 1
            #print "Processed %s block"%tab
        for tab in ["mov"]:
            for t in range(0,self.dialog.movTabWidget.count()):
                self.rOffs[tab].append(writer.Position())
                scriptText = self.dialog.scriptTabs[tab][t][1].toPlainText()
                lines = scriptText.split("\n")
                for line in lines:
                    words = line.split(" ")
                    cmdname = words[0]
                    try:
                        cmdnum = self.movsByNum.index(str(cmdname))
                    except:
                        if cmdname in (""," "):
                            break
                        return self.doError("Error: No such command named: %s\n>>> %s\n>>> In %s_%i"%(cmdname,line,tab,t+1))
                    writer.WriteUInt16(cmdnum)
                    arg = words[1]
                    if str(arg)[:2] == "0x":
                        num = int(arg,16)
                    if str(arg)[:2] == "0b":
                        num = int(arg,2)
                    else:
                        num = int(arg)
                    writer.WriteUInt16(num)
                writer.WriteUInt16(0xFE)
        ## Reassociation ##
        for functype in self.offsets:
            for off in self.offsets[functype]:
                #off = [item, offset]
                val = self.rOffs[functype][off[0]-1]-off[1]-4
                writer.WriteUInt32At(val,off[1])
        dat = writer.ReturnData()
        result = struct.pack("B"*writer.Position(),*dat)
        self.dialog.scriptNarc.replaceFile(self.dialog.spinBox_3.value(), result)
        print "Wrote SCRIPT NARC successfully"







