import narc
import execute
import poketext
import pokexml
import texttopoke
import cProfile



def ReadMsgNarc():
	filename=rom.getFolder()+"/header.bin"
	f=open(filename,"rb")
	f.seek(9)
	id=f.read(1)
	if(id=='L'):
		filename = rom.getFolder()+"/root/msgdata/pl_msg.narc"
	elif id in ('G','S'):
		filename = rom.getFolder()+"/root/a/0/2/7"
	else:
		filename = rom.getFolder()+"/root/msgdata/msg.narc"
	f.close()
	f = open(filename, "rb")
	d = f.read()
	f.close()
	return narc.NARC(d)

def WriteMsgNarc(archive):
	filename=rom.getFolder()+"/header.bin"
	f=open(filename,"rb")
	f.seek(9)
	id=f.read(1)
	if(id=='L'):
		filename = rom.getFolder()+"/root/msgdata/pl_msg.narc"
	elif id in ('G','S'):
		filename = rom.getFolder()+"/root/a/0/2/7"
	else:
		filename = rom.getFolder()+"/root/msgdata/msg.narc"
	f.close()
	f = open(filename, "wb")
	archive.ToFile(f)
	f.close()

def GetText(index, xmlname):
    archive = ReadMsgNarc()
    xmlout = pokexml.XMLWriter(xmlname)
    binary = poketext.PokeTextData(archive.gmif.files[index])
    binary.decrypt()
    xmlout.addStrings(binary.strlist, index)
    xmlout.writeFile()   

    #print binary.strlist[0]   



def GetTextAll(xmlname):
    archive = ReadMsgNarc()
    xmlout = pokexml.XMLWriter(xmlname)
    print "| = = = = = = = = = = = = = = = = = = = = | 100%"
    print "|",
    cur = 0
    
    # PokeTEXT code    
    for i in range(len(archive.gmif.files)):        
        binary = poketext.PokeTextData(archive.gmif.files[i])
        binary.decrypt()     
        xmlout.addStrings(binary.strlist, i)

        if (i*20)/623 > cur:
            print "=",
            cur+=1
    print "| Done!"
        
    xmlout.writeFile()



# rewrite code begin
def Rewrite(xmlname):
    xmlr = pokexml.XMLReader(xmlname)
    xmlr.ParseptextXML()


    archive = ReadMsgNarc()

    print xmlr.filelist

    for fileid in xmlr.filelist:
        print fileid
        binary = poketext.PokeTextData(archive.gmif.files[fileid])
        binary.decrypt()
        #print binary.strlist[0]

        for replace in xmlr.filelist[fileid]:
			if replace < len(binary.strlist):
				binary.strlist[replace]= xmlr.filelist[fileid][replace]
			else:
				print "testing"
				binary.strlist.append(xmlr.filelist[fileid][replace])
        # texttopoke module
        p=texttopoke.Makefile(binary.strlist)

        # to encrypt use
        encrypt = poketext.PokeTextData(p)
        encrypt.SetKey(0xD00E)
        encrypt.encrypt()

        #re-archive    
        archive.replaceFile(fileid, encrypt.getStr())
    #write narc
    WriteMsgNarc(archive)

#cProfile.run('GetText(341, "MyXML.xml")')






#rom and narc code
print "the NEW Poketext"
print "(C) 2008/2009 loadingNOW"
romname = raw_input("Romname:") 
rom = execute.NDSFILES(romname)
rom.dump()
#GetText(341, "MyXML.xml")

while True:
    s = raw_input(">")
    s=s.split(" ")
    if s[0]=="get":
        if len(s)==3:
            print "Trying to dump fileid " + s[1] + " to file: "+ s[2]        
            GetText(int(s[1]), s[2])
            print "Done!"
        else:
            print "get [id] [xmlname], id must be an integer, xmlname is the outfile"
        
#cProfile.run('Rewrite("MyXML2.xml")')
    elif s[0]=="getall":
        if len(s)==2:
            GetTextAll(s[1])
        else:
            print "getall [xmlfilename]"            
    elif s[0]=="patch":
        Rewrite(s[1])
    elif s[0]=="mkrom":
        rom.create(s[1])
    elif s[0]=="q":
        break
    else:
        print """commands:
get [id] [xmlname]\t- dump one file to xml
getall [xmlname]\t- dump all files to xml
patch [xmlname]\t\t- load xmlfile and create new msg.narc
mkrom [romname]\t\t- create rom from tempfiles
q\t\t\t- quit"""
#rom.cleanup()
#GetTextAll("OneBig2.xml")
