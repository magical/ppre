class byteReader():
    def __init__(self,rawdata):
        self.a = rawdata
        self.i=0
    def ReadByte(self):
        ret = self.a[self.i]
        self.i+=1
        return ret
    def Read(self, length):	
        ret = self.a[self.i:self.i+length]
        """for j in range(0, length):
            ret.append(0x00)
            ret[j] =  self.a[self.i+j]<<(j*8)"""
        self.i += length
        return ret
    def ReadUInt16(self):	
        ret =  (self.a[self.i]|(self.a[self.i+1]<<8))
        self.i+=2
        return ret
    def ReadInt16(self):
        temp=(self.a[self.i]|(self.a[self.i+1]<<8))
        if temp>>15==1:
            temp=temp-0x10000
        ret = temp
        self.i+=2
        return ret
    def ReadUInt32(self):	
        ret =  (self.a[self.i]|(self.a[self.i+1]*1<<8)|(self.a[self.i+2]*1<<16)|(self.a[self.i+3]*1<<24))
        self.i+=4
        return ret
    def ReadInt32(self):
        temp=(self.a[self.i]|(self.a[self.i+1]<<8)|(self.a[self.i+2]<<16)|(self.a[self.i+3]<<24))
        if temp>>31==1:
            temp=temp-0x100000000
        ret = temp
        self.i+=4
        return ret
    def ReadChars(self, length):
        lret = []
        for j in range(0,length):
            lret.append(chr(self.a[self.i+j]*1))
        cret = ""
        for k in range(0, len(lret)):
            cret += lret[k]
        #ret = self.a[self.i:self.i+length]
        self.i+=length
        #print cret
        return cret
    def Accel(self,c):
        self.i+=c
    def Reverse(self,c):
        self.i-=c
    def Seek(self,d):
        self.i=d
    def Position(self):
        return self.i
    """def WriteByte(self, val):
        self.a[self.i]=val&0xFF
        self.i+=1
    def WriteUInt16(self, val):	
        self.a[self.i]=val&0xFF
        self.a[self.i+1]=(val>>8)&0xFF
        self.i+=2
    def WriteUInt32(self, val):	
        self.a[self.i]=val&0xFF
        self.a[self.i+1]=(val>>8)&0xFF
        self.a[self.i+2]=(val>>16)&0xFF
        self.a[self.i+3]=(val>>24)&0xFF
        self.i+=4
    def WriteInt32(self, val):
        if val<0:
            val+=0x100000000
        self.a[self.i]=val&0xFF
        self.a[self.i+1]=(val>>8)&0xFF
        self.a[self.i+2]=(val>>16)&0xFF
        self.a[self.i+3]=(val>>24)&0xFF
        self.i+=4"""
class byteWriter():
    def __init__(self):
        self.a = []
    def WriteByte(self, val):
        self.a.append(val&0xFF)
    def WriteUInt16(self, val):	
        self.a.append(val&0xFF)
        self.a.append((val>>8)&0xFF)
    def WriteUInt32(self, val):	
        self.a.append(val&0xFF)
        self.a.append((val>>8)&0xFF)
        self.a.append((val>>16)&0xFF)
        self.a.append((val>>24)&0xFF)
    def WriteInt32(self, val):
        if val<0:
            val+=0x100000000
        self.a.append(val&0xFF)
        self.a.append((val>>8)&0xFF)
        self.a.append((val>>16)&0xFF)
        self.a.append((val>>24)&0xFF)
    def WriteChars(self,chars,length):
        for c in range(0,length):
            if c >= len(chars):
                self.a.append(ord(0x0))
            else:
                self.a.append(ord(chars[c])&0xFF)
    def WriteByteAt(self,val,pos):
        self.a[pos] = val
    def WriteUInt16At(self,val,pos):
        self.a[pos] = val&0xff
        self.a[pos+1] = (val>>8)&0xff
    def WriteUInt32At(self,val,pos):
        self.a[pos] = val&0xff
        self.a[pos+1] = (val>>8)&0xff
        self.a[pos+2] = (val>>16)&0xFF
        self.a[pos+3] = (val>>24)&0xFF
    def Write(self,data):
        self.a.extend(data)
    def Position(self):
        return len(self.a)
    def ReturnData(self):
        return self.a
