# -*- coding: latin-1 -*- 
import codecs
import xml.dom.minidom


class XMLWriter():
    def __init__(self, save):
        self.datei = codecs.open(save, "w", "utf-8")        
        xml = u"<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n"
        xml += u"<Poketext version=\"1.0\">\r\n"
        self.datei.write(xml)

    def addStrings(self, strings, fileid):
        xml = u"<file id=\"%d\" change=\"false\">\r\n" %fileid
        for i, s in enumerate(strings):
            xml += u"<text id=\"%d\">\r\n" %i
            xml += u"\t" + s + u"\r\n"
            xml += u"</text>\r\n"
        xml += u"</file>\r\n"
        self.datei.write(xml)
    def writeFile(self):        
        self.datei.write(u"</Poketext>\r\n")
        self.datei.close()

    
class XMLReader:
    def __init__(self, xmlfile):
        self.dom = xml.dom.minidom.parse(xmlfile)
        self.filelist = {}
        
    def liesText(self, knoten):
        for k in knoten.childNodes:
            if k.nodeType == k.TEXT_NODE:
                return k.nodeValue.strip()
     
    def liesFile(self, knoten):
        for num, elem in enumerate(knoten.getElementsByTagName("file")):

            if elem.getAttribute("change") != "false":
                try:
                    self.filelist[int(elem.getAttribute("id"))]={}
                except:
                    print "WARNING: file id must be an integer"
                    continue 
                
                for knotenNamen in elem.getElementsByTagName("text"):
                    self.filelist[int(elem.getAttribute("id"))][int(knotenNamen.getAttribute("id"))]=self.liesText(knotenNamen)
             
           
            
     
    def dokument(self, start):
        i = 0        
        for elem in start.getElementsByTagName("Poketext"):
            print "Parsing Pokexml Version " + elem.getAttribute("version")
            self.liesFile(elem)
            if i>0:
                print "WARNING: xml has 2 Poketext sections"
            i = i+1
            

     
    def ParseptextXML(self):             
        self.dokument(self.dom)



#strings = [ u"Ha   llo", u"Mega", u"Maän" ]
#xmlw = XMLWriter("data.xml")
#xmlw.addStrings(strings, 0)
#xmlw.writeFile()



#xml = XMLReader("OneBig2.xml")
#xml.ParseptextXML()

#print xml.filelist


