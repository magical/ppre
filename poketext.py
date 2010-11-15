# -*- coding: latin-1 -*- 
import array
import unicodeparser

class BinaryData16:
    def __init__(self, string):
        self.s = array.array('H',string)
    def read16(self, ofs):
        return self.s[ofs>>1]
    
    def write16(self, d,ofs):
        self.s[ofs>>1]=d      

    def read32(self, ofs):
        return self.s[ofs>>1] | (self.s[(ofs>>1)+1]<<16)

    def write32(self, d, ofs):
        self.s[ofs>>1]=(d&0xffff)
        self.s[(ofs>>1)+1]=((d>>16)&0xffff)
    def getStr(self):
        return self.s.tostring()


class BinaryData:
    def __init__(self, string):
        self.s = array.array('c',string)
    def read16(self, ofs):
        return ord(self.s[ofs]) | (ord(self.s[ofs+1])<<8)
    
    def write16(self, d,ofs):
        self.s[ofs]=chr(d&0xff)
        self.s[ofs+1]=chr((d>>8)&0xff)        

    def read32(self, ofs):
        return ord(self.s[ofs]) | (ord(self.s[ofs+1])<<8) | (ord(self.s[ofs+2])<<16) | (ord(self.s[ofs+3])<<24)

    def write32(self, d, ofs):
        self.s[ofs]=chr(d&0xff)
        self.s[ofs+1]=chr((d>>8)&0xff)
        self.s[ofs+2]=chr((d>>16)&0xff)
        self.s[ofs+3]=chr((d>>24)&0xff)
    def getStr(self):
        return self.s.tostring()
        
        

class PokeTextData(BinaryData16): #16 = mayor speed improvement
    def decrypt(self):
        self.DecyptPtrs(self.read16(0), self.read16(2), 4)
        self.ptrlist = self.CreatePtrList(self.read16(0), 4)

        self.strlist = []

        for i in range(self.read16(0)):
            ptr, chars = self.ptrlist[i]    
            self.DecyptTxt(chars, i+1, ptr)
            self.strlist.append(self.MakeString(chars, ptr))
    
    def encrypt(self):
        
        self.ptrlist = self.CreatePtrList(self.read16(0), 4)

        for i in range(self.read16(0)):
            ptr, chars = self.ptrlist[i]    
            self.DecyptTxt(chars, i+1, ptr)            

        self.DecyptPtrs(self.read16(0), self.read16(2), 4)
        
    def DecyptPtrs(self, count, key, sdidx):
        key = (key * 0x2FD) &0xffff

        for i in range(count):
            key2 = (key*(i+1)&0xffff)
            realkey = key2 | (key2<<16)
            self.write32(self.read32(sdidx)^realkey, sdidx)       
            self.write32(self.read32(sdidx+4)^realkey, sdidx+4)
            sdidx+=8
        

    def CreatePtrList(self, count, sdidx):
        ptrlist = []
        for i in range(count):
            ptrlist.extend([[self.read32(sdidx), self.read32(sdidx+4)]])
            sdidx+=8
        return ptrlist
        

        
    def DecyptTxt(self, count, id, idx):
        key = (0x91BD3*id)&0xffff

        for i in range(count):
            self.write16(self.read16(idx)^key, idx)
            key +=0x493D
            key&=0xffff
            idx+=2

    def MakeString(self, count, idx):
        string = ""
        chars=[]
        uncomp=[]
        for i in range(0, count):
            chars.append(self.read16(idx))        
            idx+=2
        if chars[0] ==0xF100:
            j=1
            shift1 = 0
            trans = 0
            while 1:
                tmp = chars[j]
                tmp = tmp >> shift1
                tmp1 = tmp
                if shift1 >= 0xf:
                    shift1 -= 0xf
                    if shift1 > 0:
                        tmp1 = (trans | ((chars[j]<< (9-shift1)) & 0x1FF))
                        if tmp1 == 0x1ff:
                            break
                        #string += unicodeparser.tb[tmp1]
                        uncomp.append(tmp1)
                else:
                    tmp1 = ((chars[j] >> shift1) & 0x1FF)
                    if tmp1 == 0x1ff:
                        break
                    #string += unicodeparser.tb[tmp1]
                    uncomp.append(tmp1)
                    shift1 += 9
                    if shift1 < 0xf:
                        trans = ((chars[j] >> shift1) & 0x1FF)
                        shift1 += 9
                    j+=1
            chars=uncomp
        i = 0
        #constructs \v0000\z0000\z0000 <-- auto sets second Char
        for c in range(0, len(chars)):
            try:
                string = string + unicodeparser.tb[chars[i]]
            except:
                if chars[i]==0xfffe:
                    i+=1
                    string = string + "\\v" + "%04X"%chars[i]
                    i+=1
                    total = chars[i]
                    for z in range(0,total):
                        i+=1
                        string = string + "\\z" + "%04X"%chars[i]
                elif chars[i]==0xffff:
                    break                    
                else:
                    string = string + "\\x" + "%04X"%chars[i]
            i+=1
        return string
    
    def SetKey(self, key):
        self.write16(key,2)
