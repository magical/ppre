# -*- coding: latin-1 -*-
import unicodeparser
import array

errorReport = False
depends = False

def allowErrors():
    errorReport = True
    if not depends:
        import romerror
def ToCode(text,sErrors=False,compressed=False):
    if sErrors:
        errorReport = True
        if not depends:
            import romerror
    data = []
    while len(text)!=0:
        #
        i=0
        if text[0:1]==u"\\":
            #print "is escape %c" %text[1:2]
            if text[1:2]=='x':
                #print "read as raw hex"
                data.append(int(text[2:6], 16))
                text = text[6:len(text)]
            elif text[1:2] == 'v':
                #print "VarPrint"
                data.append(0xfffe)
                data.append(int(text[2:6], 16))
                text = text[6:len(text)]
            elif text[1:2] == 'z':
                var = []
                w = 0
                while len(text)!=0:
                    if text[1:2] == 'z':
                        w += 1
                        var.append(int(text[2:6], 16))
                        text = text[6:len(text)]#\z0000
                    else:
                        break
                data.append(w)
                data.extend(var)
            elif text[1:2]=='n':
                data.append(0xe000)
                text = text[2:len(text)]
            elif text[1:2]=='r':
                data.append(0x25BC)
                text = text[2:len(text)]
            elif text[1:2]=='f':
                data.append(0x25BD)
                text = text[2:len(text)]
            else:
                if errorReport:
                    romerror.unknownEscape(text[1:2])
                print "unknown escape: %s" % text[1:2]
                text = text[2:len(text)]
        else:
            while not(unicodeparser.d.has_key(text[0:6-i]) | (i==6)):
                i=i+1
            if i==6:
                if errorReport:
                    romerror.charNotFound(text[0:1])
                print "Char not found %s(%i)" % (text[0:1],ord(text[0:1]))
                text = text[6-i+1:len(text)]
            else:
                data.append(unicodeparser.d[text[0:6-i]])
                text = text[6-i:len(text)]
    if compressed:
        data.append(0x1FF)
        bits=[]
        for i in range(0,len(data)):
            for j in range(0,9):
                bits.append((data[i]>>j)&1)
        tmp_uint16=0
        data=[]
        data.append(0xF100)
        for i in range(0,len(bits)):
            if i%15==0 and i!=0:
                data.append(tmp_uint16)
                tmp_uint16=0
            tmp_uint16|=(bits[i]<<(i%15))
        data.append(tmp_uint16)
    data.append(0xffff)
    a = array.array('H', data)
    return data

def Makefile(textarr,sError=False,compressed=False):
    base = len(textarr)*8 + 4
    ptrtable = []
    rawdata = []
    for i in range(len(textarr)):
        data = ToCode(textarr[i],sError,compressed)
        l=len(data)
        ptrtable.extend([base, l])
        rawdata.extend(data)
        base += l*2

    hdr = [len(textarr), 0]

    #ptrtable.append(array.array('H', rawdata))
    return array.array('H',hdr).tostring() + array.array('I', ptrtable).tostring() +array.array('H', rawdata).tostring()


#xml = pokexml.XMLReader("MyXML.xml")
#xml.ParseptextXML()

#p=Makefile(xml.strings[0][1])




#f = open("out.bin", "wb")
#f.write(p)

#f.close()
#a = ToCode(u"\\v0101\\x0001\\x0000 used\\xE000Pound!")



#f.write(a.tostring())
#f.close()


