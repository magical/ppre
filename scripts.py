import narc
import sys
import string

class scriptFile:
    def __init__(self,file, ID):
        self.numscripts=0
        self.bytes=[]
        self.funcKeys=[]
        self.reg=False
        self.numScripts=0
        self.text=""
        self.size=0
        self.ID=ID
        if ID== 0x5353 or ID== 0x4748:
            global cmd, jumpcmds, endcmds, movCmd
            cmd = cmd_gs[:]
            jumpcmds = jumpcmds_gs[:]
            endcmds = endcmds_gs[:]
            movCmd = movCmd_gs[:]
        self.getParam={1:readByte,2:readUInt16,4:readUInt32}
        for chr in file:
            self.bytes.append(ord(chr))
            self.size+=1
        for i in range(0,len(self.bytes),4):
            if self.reg == False:
                temp=readUInt32(self.bytes,i)
                if  temp & 0xFFFF == 0xFD13:
                    self.reg=True
                    self.numScripts=i/4
        
        """if self.reg==False:
            self.alt=False
            for i in range(0,len(self.bytes),4):
                if self.alt == False:
                    temp=readUInt32(self.bytes,i)
                    if  temp & 0xFFFF == 2:
                        self.reg=True
                        self.alt=True
                        self.numScripts=i/4"""
        self.scrOffsets=[]
        self.ords=[]
        self.scrs={}
        self.movs={}
        self.funcs={}
        if not self.reg:
            self.alt=False
            for i in range(0,len(self.bytes),4):
                if self.alt == False:
                    for j in range(0, len(self.scrOffsets)):
                        if i+2>=self.scrOffsets[j][0]:
                            self.alt=True
                if self.alt == False:
                   self.scrOffsets.append((readUInt32(self.bytes,i)+i+4, "ord_"+str(i/4)))
        else:
            for i in range(0,self.numScripts):
                self.scrOffsets.append((readUInt32(self.bytes,i*4)+4*i+4,"ord_"+str(i)))
        scrnum=0
        for i in self.scrOffsets:
            if self.scrs.has_key(i[0]):
                self.ords.append(self.scrs[i[0]])
            else:
                self.scrs[i[0]]="scr_"+str(scrnum)
                self.ords.append(self.scrs[i[0]])
                scrnum+=1
        self.peekScript()
    def getOrders(self):
        self.ordText=""
        for i in range(0, len(self.ords)):
            self.ordText+=str(i)+" "+self.ords[i]+"\n"
        return self.ordText
    def getScript(self):
        keyS = self.scrs.values()
        keyT = {}
        keyS.sort(lambda x,y: -1 if int(x[4:])<int(y[4:]) else 1)
        for key,val in self.scrs.items():
            keyT[val] = key
        for key in keyS:
            self.text+="\n==="+key+"\n"
            self.curPos=keyT[key]
            curcmd=readUInt16(self.bytes, self.curPos)
            while curcmd not in endcmds:
                self.procCmd(curcmd)
                curcmd=readUInt16(self.bytes, self.curPos)
            else:
                self.text+=cmd[curcmd][0]+"\n"
        keyS=self.funcs.values()
        keyT = {}
        keyS.sort(lambda x,y: -1 if int(x[5:])<int(y[5:]) else 1)
        for key,val in self.funcs.items():
            keyT[val] = key
        for key in keyS:
            #print key
            self.text+="\n=="+key+"\n"
            self.curPos=keyT[key]
            curcmd=readUInt16(self.bytes, self.curPos)
            while curcmd not in endcmds:
                self.procCmd(curcmd)
                if curcmd==0x16:
                    break
                curcmd=readUInt16(self.bytes, self.curPos)
            else:
                self.text+=cmd[curcmd][0]+"\n"
        keyS=self.movs.values()
        keyT = {}
        keyS.sort(lambda x,y: -1 if int(x[4:])<int(y[4:]) else 1)
        for key,val in self.movs.items():
            keyT[val] = key
        for key in keyS:
            self.text+="\n="+key+"\n"
            self.curPos=keyT[key]
            movcmd=readUInt16(self.bytes,self.curPos)
            self.curPos+=2
            while movcmd!=0xFE:
                #print movcmd
                self.text+= movCmd[movcmd]
                self.text+=" "+hex(readUInt16(self.bytes, self.curPos))+"\n"
                self.curPos+=2
                movcmd=readUInt16(self.bytes,self.curPos)
                self.curPos+=2
            else:
                self.text+="End\n"
                self.curPos+=2
        return self.text
    def procCmd(self,num):
        self.curPos+=2
        #print num
        self.text+=str(cmd[num][0])
        if(cmd[num][1]>0):
            if num in (0x16, 0x1A):
                self.text+=" "+self.funcs[readInt32(self.bytes, self.curPos)+self.curPos+4]
                self.curPos+=4
            elif num in (0x1C, 0x1D):
                self.text+=" "+hex(self.getParam[1](self.bytes, self.curPos))
                self.curPos+=1
                self.text+=" "+self.funcs[readInt32(self.bytes, self.curPos)+self.curPos+4]
                self.curPos+=4
            elif num ==0x5E:
                self.text+=" "+hex(readUInt16(self.bytes, self.curPos))
                self.curPos+=2
                self.text+=" "+self.movs[readInt32(self.bytes, self.curPos)+self.curPos+4]
                self.curPos+=4
            elif num in (0x11D, 0x1CF, 0x1E1, 0x21D,0x235, 0x23E, 0x2C4,0x2C9, 0x2CA,0x2CD,  0x2CF):
                if num==0x11D:
                    param=[]
                    param.append(self.getParam[2](self.bytes,self.curPos))
                    self.curPos+=2
                    param.append(self.getParam[2](self.bytes,self.curPos))
                    self.curPos+=2
                    if self.ID==0x4C50:
                        param.append(self.getParam[2](self.bytes,self.curPos))
                        self.curPos+=2
                elif num==0x1CF:
                    param=[]
                    param.append(self.getParam[1](self.bytes, self.curPos))
                    self.curPos+=1
                    if param[0]==2:
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                elif num==0x1E1:
                    param=[]
                    if self.ID==0x4C50:
                        for i in range (0,cmd[num][1]):
                            param.append(self.getParam[cmd[num][i+2]](self.bytes,self.curPos))
                            self.curPos+=cmd[num][i+2]
                    else:
                        param.append(self.getParam[2](self.bytes,self.curPos))
                        self.curPos+=2
                        param.append(self.getParam[2](self.bytes,self.curPos))
                        self.curPos+=2
                elif num==0x21D:
                    param=[]
                    param.append(self.getParam[2](self.bytes, self.curPos))
                    self.curPos+=2
                    if param[0]!=6:
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        if param[0]!=5:
                            param.append(self.getParam[2](self.bytes, self.curPos))
                            self.curPos+=2 
                elif num==0x235:
                    param=[]
                    param.append(self.getParam[2](self.bytes, self.curPos))
                    self.curPos+=2
                    if param[0] in (0, 1, 3, 4, 6):
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        if param[0] in (1, 3, 4):
                            param.append(self.getParam[2](self.bytes, self.curPos))
                            self.curPos+=2
                            if param [0] in (1, 3):
                                param.append(self.getParam[2](self.bytes, self.curPos))
                                self.curPos+=2
                elif num==0x23E:
                    param=[]
                    if self.ID in (0x5353, 0x4748):
                        for i in range (0,cmd[num][1]):
                            param.append(self.getParam[cmd[num][i+2]](self.bytes,self.curPos))
                            self.curPos+=cmd[num][i+2]
                    else:
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        if param[0] in (1,3, 5, 6) :
                            param.append(self.getParam[2](self.bytes, self.curPos))
                            self.curPos+=2
                            if param[0] in (5, 6):
                                param.append(self.getParam[2](self.bytes, self.curPos))
                                self.curPos+=2
                elif num==0x2C4:
                    param=[]
                    param.append(self.getParam[1](self.bytes, self.curPos))
                    self.curPos+=1
                    if param[0] in (0, 1):
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                elif num==0x2C9:
                    param=[]
                    if self.ID!=0x4C50:
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        self.curPos+=1
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        self.curPos+=1
                elif num==0x2CA:
                    param=[]
                    if self.ID!=0x4C50:
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        self.curPos+=1
                elif num==0x2CD:
                    param=[]
                    if self.ID!=0x4C50:
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        #print param[0]
                        self.curPos+=1
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        #print param[1]
                elif num==0x2CF:
                    param=[]
                    if self.ID==0x4C50:
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                    else:
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        self.curPos+=1
                for i in range(0, len(param)):
                    self.text+=" "+hex(param[i])
            else:
                for i in range (0,cmd[num][1]):
                    self.text+=" "+hex(self.getParam[cmd[num][i+2]](self.bytes,self.curPos))
                    self.curPos+=cmd[num][i+2]
        self.text+="\n"
    def peekScript(self):
        #print self.bytes
        for key in self.scrs.keys():
            #print "\n==="+self.scrs[key]+""
            self.curPos=key
            curcmd=readUInt16(self.bytes, self.curPos)
            while curcmd not in endcmds:
                self.peekCmd(curcmd)
                curcmd=readUInt16(self.bytes, self.curPos)
            #else:
                #print cmd[curcmd][0]
        self.keyProc=0
        """for key in self.funcs.keys():
            self.funcKeys.append(key)"""
        while self.keyProc<len(self.funcKeys):
            key=self.funcKeys[self.keyProc]
            self.keyProc+=1
            #print "\n=="+self.funcs[key]
            #print self.curPos
            self.curPos=key
            curcmd=readUInt16(self.bytes, self.curPos)
            while curcmd not in endcmds:
                self.peekCmd(curcmd)
                if curcmd==0x16:
                    break
                curcmd=readUInt16(self.bytes, self.curPos)
            #else:
                #print cmd[curcmd][0]
        for key in self.movs.keys():
            #print "\n="+self.movs[key]
            self.curPos=key
            movcmd=readUInt16(self.bytes,self.curPos)
            self.curPos+=2
            while movcmd!=0xFE:
                #print hex(movcmd)
                #print " "+hex(readUInt16(self.bytes, self.curPos))+" "
                self.curPos+=2
                movcmd=readUInt16(self.bytes,self.curPos)
                self.curPos+=2
            #else:
               # print "End\n"
            self.curPos+=2
    def peekCmd(self, num):
        self.curPos+=2
        #print hex(num)+" "+cmd[num][0]
        if(cmd[num][1]>0):
            if num==0x5E:
                keyvalue=readInt32(self.bytes, self.curPos+2)+self.curPos+6
                if keyvalue not in self.movs.keys():
                    self.movs[keyvalue]="mov_"+str(len(self.movs))
            if num in jumpcmds:
                if num==0x16 or num==0x1A:
                    keyvalue=readInt32(self.bytes, self.curPos)+self.curPos+4
                    if keyvalue not in self.funcKeys:
                        self.funcs[keyvalue]="func_"+str(len(self.funcs))
                        self.funcKeys.append(keyvalue)
                else:
                    keyvalue=readInt32(self.bytes, self.curPos+1)+self.curPos+5
                    if keyvalue not in self.funcKeys:
                        self.funcs[keyvalue]="func_"+str(len(self.funcs))
                        self.funcKeys.append(keyvalue)
            if num in (0x11D, 0x1CF, 0x1E1, 0x21D, 0x235, 0x23E, 0x2C4, 0x2C9, 0x2CA, 0x2CD, 0x2CF):
                if num==0x11D:
                    param=[]
                    param.append(self.getParam[2](self.bytes,self.curPos))
                    self.curPos+=2
                    param.append(self.getParam[2](self.bytes,self.curPos))
                    self.curPos+=2
                    if self.ID==0x4C50:
                        param.append(self.getParam[2](self.bytes,self.curPos))
                        self.curPos+=2
                elif num==0x1CF:
                    param=[]
                    param.append(self.getParam[1](self.bytes, self.curPos))
                    self.curPos+=1
                    if param[0]==2:
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                elif num==0x1E1:
                    param=[]
                    if self.ID==0x4C50:
                        for i in range (0,cmd[num][1]):
                            param.append(self.getParam[cmd[num][i+2]](self.bytes,self.curPos))
                            self.curPos+=cmd[num][i+2]
                    else:
                        param.append(self.getParam[2](self.bytes,self.curPos))
                        self.curPos+=2
                        param.append(self.getParam[2](self.bytes,self.curPos))
                        self.curPos+=2
                elif num==0x21D:
                    param=[]
                    param.append(self.getParam[2](self.bytes, self.curPos))
                    self.curPos+=2
                    if param[0]!=6:
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        if param[0]!=5:
                            param.append(self.getParam[2](self.bytes, self.curPos))
                            self.curPos+=2
                elif num==0x235:
                    param=[]
                    param.append(self.getParam[2](self.bytes, self.curPos))
                    self.curPos+=2
                    if param[0] in (0, 1, 3, 4, 6):
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        if param[0] in (1, 3, 4):
                            param.append(self.getParam[2](self.bytes, self.curPos))
                            self.curPos+=2
                            if param [0] in (1, 3):
                                param.append(self.getParam[2](self.bytes, self.curPos))
                                self.curPos+=2
                elif num==0x23E:
                    param=[]
                    if self.ID in (0x5353, 0x4748):
                        for i in range (0,cmd[num][1]):
                            param.append(self.getParam[cmd[num][i+2]](self.bytes,self.curPos))
                            self.curPos+=cmd[num][i+2]
                    else:
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        if param[0] in (1,3, 5, 6) :
                            param.append(self.getParam[2](self.bytes, self.curPos))
                            self.curPos+=2
                            if param[0] in (5, 6):
                                param.append(self.getParam[2](self.bytes, self.curPos))
                                self.curPos+=2
                elif num==0x2C4:
                    param=[]
                    param.append(self.getParam[1](self.bytes, self.curPos))
                    self.curPos+=1
                    if param[0] in (0, 1):
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                elif num==0x2C9:
                    param=[]
                    if self.ID!=0x4C50:
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        self.curPos+=1
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        self.curPos+=1
                elif num==0x2CA:
                    param=[]
                    if self.ID!=0x4C50:
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        self.curPos+=1
                elif num==0x2CD:
                    param=[]
                    if self.ID!=0x4C50:
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        #print param[0]
                        self.curPos+=1
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        #print param[1]
                elif num==0x2CF:
                    param=[]
                    if self.ID==0x4C50:
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                        param.append(self.getParam[2](self.bytes, self.curPos))
                        self.curPos+=2
                    else:
                        param.append(self.getParam[1](self.bytes, self.curPos))
                        self.curPos+=1
                #for i in range(0, len(param)):
                    #print " "+hex(param[i]), 
            else: 
                for i in range (0,cmd[num][1]):
                    #print " "+hex(self.getParam[cmd[num][i+2]](self.bytes,self.curPos)),
                    self.curPos+=cmd[num][i+2]
        #print "\n"
    def procMov(self, num):
        self.text+=movCmd[num]
        self.curPos+=2
    def getBinary(self, scrText, scrOrder):
        self.sC=[]
        self.binary=[]
        self.oC=[]
        self.order=[]
        for char in scrText:
            self.sC.append(str(char));
        for char in scrOrder:
            self.oC.append(str(char));
        self.bP=0
        self.cP=0
        self.error=False
        self.lP=0
        self.pOrd=[]
        self.bScr={}
        self.bFunc={}
        self.bMov={}
        self.pFunc={}
        self.pMov={}
        self.isMovCmd=False
        while(self.cP<len(self.sC)):
            if self.error==False:
                #print self.bP
                self.procLine()
                self.lP+=1
            else:
                print "ERROR"
                print self.errorText
                break
        if self.error==True:
            return False
        else:
            r=""
            for pos in self.pFunc.keys():
                writeInt32(self.binary, pos, self.bFunc[self.pFunc[pos]]-4-pos)
            for pos in self.pMov.keys():
                writeInt32(self.binary, pos, self.bMov[self.pMov[pos]]-4-pos)
            self.buildHeader()
            #print self.bScr
            for bin in self.order:
                r+=chr(int(bin))
            for bin in self.binary:
                r+=chr(int(bin))
            return r
    def buildHeader(self):
        self.oP=0
        while self.oP<len(self.oC):
            while self.oC[self.oP]!=" ":
                self.oP+=1
            while self.oC[self.oP]==" ":
                self.oP+=1
            word=""
            while self.oP<len(self.oC) and self.oC[self.oP] not in (" ", "\n"):
                word+=self.oC[self.oP]
                self.oP+=1
            else:
                while self.oP<len(self.oC) and self.oC[self.oP]!="\n":
                    self.oP+=1
            self.pOrd.append(word)
            self.oP+=1
        headsize=len(self.pOrd)
        for i in range(0, 4*headsize+2):
            self.order.append(0)
        for i in range(0, headsize):
            writeInt32(self.order, i*4, self.bScr[self.pOrd[i]]+headsize*4+2-(i*4)-4)
        writeUInt16(self.order, headsize*4, 0xFD13)
    def cmdIndex(self, cmdName):
        for i in range(0, 0x348):
            if cmd[i][0]==cmdName:
                return i
        else:
            return 0xFFFF
    def movCmdIndex(self, cmdName):
        for i in range(0, 0x70):
            if movCmd[i]==cmdName:
                return i
        else:
            if cmdName=='End':
                return 0xFE
            else:
                return 0xFFFF
    def procLine(self):
        if self.sC[self.cP]=="=":
            self.cP+=1
            if self.sC[self.cP]=="=":
                self.cP+=1
                if self.sC[self.cP]=="=":
                    self.isMovCmd=False
                    self.cP+=1
                    scrName=self.readWord()
                    self.ignore()
                    if scrName not in self.bScr.keys():
                        self.bScr[scrName]=self.bP
                    else:
                        self.error=True
                        self.errorText=("Duplicate script definition", scrName)
                    self.cP+=1
                else:
                    self.isMovCmd=False
                    funcName=self.readWord()
                    self.ignore()
                    if funcName not in self.bFunc.keys():
                        self.bFunc[funcName]=self.bP
                    else:
                        self.error=True
                        self.errorText=("Duplicate function definition", funcName)
                    self.cP+=1
            else:
                self.isMovCmd=True
                movName=self.readWord()
                self.ignore()
                while not (self.bP+2)%4==0:
                    self.binary.append(0)
                    self.bP+=1
                if movName not in self.bMov.keys():
                    self.bMov[movName]=self.bP
                else:
                    self.error=True
                    self.errorText=("Duplicate movement definition", movName)
                self.cP+=1
        elif self.sC[self.cP] !="\n":
            pC=self.readWord()
            if self.isMovCmd==False:
                cI=self.cmdIndex(pC)
            else:
                cI=self.movCmdIndex(pC)
            if cI!=0xFFFF:
                #print hex(cI), "cmd"
                self.ignoreSp()
                if self.isMovCmd==False:
                    self.bProcCmd(cI)
                else:
                    self.bProcMovCmd(cI)
            else:
                print "Error with Mov"
                self.error=True
                self.errorText=("Invalid Command",  pC)
            self.cP+=1
        else:
            self.cP+=1
    def bProcMovCmd(self, cmdNum):
        self.growBinary(2)
        writeUInt16(self.binary, self.bP, cmdNum)
        self.bP+=2
        if(cmdNum!=0xFE):
            #print movCmd[cmdNum]
            self.readParam(2)
        else:
            self.binary.append(0)
            self.bP+=1
            self.binary.append(0)
            self.bP+=1
        self.ignore()
    def bProcCmd(self, cmdNum):
        self.growBinary(2)
        writeUInt16(self.binary, self.bP, cmdNum)
        self.bP+=2
        if cmdNum in (0x16, 0x1A, 0x1C, 0x1D, 0x5E, 0x11D, 0x1CF, 0x1E1, 0x21D, 0x235, 0x23E, 0x2C4, 0x2C9, 0x2CA, 0x2CD, 0x2CF):
            self.ignoreSp()
            if cmdNum in (0x16, 0x1A):
                self.pFunc[self.bP]=self.readWord()
                self.growBinary(4)
                self.bP+=4
            elif cmdNum in (0x1C, 0x1D, 0x5E):
                if cmdNum==0x5E:
                    self.readParam(2)
                    self.ignoreSp()
                    self.growBinary(4)
                    self.pMov[self.bP]=self.readWord()
                else:
                    self.readParam(1)
                    self.ignoreSp()
                    self.growBinary(4)
                    self.pFunc[self.bP]=self.readWord()
                self.bP+=4
            elif num==0x11D:
                    params=self.getParams()
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[0])
                    self.bP+=2
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[1])
                    self.bP+=2
                    if self.ID==0x4C50:
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[2])
                        self.bP+=2
            elif cmdNum==0x1CF:
                params=self.getParams()
                if len(params > 0):
                    self.binary.append(params[0]&0xFF);
                    self.bP+=1
                    if params[0]==2 and len (params)>1:
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[1])
                        self.bP+=2
                else:
                    self.error=True
                    self.errorText=("Insufficient Paramenters", 0x1CF)
            elif num==0x1E1:
                    params=self.getParams()
                    if self.ID==0x4C50:
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[0])
                        self.bP+=2
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[1])
                        self.bP+=2
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[2])
                        self.bP+=2
                    else:
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[0])
                        self.bP+=2
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[1])
                        self.bP+=2
            elif cmdNum==0x21D:
                params=self.getParams()
                if len(params > 0):
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[0])
                    self.bP+=2
                    if param[0]!=6 and len(params)>1:
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[1])
                        self.bP+=2
                        if param[0]!=5 and len(params)>2:
                            self.growBinary(2)
                            writeUInt16(self.binary, self.bP, params[2])
                            self.bP+=2
                else:
                    self.error=True
                    self.errorText=("Insufficient Paramenters", 0x21D)
            elif num==0x235:
                params=self.getParams()
                if len(params) > 0:
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[0])
                    self.bP+=2
                    if param[0] in (0, 1, 3, 4, 6):
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[1])
                        self.bP+=2
                        if param[0] in (1, 3, 4):
                            self.growBinary(2)
                            writeUInt16(self.binary, self.bP, params[2])
                            self.bP+=2
                            if param [0] in (1, 3):
                                self.growBinary(2)
                                writeUInt16(self.binary, self.bP, params[3])
                                self.bP+=2
            elif num==0x23E:
                params=self.getParams()
                if self.ID in (0x5353, 0x4748):
                    #pP=Parameters proccessed
                    pP=0
                    #print cmd[cmdNum][1], 
                    while self.sC[self.cP] !="\n" and pP<cmd[cmdNum][1]:
                        #self.growBinary(cmd[cmdNum][pP+2])
                        self.readParam(cmd[cmdNum][pP+2])
                        #print pP
                        pP+=1
                    if pP!=cmd[cmdNum][1]:
                        self.error=True
                        self.errorText=("Not enough parameters",  cmdNum)
                    self.ignore()
                else:
                    if len(params)>0:
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[0])
                        self.bP+=2
                        if param[0] in (1,3, 5, 6) :
                            self.growBinary(2)
                            writeUInt16(self.binary, self.bP, params[1])
                            self.bP+=2
                            if param[0] in (5, 6):
                                self.growBinary(2)
                                writeUInt16(self.binary, self.bP, params[0])
                                self.bP+=2
            elif num==0x2C4:
                    params=self.getParams()
                    self.binary.append(params[0]&0xFF);
                    self.bP+=1
                    if param[0] in (0, 1):
                        self.growBinary(2)
                        writeUInt16(self.binary, self.bP, params[1])
                        self.bP+=2
            elif num==0x2C9:
                params=self.getParams()
                if self.ID!=0x4C50:
                    self.binary.append(params[0]&0xFF);
                    self.bP+=1
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[1])
                    self.bP+=2
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[2])
                    self.bP+=2
                    self.binary.append(params[3]&0xFF);
                    self.bP+=1
            elif num==0x2CA:
                params=self.getParams()
                if self.ID!=0x4C50:
                    self.binary.append(params[0]&0xFF);
                    self.bP+=1
            elif num==0x2CD:
                params=self.getParams()
                if self.ID!=0x4C50:
                    self.binary.append(params[0]&0xFF);
                    self.bP+=1
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[1])
                    self.bP+=2
            elif num==0x2CF:
                params=self.getParams()
                if self.ID==0x4C50:
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[0])
                    self.bP+=2
                    self.growBinary(2)
                    writeUInt16(self.binary, self.bP, params[1])
                    self.bP+=2
                else:
                    self.binary.append(params[0]&0xFF);
                    self.bP+=1
        else:
            #pP=Parameters proccessed
            pP=0
            #print cmd[cmdNum][1], 
            while self.sC[self.cP] !="\n" and pP<cmd[cmdNum][1]:
                #self.growBinary(cmd[cmdNum][pP+2])
                self.readParam(cmd[cmdNum][pP+2])
                #print pP
                pP+=1
            if pP!=cmd[cmdNum][1]:
                self.error=True
                self.errorText=("Not enough parameters",  cmdNum)
            self.ignore()
    def readParam(self, size):
        self.ignoreSp()
        num=""
        self.isHex=False
        if self.sC[self.cP]=="0" and self.sC[self.cP+1]=="x":
            self.isHex=True
            self.cP+=2
        while self.sC[self.cP] not in (" ", "\n"):
            num+=self.sC[self.cP]
            self.cP+=1
        if size==1:
            self.growBinary(1)
            if self.isHex==True:
                writeByte(self.binary, self.bP, int(num,16))
            else:
                writeByte(self.binary, self.bP, int(num,10))
            self.bP+=1
        elif size==2:
            self.growBinary(2)
            if self.isHex==True:
                writeUInt16(self.binary, self.bP, int(num, 16))
            else:
                writeUInt16(self.binary, self.bP, int(num, 10))
            self.bP+=2
        else:
            self.growBinary(4)
            if self.isHex==True:
                writeInt32(self.binary, self.bP, int(num,16))
            else:
                writeInt32(self.binary, self.bP, int(num, 10))
            self.bP+=4
    def readWord(self):
        word=""
        while self.sC[self.cP] not in (" ", "\n"):
            word+=self.sC[self.cP]
            self.cP+=1
        return word
    def readParams(self):
        params=[]
        while(self.sC[self.cP]!="\n"):
            self.ignoreSp()
            params.append[int(self.readWord(), 0)]
        return params
    def ignore(self):
        while self.sC[self.cP]!="\n":
            self.cP+=1
    def ignoreSp(self):
        while self.sC[self.cP]==" ":
            self.cP+=1
    def growBinary(self, num):
        for i in range(0, num):
            self.binary.append(0)
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
cmd=(("Nop",0),
("Nop1",0),
("End",0),
("Return",2,2,2),
("0004",1,2),
("0005",0),
("0006",0),
("0007",0),
("0008",0),
("0009",0),
("000A",0),
("000B",0),
("000C",0),
("000D",0),
("000E",0),
("000F",0),
("0010",4,2,2,2,2),
("If",2,2,2),
("If2",2,2,2),
("0013",0),
("Callstd",1,2),
("0015",0),
("Jump",1,4),
("0017",4,2,2,2,2),
("0018",0),
("0019",0),
("Goto",1,4),
("Killscript",0),
("COMPARELASTRESULT" ,2,1,4),
("COMPARELASTRESULT1",2,1,4),
("Clearflag",1,2),
("Setflag",1,2),
("Checkflag",1,2),
("0021",0),
("0022",1, 2),
("0023",1,2),
("0024",1,2),
("0025",1,2),
("Comparevarstobyte",2,2,2),
("0027",2,2,2),
("Setvar",2,2,2),
("Copyvar",2,2,2),
("002A",0),
("002B",1,1),
("Message",1,1),
("Message2",1,2),
("002E" ,1, 2),
("Message3",1,1),
("0030",0),
("Waitbutton",0),
("0032",0),
("0033",0),
("Closemsgonkeypress",0),
("Freezemsgbox",0),
("Callmsgbox",3,2,2,2),
("Colormsgbox",2,1,2),
("Typemsgbox",1,1),
("NoMapmsgbox",0),
("Callmsgboxtext",2,1,2),
("003B",1,2),
("Menu",0),
("003D",0),
("Yesnobox",1,2),
("Waitfor",1,2),
("Multi",5,1,1,1,1,2),
("Multi2",5,1,1,1,1,2),
("Txtscrpmulti",2,1,1),
("CloseMulti",0),
("Multi3",5,1,1,1,1,2),
("0045",3,2,2,2),
("Txtmsgscrpmulti",3,2,2,2),
("0047",0),
("Multirow",1,1),
("PlaySound",1,2),
("004A",1,2),
("004B",1,2),
("Cryfr",2,2,2),
("Waitcry",0),
("Soundfr",1,2),
("Fadedef",0),
("0050",1,2),
("Stop",1,2),
("Restart",0),
("0053",0),
("0054",2,2,2),
("0055",1,2),
("0056",0),
("0057",1, 2),
("0058",4, 1, 1, 1, 1),
("0059",1, 2),
("005A",2,2,2),
("005B",0),
("005C",0),
("005D",0),
("Applymovement",2,2,4),
("Waitmovement",0),
("Lockall",0),
("Releaseall",0),
("Lock",1,2),
("Release",1,2),
("Addpeople",1,2),
("Removepeople",1,2),
("Lockcam",2,2,2),
("0067",0),
("Faceplayer",0),
("CheckSpritePosition",2,2,2),
("006A",0),
("006B",3,2,2,2),
("Continuefollow(Changemap)",2,1,2),
("Followhero",2,2,2),
("StopFollowhero",0),
("Givemoney",1,2),
("Takemoney",2,2,2),
("Checkmoney",3,2,2,2),
("Showmoney",2,2,2),
("Hidemoney",0),
("Updatemoney",0),
("Showcoins",2,2,2),
("Hidecoins",0),
("Updatecoins",0),
("Checkcoins",3,2,2,2),
("Givecoins",1,2),
("Takecoins",3,2,2,2),
("Takeitem",3,2,2,2),
("Giveitem",3,2,2,2),
("Checkstoreitem",3,2,2,2),
("Checkitem",3,2,2,2),
("007F",2,2,2),
("0080",2,2,2),
("0081",0),
("0082",0),
("0083",3,2,2,2),
("0084",0),
("0085",3,2,2,2),
("0086",0),
("0087",3,2,2,2),
("0088",0),
("0089",0),
("008A",0),
("008B",0),
("008C",0),
("008D",0),
("008E",0),
("008F",3,2,2,2),
("0090",0),
("0091",0),
("0092",0),
("0093",2,2,2),
("0094",2,2,2),
("0095",2,2,2),
("GivePokemon",4,2,2,2,2),
("GiveEgg",2,2,2),
("0098",0),
("Checkmove",3,2, 2, 2),
("009A",2,2,2),
("009B",2,2,2),
("009C",3,2,2,2),
("009D",0),
("009E",0),
("009F",0),
("00A0",0),
("Callend",0),
("00A2",0),
("Wfc",0),
("00A4",0),
("Interview",0),
("DressPokemon",3,2,2,2),
("DisplayDressedPokemon",2,2,2),
("00A8",2,2,2),
("CapsuleEditor",0),
("SinnohMaps",0),
("BoxPkmn",1,1),
("DrawUnion",0),
("TrainerCaseUnion",0),
("00AE",0),
("RecordMixingUnion",0),
("EndGame",0),
("HallFameData",0),
("00B2",2,2,2),
("Wfc",1,2),
("ChooseStarter",0),
("00B5",0),
("00B6",1, 2),
("00B7",2, 2, 2),
("00B8",1, 2),
("00B9",2, 2, 2),
("ChoosePlayerName",0),
("ChoosePokemnName",2,2,2),
("Fadescreen",4,2,2,2,2),
("Resetscreen",0),
("Warp",5,2,2,2,2,2),
("RockClimbAnimation",1, 2),
("SurfAnimation",1, 2),
("WaterfallAnimation",1, 2),
("FlyAnimation",1, 2),
("00C3",0),
("00C4",0),
("00C5",1, 2),
("Tuxedo",0),
("Checkbike",1,2),
("Ridebike",1,1),
("00C9",1,1),
("00CA",0),
("BerryHiroAnimation",1,2),
("StopBerryHiroAnimation",0),
("Setvarhero",1,1),
("Setvarrival",1,1),
("Setvaralter",1,1),
("Setvarpoke",2,1,2),
("Setvaritem",2,1,2),
("00D2",2, 1, 2),     
("Setvaratkitem",2,1,2),
("Setvaratk",2,1,2),
("Setvarnum",2,1,2),
("Setvarpokenick",2,1,2),
("Setvarobj",2,1,2),
("Setvartrainer",0),
("00D9",1,1),
("Setvarpokestored",4,1,2,2,1),
("Setvarstrhero",1,1),
("Setvarstrrival",1,1),
("Setvarstralter",1,1),
("StoreStarter",1,2),
("00DF",2,1,2),
("00E0",2,1,2),
("00E1",2,1,2),
("00E2",2,1,2),
("00E3",2,2,2),
("00E4",1,2),
("Trainerbattle",2,2,2),
("Endtrainerbattle",2,2,2),
("00E7",3,2,2,2),
("00E8",3,2,2,2),
("00E9",1,2),
("ActLeaugueBattlers",1,2),
("LostGoPc",0),
("CheckLost",1,2),
("00ED",1,2),
("00EE",1,2),
("00EF",0),
("00F0",0),
("00F1",0),
("ChsFriend",4,2,2,2,2),
("WireBattleWait",4,2,2,2,2),
("00F4",0),
("00F5",0),
("00F6",0),
("Pokecontest",0),
("00F8",1,2),
("00F9",1,2),
("00FA",4,2,2,2,2),
("00FB",1,2),
("00FC",0),
("00FD",2,2,2),
("00FE",2,2,2),
("00FF",2,2,2),
("0100",0),
("0101",0),
("0102",2,1,1),
("0103",2,1,1),
("0104",0),
("0105",0),
("0106",0),
("0107",1,2),
("0108",0),
("0109",1,2),
("010A",2,2,2),
("010B",2,2,2),
("010C",1, 2),
("010D",0),
("010E",0),
("010F",0),
("0110",4,2,2,2,2),
("FlashContest",1,2),
("EndFlash",0),
("0113",0),
("0114",0),
("0115",2,2,2),
("ShowLnkCntRecord",0),
("0117",0),
("0118",0),
("0119",1,2),
("011A",0),
("WarpMapElevator",5,2,2,2,2,2),
("CheckFloor",1,2),
("011D",3, 2, 2, 2),
("011E",1,2),
("011F",0),
("Setposaftship",4,2,2,1,2),
("0121",1, 2),
("0122",1,2),
("0123",2, 1, 2),
("Wildbattle",4,2,2,2,2),
("Starterbattle",4,2,2,2,2),
("Explantionbattle",0),
("Honeytreebattle",3,2,2,2),
("0128",1,2),
("Randombattle",0),
("012A",0),
("WriteAutograph",0),
("012C",1,2),
("012D",2,2,2),
("CheckDress",2,2,2),
("012F",2,2,2),
("0130",1,2),
("GivePoketch",0),
("0132",1,2),
("ActPktchAppl",1,2),
("StorePktchAppl",2,2,2),
("0135",1,2),
("0136",0),
("0137",0),
("0138",1,2),
("0139",1,2),
("013A",0),
("013B",0),
("013C",1,2),
("013D",0),
("013E",0),
("013F",2,2,2),
("0140",1,2),
("0141",1,2),
("0142",1,2),
("ExpectDecisionOther",2,2,2),
("0144",1,2),
("0145",1,2),
("0146",2,2,2),
("Pokemart",1,2),
("Pokemart1",1,2),
("Pokemart2",1,2),
("Pokemart3",1,2),
("Defeatgopc",0),
("014C",1,2),
("Checkgender",1,2),
("HealPkmn",0),
("014F",0),
("0150",0),
("0151",0),
("0152",1,2),
("UnionRoom",0),
("0154",0),
("0155",2,2,2),
("0156",1,2),
("0157",0),
("ActPokedex",0),
("0159",0),
("GiveRShoes",0),
("Checkbadge",2,2,2),
("Setbdgtrue",1,2),
("Setbdgfalse",1,2),
("015E",0),
("015F",0),
("0160",1, 2),
("0161",0),
("0162",0),
("0163",0),
("0164",0),
("0165",0),
("0166",1,2),
("0167",0),
("PrpDoorAnm",5,2,2,2,2,1),
("Waitaction",1,1),
("Waitclose",1,1),
("Opendoor",1,1),
("Closedoor",1,1),
("016D",0),
("016E",0),
("016F",0),
("0170",0),
("0171",0),
("0172",0),
("0173",0),
("0174",0),
("0175",3,2,2,2),
("0176",2,2,1),
("Checkpartynumber",1,2),
("OpnBerry",1, 1),
("0179",1, 2),
("017A",0),
("017B",3, 1, 2, 2),
("017C",2,1,2),
("017D",1, 2),
("017E",1, 2),
("017F",1, 2),
("0180",0),
("0181",1, 2),
("0182",1,2),
("0183",1,2),
("0184",0),
("0185",0),
("SetOwPosition",3,2,2,2),
("0187",5,2,2,2,2,2),
("SetOwMovement",2,2,2),
("ReleaseOw",2,2,2),
("SetDoorPassable",3,2,2,2),
("SetDoorLocked",3,2,2,2),
("018C",2,2,2),
("Showclocksave",0),
("Hideclocksave",0),
("018F",1,2),
("0190",1,2),
("ChsPkmmenu",0),
("ChsPkmmenu2",0),
("StorePkmmenu2",1,2),
("0194",4, 2, 2, 2, 2),
("0195",2, 2, 2),
("Pokeinfo",1, 2),
("0197",1, 2),
("Storepkmnum",2,2,2),
("0199",2,2,2),
("CheckPartynum2",1,2),
("019B",2,2,2),
("019C",0),
("019D",1,2),
("019E",2,2,2),
("019F",1,2),
("01A0",0),
("01A1",0),
("01A2",0),
("01A3",1,2),
("01A4",2,2,2),
("01A5",0),
("01A6",0),
("01A7",0),
("01A8",0),
("01A9",0),
("01AA",2,2,2),
("01AB",2,2,2),
("EggAnm",0),
("01AD",0),
("01AE",2,2,2),
("01AF",3,2,2,2),
("01B0",1,2),
("01B1",1,2),
("01B2",1,2),
("Mailbox",0),
("01B4",1,2),
("Recordlist",1,2),
("01B6",1,2),
("01B7",2,2,2),
("01B8",2,2,2),
("Checkhappy",2,2,2),
("01BA",2,2,2),
("01BB",0),
("01BC",4,2,2,2,2),
("CheckPosition",1,2),
("01BE",1,2),
("01BF",1,2),
("CheckPkmnParty",2,2,2),
("CopyPkmnHeight",2,2,2),
("SetvarPkmnHeight",1,2),
("ComparePkmnHeight",3,2,2,2),
("CheckPkmnHeight",3,2,2,2),
("01C5",2,2,2),
("Moveinfo",1,2),
("Storemove",1,2),
("01C8",2,2,2),
("Deletemove",2,2,2),
("01CA",3,2,2,2),
("01CB",3,2,2,1),
("01CC",0),
("01CD",5,2,2,2,2,2),
("01CE",0),
("01CF",1),
("01D0",1,1),
("01D1",1,1),
("01D2",2,2,2),
("01D3",3,2,2,2),
("01D4",0),
("01D5",1,2),
("01D6",2,2,2),
("Berrypoffin",0),
("01D8",1, 2),
("Battlermresult",2,2,2),
("01DA",0),
("01DB",2,2,2),
("01DC",0),
("01DD",3,2,2,2),
("01DE",4,2,2,2,2),
("01DF",1,2),
("01E0",1,2),
("01E1",3,2,2,2),
("01E2",2,2,2),
("01E3",2,2,2),
("01E4",1,2),
("01E5",1,2),
("01E6",0),
("01E7",1, 2),
("CheckSinPkdx",1,2),
("CheckNatPkdx",1,2),
("ShowSinSheet",1,2),
("ShowNatSheet",1,2),
("01EC",0),
("01ED",1,2),
("01EE",0),
("01EF",0),
("01F0",0),
("CheckFossil",1,2),
("01F2",0),
("01F3",1,2),
("01F4",2,2,2),
("01F5",3,2,2,2),
("CheckPokeLevel",2,2,2),
("01F7",2,2,2),
("01F8",0),
("01F9",1,2),
("01FA",0),
("01FB",2, 2, 2),
("01FC",0),
("01FD",0),
("01FE",1,1),
("01FF",3,2,2,2),
("0200",1,2),
("0201",1, 2),
("0202",1,1),
("0203",5,2,2,2,2,2),
("Warplstelev",0),
("Geonet",0),
("Gmbynocule",0),
("0207",1,2),
("Pokepic",2,2,2),
("Hidepic",0),
("020A",1,2),
("020B",0),
("020C",0),
("020D",2,1,2),
("020E",0),
("020F",2, 2, 2),
("0210",2, 2, 2),
("0211",1, 1),
("0212",2,2,2),
("0213",2,2,2),
("0214",1,2),
("0215",0),
("0216",1,2),
("0217",2,2,2),
("0218",1,2),
("0219",0),
("021A",1,2),
("021B",0),
("021C",1,1),
("021D",1),
("021E",0),
("021F",2,2,2),
("0220",0),
("Remembermove",1,2),
("0222",0),
("0223",2,2,2),
("Teachmove",2,2,2),
("Checkteachmove",1,2),
("0226",1,1),
("0227",0),
("CheckPkmnTrade",1,2),
("TradeChosenPokemon",1,2),
("StopTrade",0),
("022B",0),
("022C",0),
("022D",2,1,2),
("022E",0),
("022F",1,2),
("0230",3,2,2,2),
("0231",2,2,2),
("0232",2,1,2),
("0233",2, 2, 2),
("0234",1,2),
("0235",1),
("0236",1, 2),
("0237",4, 2, 2, 2, 2),
("0238",2, 2, 2),
("Deciderules",1, 2),
("023A",3,2,2,2),
("HealpcAnm",1,2),
("023C",2,2,2),
("ShipAnm",4,2,2,2,2),
("023E",1),
("023F",0),
("0240",0),
("0241",0),
("0242",0),
("PhraseBox1W",3,2,2,2),
("PhraseBox2W",4,2,2,2,2),
("0245",2,2,2),
("0246",1,2),
("0247",1,2),
("0248",3,2,2,2),
("CheckPhraseBoxImput",5,2,2,2,2,2),
("024A",1,2),
("PrpPcAnm",1,1),
("PcOpnAnm",1,1),
("PcClsAnm",1,1),
("CheckLotoNumber",1,2),
("CompareLotoNumber",4,2,2,2,2),
("0250",2,2,2),
("0251",2,1,2),
("CheckBoxesNumber",1,2),
("0253",1,2),
("0254",1,2),
("0255",0),
("0256",2,2,2),
("SprtSave",0),
("RetSprtSave",3,2,2,2),
("ElevLgAnm",0),
("025A",1,2),
("025B",0),
("025C",0),
("025D",1,2),
("025E",0),
("025F",0),
("0260",1, 2),
("CheckAccessories",2,1,2),
("0262",0),
("0263",1,2),
("0264",1,2),
("0265",0),
("0266",0),
("Pokecasino",2,2,2),
("0268",1,2),
("0269",2,2,2),
("026A",3,2,2,2),
("026B",1,2),
("026C",1,2),
("Unownmsgbox",1,2),
("026E",1,2),
("026F",0),
("0270",2,1,2),
("Thanknameins",1,2),
("0272",1,1),
("0273",2,1,2),
("0274",1,2),
("0275",1,2),
("0276",3,2,2,2),
("0277",1,2),
("0278",2,2,2),
("0279",0),
("LgCstlView",0),
("027B",1,2),
("027C",2,2,2),
("027D",2,2,2),
("027E",1,2),
("027F",1,2),
("0280",4,1,2,1,1),
("0281",3,2,2,2),
("0282",1,2),
("0283",1,2),
("0284",1,2),
("0285",2,2,2),
("0286",1,2),
("0287",1,2),
("0288",1,2),
("0289",6,2,2,2,2,2,2),
("028A",1,2),
("028B",2,1,2),
("Pokepartypic",1,2),
("028D",0),
("028E",1, 2),
("CheckFirstTimeChampion",1,2),
("0290",0),
("0291",0),
("0292",2,1,2),
("0293",1,2),
("ShowBpntsbox",1,2),
("HideBpntsbox",0),
("0296",0),
("0297",0),
("0298",0),
("0299",1,2),
("029A",2,2,2),
("029B",4,2,2,2,2),
("029C",2,2,2),
("ChoiceMulti",2,2,2),
("HmEffect",2,2,2),
("CmrBmpEffect",1,2),
("DoubleBattle",3,2,2,2),
("Applymovement2",0),
("02A2",1,2),
("02A3",1,2),
("02A4",1,2),
("TrdchsPkmn",0),
("02A6",3,2,2,2),
("02A7",2,2,2),
("02A8",2,2,2),
("02A9",2,2,2),
("ComparePhraseBoxImput",5,2,2,2,2,2),
("02AB",1,2),
("ActMisteryGift",0),
("02AD",2,2,2),
("02AE",0),
("02AF",1,2),
("02B0",0),
("02B1",0),
("02B2",0),
("02B3",2,1,2),
("02B4",0),
("02B5",3,2,2,2),
("02B6",2,1,2),
("02B7",1,2),
("02B8",1,2),
("02B9",0),
("02BA",1,2),
("02BB",0),
("CheckWildBattle2",1,2),
("Wildbattle2",4,2,2,2,2),
("02BE",1,2),
("Bikeride",0),
("02C0",1,2),
("ShowSavebox",0),
("HideSavebox",0),
("02C3",0),
("02C4",1,1),
("02C5",2,2,2),
("SpinTradeUnion",0),
("CheckVersionGame",1,2),
("02C8",3, 2, 2, 2),
("02C9",1),
("FlrClckAnm",1),
("02CB",2,2,2),
("02CC",3,2,2,2),
("02CD",1),
("02CE",1, 1),
("02CF",2,2,2),
("02D0",3,2,2,2),
("02D1",1,2),
("02D2",3,2,2,2),
("02D3",3,2,2,2),
("02D4",3,2,2,2),
("02D5",1,2),
("02D6",0),
("02D7",1,2),
("02D8",1,1),
("02D9",3,2,2,2),
("02DA",3,2,2,2),
("02DB",3,2,2,2),
("02DC",1,2),
("02DD",2,2, 2),
("02DE",5,2,2,2,2,2),
("02DF",1,2),
("02E0",2,2,2),
("02E1",2,2,2),
("02E2",0),
("02E3",0),
("02E4",3, 2, 2, 2),
("02E5",3,2,2,2),
("02E6",3,2,2,2),
("02E7",2,2,2),
("02E8",1,2),
("02E9",3,2,2,2),
("02EA",2,2,2),
("02EB",1,2),
("02EC",0),
("02ED",0),
("02EE",4,2,2,2,2),
("02EF",0),
("02F0",0),
("02F1",0),
("02F2",0),
("02F3",2,1,2),
("02F4",4,2,2,2,2),
("02F5",4,2,2,2,1),
("02F6",3, 2, 2, 2),
("02F7",1,2),
("02F8",0),
("02F9",2,2,2),
("02FA",2,2,2),
("02FB",0),
("02FC",1,2),
("02FD",2,1,2),
("02FE",2,2,2),
("02FF",2,2,2),
("0300",0),
("0301",0),
("0302",5,2,2,2,2,2),
("0303",2,2,2),
("0304",4,2,2,2,2),
("0305",2,2,2),
("0306",2,2,2),
("0307",1,2),
("0308",0),
("0309",0),
("030A",1,2),
("030B",0),
("030C",0),
("030D",1,2),
("030E",1,2),
("030F",2,2,2),
("0310",0),
("0311",1,2),
("0312",1,2),
("0313",1,2),
("0314",1,2),
("0315",1,2),
("0316",3,2,2,2),
("0317",3,2,2,2),
("0318",2,2,2),
("0319",0),
("031A",0),
("031B",1,2),
("031C",2,2,2),
("031D",1, 2),
("031E",2,2,2),
("031F",0),
("0320",0),
("0321",1,2),
("0322",0),
("0323",1, 2),
("0324",4, 2, 2, 2, 2),
("0325",1,2),
("0326",1,2),
("0327",1,2),
("PortalEffect",1,2),
("0329",4,2,2,2,2),
("032A",1,2),
("032B",1,2),
("032C",4,2, 2, 2, 2),
("032D",0),
("032E",0),
("032F",2,2,2),
("0330",0), 
("0331",0),
("0332",0),
("0333",1,2),
("0334",0),
("0335",3,2,2,2),
("0336",1,2),
("0337",0),
("0338",0),
("0339",0),
("033A",1,1),
("033B",0),
("033C",2,1,2),
("033D",2,1,2),
("033E",2,1,2),
("033F",0),
("0340",0),
("0341",4,1,2,2,1),
("0342",1,1),
("0343",2,1,2),
("0344",2,1,2),
("0345",2,1,2),
("0346",1,1),
("DysplayFloor",1,2),
)

movCmd=(
    "Seeup", 
    "Seedown", 
    "Seeleft", 
    "Seeright", 
    "Walkupsl", 
    "Walkdownsl", 
    "Walkleftsl", 
    "Walkrightsl", 
    "Walkupnor", 
    "Walkdownnor", 
    "Walkleftnor", 
    "Walkrightnor", 
    "Walkupfst", 
    "Walkdownfst", 
    "Walkleftfst", 
    "Walkrightfst", 
    "Walkupvrfst", 
    "Walkdownvrfst", 
    "Walkleftvrfst", 
    "Walkrightvrfst", 
    "0014", 
    "0015", 
    "0016", 
    "0017", 
    "0018", 
    "0019", 
    "001A", 
    "001B", 
    "001C", 
    "001D", 
    "001E", 
    "001F",
    "0020", 
    "0021", 
    "0022", 
    "0023", 
    "0024", 
    "0025", 
    "0026", 
    "0027", 
    "0028", 
    "0029", 
    "002A", 
    "002B", 
    "002C", 
    "002D", 
    "002E", 
    "002F", 
    "0030", 
    "0031", 
    "0032", 
    "0033", 
    "0034", 
    "0035", 
    "0036", 
    "0037", 
    "0038", 
    "0039", 
    "003A", 
    "003B", 
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
    "004B", 
    "004C", 
    "004D", 
    "004E", 
    "004F", 
    "0050", 
    "0051", 
    "0052", 
    "0053", 
    "0054", 
    "0055", 
    "0056", 
    "0057", 
    "0058", 
    "0059", 
    "005A", 
    "005B", 
    "005C", 
    "005D", 
    "005E", 
    "005F", 
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
    "009F", 
       )
jumpcmds=(0x16, 0x1A, 0x1C, 0x1D,)
endcmds=(2, 0x1B)

#
#
#FULL CREDIT TO PICHU 2000 FOR BELOW
#
#
cmd_gs=(("Nop",0),
("Nop1",0),
("End",0),
("Return",2,2,2),
("0004",0),
("0005",0),
("0006",0),
("0007",0),
("0008",0),
("0009",0),
("000A",0),
("000B",0),
("000C",0),
("000D",0),
("000E",0),
("000F",0),
("0010",2,2,2),
("If",2,2,2),
("If2",2,2,2),
("0013",0),
("Callstd",2,1,1),
("0015",1,2),
("Jump",1,4),
("0017",0),
("0018",1,2),
("0019",2,2,2),
("Goto",2,2,2),
("Killscript",0),
("COMPARELASTRESULT" ,2,1,4),
("COMPARELASTRESULT1",3,1,2,2),
("Setflag",1,2),
("Clearflag",1,2),
("Checkflag",1,2),
("0021",1,2),
("0022",1,2),
("0023",2,2,2),
("0024",1,2),
("0025",1,2),
("0026",1,2),
("Copy",2,2,2),
("0028",2,2,2),
("Setvar",2,2,2),
("Copyvar",2,2,2),
("002B",2,2,2),
("002C",1,1),
("Message",1,1),
("Message2" ,1,2),
("002F",1,2),
("0030",0),
("0031",0),
("Waitbutton",0),
("0033",0),
("0034",0),
("Closemsgonkeypress",0),
("FreezeMsgbox",0),
("CallMsgbox",3,2,2,2),
("ColorMsgbox",2,2,1),
("TypeMsgBox",1,1),
("NoMapMsgBox",0),
("003B",2,1,2),
("003C",1,2),
("003D",0),
("003e",0),
("003F",1,2),
("Multi",5,1,1,1,1,2),
("Multi2",5,1,1,1,1,2),
("Txtscrpmulti",2,1,1),
("CloseMulti",0),
("Multi3",5,1,1,1,1,2),
("0045",3,2,2,2),
("0046",1,1),
("0047",0),
("Multirow",1,1),
("Fanfare",1,2),
("004A",1,2),
("004B",1,2),
("Cryfr",2,2,2),
("Waitcry",0),
("Soundfr",1,2),
("Fadedef",0),
("Playsound",1,2),
("Stop",1,2),
("Restart",0),
("0053",1,2),
("0054",2,2,2),
("0055",1,2),
("0056",0),
("0057",1, 2),
("0058",4, 1, 1, 1, 1),
("0059",1, 2),
("005A",2,2,2),
("005B",1,2),
("005C",0),
("005D",0),
("Applymovement",2,2,4),
("Waitmovement",0),
("Lockall",0),
("Releaseall",0),
("Lock",1,2),
("Release",1,2),
("Addpeople",1,2),
("Removepeople",1,2),
("Lockcam",2,2,2),
("0067",0),
("Faceplayer",0),
("CheckSpritePosition",2,2,2),
("006A",3,2,2,2),
("006B",3,2,2,2),
("Continuefollow(Changemap)",2,1,2),
("Followhero",2,2,2),
("Money",2,2,2),
("CheckMoney",2,2,2),
("TakeMoney",3,2,2,2),
("DisplayMoneyBox",2,2,2),
("HideMoneyBox",0),
("0073",0),
("0074",1,1),
("0075",0),
("0076",1,1),
("0077",1,2),
("0078",1,2),
("0079",1,2),
("007A",3,2,2,2),
("007B",0),
("007C",3,2,2,2),
("007D",3,2,2,2),
("TakeItem",3,2,2,2),
("GiveItem",3,2,2,2),
("CheckItem",3,2,2,2),
("0081",0),
("0082",2,2,2),
("0083",1,2),
("DoubleMessage",2,1,1),
("0085",2,2,2),
("0086",2,2,2),
("0087",3,2,2,2),
("0088",2,2,2),
("GivePokeStored",6,2,2,2,2,2,2),
("008A",2,2,2),
("008B",3,2,2,2),
("008C",3,2,2,2),
("008D",2,2,2),
("008E",2,2,2),
("008F",3,2,2,2),
("0090",1,2),
("0091",1,1),
("RecPkgrNumber",1,2),
("0093",2,2,2),
("0094",2,2,2),
("0095",1,1),
("Callend",0),
("0097",0),
("OpenWi-fi",0),
("0099",3,2, 2, 2),
("OpenPokeDress",3,2,2,2),
("009B",2,2,2),
("009C",0),
("OpenPkgrMap",0),
("009E",1,1),
("009F",0),
("00A0",0),
("Callend",0),
("00A2",0),
("EndGame",1,2),
("00A4",4,2,2,2,2),
("00A5",2,2,2),
("Wfc",1,2),
("00A7",2,2,2),
("00A8",1,2),
("00A9",2,2,2),
("00AA",1,2),
("00AB",2,2,2),
("00AC",0),
("GivePokeNick",2,2,2),
("Fadescreen",4,2,2,2,2),
("Resetscreen",0),
("Warp",5,2,2,2,2,2),
("HallFameData",0),
("00B2",4,2,2,2,2),
("Wfc",1,2),
("00B4",0),
("00B5",0),
("00B6",1, 2),
("00B7",2, 2, 2),
("00B8",1, 2),
("00B9",1,1),
("00BA",1,1),
("00BB",1,2),
("00BC",1,2),
("00BD",0),
("SetvarHero",1,1),
("SetvarRival",1,1),
("SetvarAlter",1,1),
("SetvarPoke",2,1,2),
("SetvarItem",2,1,2),
("00C3",2,1,2),
("SetvarAtkitem",2,1,2),
("SetvarAtk",2,1,2),
("SetvarNum",2,1,2),
("SetvarPokenick",2,1,2),
("SetvarObj",2,1,2),
("00C9",1,1),
("SetvarPokeStored",4,1,2,2,1),
("00CB",1,2),
("00CC",0),
("CheckStarter",1,1),
("00CE",1,2),
("00CF",1,1),
("00D0",2,1,2),
("00D1",2,1,2),
("00D2",2, 1, 2),     
("00D3",2,1,2),
("00D4",1,2),
("TrainerBattle",3,2,2,2),
("00D6",2,2,2),
("00D7",3,2,2,2),
("00D8",3,2,2,2),
("00D9",1,2),
("00DA",1,2),
("LostGoPc",0),
("CheckLost",1,2),
("00DD",4,2,2,2,2),
("StoreStarter",1,2),
("00DF",2,1,2),
("00E0",2,1,2),
("00E1",2,1,2),
("00E2",4,2,2,2,2),
("00E3",4,2,2,2,2),
("00E4",1,2),
("00E5",2,2,2),
("00E6",0),
("00E7",3,2,2,2),
("00E8",3,2,2,2),
("00E9",1,2),
("00EA",1,2),
("00EB",0),
("00EC",5,2,2,2,2,2),
("00ED",1,2),
("00EE",4,2,2,2,2),
("CheckPokeGender",2,2,2),
("WarpLift",5,2,2,2,2,2),
("CheckFloor",1,2),
("00F2",0),
("WireBattleWait",4,2,2,2,2),
("00F4",0),
("00F5",0),
("00F6",0),
("Pokecontest",0),
("00F8",1,2),
("00F9",0),
("00FA",0),
("00FB",1,2),
("00FC",0),
("00FD",1,2),
("00FE",1,2),
("00FF",2,2,2),
("0100",1,2),
("0101",1,2),
("0102",2,2,2),
("0103",2,1,1),
("0104",1,2),
("0105",1,2),
("0106",0),
("0107",0),
("0108",1,2),
("0109",0),
("010A",0),
("010B",2,2,2),
("010C",1, 2),
("010D",4,2,2,2,2),
("010E",1,2),
("010F",2,2,2),
("0110",1,2),
("0111",1,2),
("0112",2,2,2),
("0113",2,2,2),
("0114",2,2,2),
("0115",2,2,2),
("0116",4,2,2,2,2),
("0117",0),
("0118",0),
("CheckGender",1,2),
("HealPkmn",0),
("011B",0),
("011C",0),
("011D",2,2,2),
("011E",1,2),
("011F",2,2,2),
("0120",2,2,2),
("0121",1, 2),
("0122",2,2,2),
("ActPokedex",0),
("0124",0),
("GiveRShoes",0),
("Checkbadge",2,2,2),
("Setbdgtrue",1,2),
("Setbdgfalse",1,2),
("0129",0),
("012A",4,2,2,2,2),
("012B",0),
("012C",1,2),
("012D",1,2),
("012E",2,2,2),
("012F",2,2,2),
("0130",1,2),
("0131",0),
("0132",4,2,2,2,2),
("PrpDoorMovement",5,2,2,2,2,1),
("CloseDoor",1,1),
("MoveDoor",1,1),
("OpenDoor",1,1),
("WaitDoor",1,1),
("0138",0),
("0139",4,2,2,2,2),
("013A",0),
("013B",0),
("013C",0),
("013D",1,1),
("013E",0),
("013F",1,2),
("0140",1,2),
("LtSurgeGymAnm",1,2),
("CheckLtSurgeGymBin",2,1,2),
("0143",2,2,2),
("0144",1,2),
("0145",2,2,2),
("0146",2,2,2),
("0147",2,1,2),
("0148",2,1,2),
("0149",0),
("014A",0),
("014B",1,2),
("CheckPartyNumber",1,2),
("014D",1,2),
("014E",0),
("014F",0),
("0150",0),
("0151",0),
("0152",3,2,2,2),
("SetOverwordPosition",5,2,2,2,2,2),
("0154",2,2,2),
("0155",2,2,2),
("0156",3,2,2,2),
("0157",0),
("0158",2,2,2),
("0159",0),
("015A",0),
("015B",2,2,2),
("015C",1,2),
("ChsPokemenu",0),
("ChsPokemenu2",0),
("StorePokemenu",1,2),
("0160",3,1,2,2),
("0161",2,1,2),
("StorePkmnNum",2,2,2),
("CheckIfPokeTraded",2,2,2),
("0164",1,2),
("0165",2,2,2),
("0166",1,2),
("0167",1,2),
("0168",1,2),
("0169",2,2,2),
("016A",1,2),
("016B",3,1,2,2),
("016C",1,2),
("016D",0),
("016E",0),
("016F",2,2,2),
("CheckHiroMoneyNumber",2,2,2),
("0171",0),
("0172",0),
("0173",2,2,2),
("0174",2,2,2),
("0175",1,2),
("0176",1,2),
("0177",1,2),
("OpenMail",0),
("CheckMail",1, 2),
("017A",2,2,2),
("017B",1,2),
("017C",2,2,2),
("017D",1, 2),
("017E",2,2,2),
("017F",2,2,2),
("0180",1,1),
("0181",2,2,2),
("0182",1,2),
("0183",1,2),
("0184",1,2),
("0185",1,2),
("0186",2,2,2),
("0187",5,2,2,2,2,2),
("0188",3,2,2,2),
("0189",2,2,2),
("ChoosePokeDelete",1,2),
("StoreMoveDelete",1,2),
("CheckMoveNumber",2,2,2),
("DeleteMove",2,2,2),
("018E",3,2,2,2),
("SetVarMoveDelete",3,1,2,2),
("0190",1,1),
("0191",0),
("0192",0),
("0193",2,2,2),
("GiveItemStored",3,2,2,2),
("0195",2, 2, 2),
("0196",1, 2),
("0197",2,2,2),
("0198",2,2,2),
("0199",0),
("019A",2,2,2),
("019B",0),
("019C",3,2,2,2),
("019D",4,2,2,2,2),
("019E",1,2),
("019F",1,2),
("01A0",3,2,2,2),
("01A1",2,2,2),
("01A2",2,2,2),
("01A3",3,2,2,2),
("01A4",1,2),
("01A5",0),
("01A6",0),
("01A7",1,2),
("01A8",1,2),
("01A9",1,2),
("01AA",3,1,2,2),
("01AB",2,2,2),
("01AC",1,2),
("01AD",1,2),
("01AE",3,2,2,2),
("01AF",3,2,2,2),
("01B0",2,2,2),
("01B1",3,2,2,2),
("01B2",2,2,2),
("01B3",2,2,2),
("01B4",0),
("01B5",1,2),
("01B6",2,2,2),
("01B7",2,2,2),
("01B8",2,2,2),
("01B9",2,2,2),
("01BA",2,2,2),
("01BB",0),
("01BC",2,2,2),
("01BD",1,2),
("01BE",1,2),
("01BF",1,2),
("01C0",5,2,2,2,2,2),
("01C1",2,2,2),
("01C2",1,2),
("01C3",1,2),
("01C4",2,2,2),
("01C5",0),
("01C6",0),
("01C7",1,2),
("01C8",2,2,2),
("01C9",2,2,2),
("01CA",3,2,2,2),
("01CB",0),
("01CC",2,2,2),
("01CD",3,1,2,2),
("01CE",1,2),
("01CF",0),
("01D0",1,1),
("01D1",1),
("01D2",2,2,2),
("ChoosePokeRem",1,2),
("01D4",2,2,2),
("StoreMoveRem",1,2),
("01D6",1,1),
("01D7",0),
("CheckPokeTrade",1,2),
("TradeChsPoke",1,2),
("StopTrade",0),
("01DB",2,2,2),
("01DC",0),
("01DD",2,1,2),
("01DE",4,2,2,2,2),
("01DF",4,2,2,2,2),
("CheckRibbon",3,2,2,2),
("GiveRibbon",3,2,2,2),
("01E2",2,2,2),
("CheckPokeRibbon",2,2),
("01E4",1,2),
("01E5",1,2),
("RBattleRecorder",0),
("01E7",1,2),
("01E8",2,2,2),
("01E9",1),
("01EA",1,2),#A
("01EB",1,2),
("01EC",3,2,2,2),
("01ED",3,2,2,2),
("01EE",2,2,2),
("CheckVersion",1,2),
("01F0",0),
("01F1",3,2,2,2),
("01F2",5,2,2,2,2,2),
("01F3",5,2,2,2,2,2),
("01F4",1,1),
("01F5",1,1),
("01F6",2,2,2),
("01F7",1,2),
("01F8",4,2,2,2,2),
("01F9",1,2),
("01FA",2,1,2),
("CheckBoxsNumber",1,2),
("01FC",1,2),
("01FD",1,2),
("01FE",0),
("StoreFriendParkResult",2,2,2),
("0200",1,2),
("0201",3,2,2,2),
("0202",1,2),
("0203",1,2),
("0204",2,1,2),
("0205",0),
("0206",1,2),
("0207",1,2),
("0208",1,2),
("0209",0),
("020A",1,2),
("020B",1,2),
("020C",0),
("020D",2,1,2),
("020E",0),
("020F",2, 2, 2),
("0210",1,2),
("0211",1,2),
("0212",2,1,2),
("0213",2,1,2),
("0214",3,2,2,2),
("0215",3,2,2,2),
("0216",1,2),
("0217",2,2,2),
("0218",1,2),
("0219",0),
("021A",2,2,2),
("021B",0),
("021C",1,2),
("021D",1,2),
("021E",0),
("021F",2,2,2),
("0220",0),
("0221",1,2),
("0222",2,1,2),
("0223",1,2),
("0224",2,2,2),
("0225",1,2),
("0226",1,1),
("0227",1,2),
("0228",2,2,2),
("0229",2,1,2),
("022A",0),
("022B",1,2),
("022C",1,2),
("022D",2,2,2),
("022E",2,2,2),
("022F",1,2),
("0230",3,2,2,2),
("0231",4,2,2,2,2),
("0232",0),
("0233",2, 2, 2),
("0234",2,2,2),
("0235",1),
("ChsPokeMenuTrade",0),
("0237",4, 2, 2, 2, 2),
("0238",2, 2, 2),
("0239",1, 2),
("023A",3,2,2,2),
("023B",1,2),
("023C",1,2),
("023D",0),
("023E",2,2,2),
("023F",0),
("0240",1,2),
("0241",0),
("0242",0),
("0243",0),
("0244",3,2,2,1),
("0245",2,2,2),
("0246",0),
("0247",1,2),
("0248",1,2),
("0249",0),
("024A",1,2),
("024B",1,2),
("024C",1,2),
("LegendBattle",3,2,1,2),
("024E",1,2),
("024F",4,2,2,2,2),
("0250",1,2),
("0251",0),
("0252",1,2),
("0253",1,2),
("0254",1,2),
("0255",0),
("0256",2,2,2),
("0257",0),
("StartFriendPark",0),
("0259",0),
("025A",1,2),
("025B",0),
("025C",1,2),
("025D",1,2),
("EndFriendPark",0),
("025F",0),
("0260",3,2,2,2),
("MecScript",0),
("0262",0),
("0263",1,2),
("0264",1,2),
("0265",1,2),
("0266",1,2),
("MakePhoto",2,2,2),
("0268",1,2),
("0269",2,2,2),
("CheckAlbumPhoto",1,2),
("026B",1,2),
("026C",1,1),
("026D",1,2),
("026E",2,2,2),
("026F",1,2),
("0270",1,2),
("0271",3,2,2,2),
("0272",2,1,2),
("0273",1,1),
("0274",2,2,2),
("0275",1,2),
("0276",3,2,2,2),
("0277",3,2,2,2),
("0278",2,2,2),
("0279",3,2,2,2),
("027A",2,2,2),
("027B",2,2,2),
("027C",1,2),
("027D",3,2,2,2),
("027E",3,2,2,2),
("027F",3,2,2,2),
("0280",1,1),
("0281",3,2,2,2),
("0282",3,2,2,2),
("0283",3,2,2,2),
("0284",3,2,2,2),
("0285",3,2,2,2),
("0286",1,2),
("0287",1,2),
("0288",1,2),
("0289",0),
("028A",1,2),
("028B",3,2,2,2),
("028C",3,2,2,2),
("028D",4,2,2,2,2),
("028E",3,2,2,2),
("028F",2,2,2),
("0290",2,2,2),
("0291",4,2,2,2,2),
("0292",2,1,2),
("0293",1,2),
("0294",1,2),
("0295",0),
("0296",3,2,2,2),
("0297",0),
("0298",0),
("0299",1,2),
("029A",2,2,2),
("029B",4,2,2,2,2),
("029C",2,1,2),
("029D",2,2,2),
("029E",2,2,2),
("029F",0),
("02A0",3,2,2,2),
("02A1",5,2,2,2,2,2),
("02A2",2,2,2),
("02A3",4,2,2,2,2),
("02A4",2,2,2),
("02A5",0),
("02A6",3,2,2,2),
("02A7",2,2,2),
("02A8",2,2,2),
("02A9",1,2),
("02AA",1,2),
("02AB",1,2),
("02ACS",0),
("02AD",2,2,2),
("02AE",0),
("02AF",1,2),
("02B0",1,2),
("02B1",1,2),
("02B2",2,2,2),
("02B3",1,2),
("02B4",0),
("02B5",1,2),
("02B6",1,2),
("02B7",1,2),
("02B8",1,2),
("02B9",0),
("02BA",3,1,2,2),
("02BB",0),
("CheckWildBattle2",1,2),
("Wildbattle2",4,2,2,2,2),
("02BE",0),
("02BF",0),
("02C0",1,2),
("02C1",0),
("02C2",1,2),
("02C3",2,2,2),
("02C4",1,2),
("02C5",0),
("02C6",0),
("02C7",1,2),
("02C8",1,1),
("02C9",1,1),
("02CA",1,1),
("02CB",0),
("02CC",0),
("02CD",1,2),
("02CE",2,1,2),
("02CF",2,2,2),
("02D0",1,2),
("02D1",1,2),
("02D2",3,2,2,2),
("02D3",3,2,2,2),
("02D4",2,2,2),
("02D5",2,1,2),
("02D6",0),
("02D7",1,2),
("02D8",1,1),
("02D9",1,2),
("02DA",3,2,2,2),
("02DB",3,2,2,2),
("02DC",1,2),
("02DD",2,1,2),
("02DE",1,1),
("02DF",1,2),
("02E0",0),
("02E1",1,2),
("02E2",1,2),
("02E3",0),
("02E4",3, 2, 2, 2),
("02E5",4,2,2,2,2),
("02E6",3,2,2,2),
("02E7",1,2),
("02E8",0),
("02E9",3,2,2,2),
("OpenLowScreen",0),
("CloseLowScreen",0),
("OpenLowYesNoBox",1,2),
("Multi4",5,1,1,1,1,2),
("Multi5",5,1,1,1,1,2),
("Txtscrpmulti4",3,2,2,2),
("CloseMulti4",0),
("02F1",0),
("02F2",0),
("02F3",0),
("02F4",0),
("02F5",2,2,2),
("02F6",3, 2, 2, 2),
("02F7",1,2),
("02F8",0),
("02F9",1,2),
("02FA",1,2),
("02FB",0),
("02FC",0),
("02FD",0),
("02FE",2,2,2),
("02FF",2,2,2),
("0300",3,1,2,2),
("0301",1,1),
("0302",1,2),
("0303",0),
("0304",4,2,2,2,2),
("0305",1,2),
("0306",2,2,2),
("0307",2,2,2),
("0308",0),
("0309",2,2,2),
("030A",1,2),
("030B",2,2,2),
("030C",1,2),
("030D",1,2),
("030E",1,2),
("030F",1,1),
("0310",1,2),
("0311",1,2),
("0312",1,1),
("0313",3,2,2,2),
("0314",1,2),
("0315",1,1),
("0316",2,2,2),
("0317",3,2,2,2),
("0318",2,2,2),
("TakeMomMoney",2,2,2),
("GiveMomMoney",3,2,2,2),
("OpenMomMoneyBox",2,2,2),
("CloseMomMoneyBox",0),
("031D",1,2),
("031E",1,2),
("031F",1,2),
("0320",1,2),
("0321",1,2),
("0322",0),
("0323",2,2,2),
("0324",1,1),
("0325",0),
("0326",0),
("0327",2,2,2),
("0328",1,2),
("0329",1,2),
("032A",0),
("032B",1,2),
("032C",4,2, 2, 2, 2),
("032D",1,2),
("032E",0),
("032F",1,2),
("0330",0), 
("0331",1,1),
("0332",0),
("0333",1,2),
("0334",1,1),
("0335",2,2,2),
("0336",1,2),
("0337",1,2),
("0338",1,2),
("0339",2,2,2),
("033A",1,2),
("033B",2,2,2),
("033C",3,2,2,1),
("033D",2,1,2),
("033E",1,2),
("033F",1,2),
("0340",1,2),
("0341",1,2),
("0342",1,2),
("0343",1,2),
("0344",1,2),
("0345",1,2),
("CheckMonMoneyNumber",2,2,2),
("0347",1,2),
("0348",2,2,2),     
("0349",0),
("034A",1,1),
("034B",2,2,2),
("034C",2,1,2),
("034D",2,1,2),
("034E",1,2),
("034F",1,2),
("0350",1,2),
("0351",1,2),
("0352",1,2),
("0353",1,2),
("0354",2,1,2),
("0355",2,1,2),
("0356",1,1),
("0357",1,2),
)

movCmd_gs=(
    "Seeup", 
    "Seedown", 
    "Seeleft", 
    "Seeright", 
    "Walkupsl", 
    "Walkdownsl", 
    "Walkleftsl", 
    "Walkrightsl", 
    "Walkupnor", 
    "Walkdownnor", 
    "Walkleftnor", 
    "Walkrightnor", 
    "Walkupfst", 
    "Walkdownfst", 
    "Walkleftfst", 
    "Walkrightfst", 
    "Walkupvrfst", 
    "Walkdownvrfst", 
    "Walkleftvrfst", 
    "Walkrightvrfst", 
    "0014", 
    "0015", 
    "0016", 
    "0017", 
    "0018", 
    "0019", 
    "001A", 
    "001B", 
    "001C", 
    "001D", 
    "001E", 
    "001F",
    "0020", 
    "0021", 
    "0022", 
    "0023", 
    "0024", 
    "0025", 
    "0026", 
    "0027", 
    "0028", 
    "0029", 
    "002A", 
    "002B", 
    "002C", 
    "002D", 
    "002E", 
    "002F", 
    "0030", 
    "0031", 
    "0032", 
    "0033", 
    "0034", 
    "0035", 
    "0036", 
    "0037", 
    "0038", 
    "0039", 
    "003A", 
    "003B", 
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
    "004B", 
    "004C", 
    "004D", 
    "004E", 
    "004F", 
    "0050", 
    "0051", 
    "0052", 
    "0053", 
    "0054", 
    "0055", 
    "0056", 
    "0057", 
    "0058", 
    "0059", 
    "005A", 
    "005B", 
    "005C", 
    "005D", 
    "005E", 
    "005F", 
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
    "009F", 
       )
jumpcmds_gs=(0x16, 0x1A, 0x1C, 0x1D,)
endcmds_gs=(2, 0x1B)
