import subprocess
import os



class NDSFILES:
    def __init__(self, romname):
        self.readmode = 0
        self.r = romname
        self.f = "tmp_"+romname.rsplit(".", 1)[0]
        try:
            os.mkdir(self.f);
        except:
            self.readmode = 2
            print "Using Temp Folder: " +  self.f + " (this is no problem if it exists and contains a complete rom)"
    def dump(self):
        if self.readmode==0 and os.name == 'nt':
            subprocess.call(["ndstool.exe"] + ["-x", self.r, "-9", self.f+"/arm9.bin","-7", self.f+"/arm7.bin","-y9",
                               self.f+"/overarm9.bin","-y7", self.f+"/overarm7.bin","-d", self.f+"/root","-y",
                               self.f+"/overlay","-t", self.f+"/banner.bin","-h", self.f+"/header.bin" ])
            self.readmode = 1
        if self.readmode==0 and os.name == 'posix':
            os.system("wine ndstool.exe "+"-x "+self.r+ " -9 "+self.f+"/arm9.bin "+"-7 "+self.f+"/arm7.bin "+"-y9 "+self.f+"/overarm9.bin "+"-y7 "+ self.f+"/overarm7.bin "+"-d "+self.f+"/root "+"-y "+self.f+"/overlay "+"-t "+self.f+"/banner.bin "+"-h "+ self.f+"/header.bin")
            
    def create(self, name):
        if self.readmode!=0 and os.name == 'nt':
            subprocess.call(["ndstool"] + ["-c", name, "-9", self.f+"/arm9.bin","-7", self.f+"/arm7.bin","-y9",
                               self.f+"/overarm9.bin","-y7", self.f+"/overarm7.bin","-d", self.f+"/root","-y",
                               self.f+"/overlay","-t", self.f+"/banner.bin","-h", self.f+"/header.bin"])
        if (self.readmode!=0) and (os.name == "posix"):
            os.system("wine ndstool.exe "+"-c "+name+ " -9 "+self.f+"/arm9.bin "+"-7 "+self.f+"/arm7.bin "+"-y9 "+self.f+"/overarm9.bin "+"-y7 "+ self.f+"/overarm7.bin "+"-d "+self.f+"/root "+"-y "+self.f+"/overlay "+"-t "+self.f+"/banner.bin "+"-h "+ self.f+"/header.bin")
    def getFolder(self):
        return self.f
    def cleanup(self):
        if self.readmode ==1:
            os.removedirs(self.f)
"""		def patch(self, patchname, newrom):
        if self.readmode!=0 and os.name == 'nt':
            subprocess.call(["xdelta"] + ["patch", patchname, self.r, newrom])
        if (self.readmode!=0) and (os.name == "posix"):
            os.system("wine xdelta.exe "+"patch "+patchname+ " "+self.r+" "+newrom)
		def mkpatch(self, patchname, newrom):
        if self.readmode!=0 and os.name == 'nt':
            subprocess.call(["xdelta"] + ["delta", self.r, newrom, patchname])
        if (self.readmode!=0) and (os.name == "posix"):
            os.system("wine xdelta.exe "+"delta "+self.r+" "+newrom+ " "+patchname)"""

