

import re
import os

#These dependencies are custom code...
from confluence import confluence_fetcher_rest as cf
from tinyxml import xml_kit

class eTPageParser:

	def __init__(self, space, pagetitle):

                self.space = space
                self.pagetitle = pagetitle

		self.fetcher = cf.ConfluenceFetcher()	
		self.pather = xml_kit.XMLKit()

		# XPath for Confluence rendered (HTML) format
		# GOD IN HEAVEN REMEMBER TO START ONE LEVEL DOWN, NOT AT ROOT ELEMENT!!!
		#self.XPATH_requiredinputs = "//table//tbody//tr/th[text()='Label']/../../.."
		self.XPATH_requiredinputs = "//table/tbody/tr/th"
                self.XPATH_img = "//img"
                self.XPATH_panels = "//div[@class='panelContent']"
                self.XPATH_prerequisites = "//table/tbody//tr/th[text()='PrerequisiteType']/../../.."

                self.reqinputstagset = ["Label: ", "Description: ", "InputSemantics: ", "Now: "]
                self.prerequisitestagset = ["PrerequisiteType: ", "Name: ", "Description: "]
                self.hardwaregrouptagset = ["HardwareGroup: "]
                self.hardwarerelationshiptagset = ["RelationshipName: ", "RelationshipAction: "]

                self.requiredinputs = []
                self.optionalinputs = []
                self.prereqs = []
                self.hardwarerelationshiptaskslist = []
                self.stepdescription = []
                self.hardwaregroup = []
                self.travdict = {"hardwaregroup":self.hardwaregroup, "stepdescription":self.stepdescription, "title":None, "prereqs":self.prereqs, "required":self.requiredinputs, "optional":self.optionalinputs, "hardwarerelationships":self.hardwarerelationshiptaskslist} 

                self.stepChildren = None
	
                self._fetch()
                self._parseDescriptionPanels()
                self._parseTables()
                self._parseIMGTags()
                #self._parsePrerequisites()
                self._parseTitle()

	def _fetch(self):

		self.fetcher.setPage(self.space, self.pagetitle)	
		anHTMLPage = self.fetcher.renderedPage()
                self.stepChildren = self.fetcher.pageChildren() 

		cleanPage = self.pather.clean(anHTMLPage.encode("UTF-8"))	
                cleanPageNoIMG = self.pather.replaceBadIMGTags(cleanPage)

		# Post 5.X Confluence update, the HTML structure of the user content section changed
		# No longer wrapped in a big ol div? So now adding a div wrapper to create one XML root so ET will parse
		# This seems really really icky
		onerootcleanhtml = "<div>" + str(cleanPageNoIMG) + "</div>"

                quotesfixedhtml = self._cleanPageSource(onerootcleanhtml)

		#print "HEYYYYY------------------"
		#print onerootcleanhtml 

		self.linkPageTree = self.pather.parsesource(quotesfixedhtml)

        def _cleanPageSource(self, htmlsource):

                #print htmlsource

                # Confluence editor allows a fair amount of junk in
                sourcequotesfixed = htmlsource.replace("&amp;quot;",'"')

                return sourcequotesfixed


        # The lxml parser seems to enjoy adding a few character codes that choke the eT parser with their &, #, etc. characters
        # Most common example is lxml converting a space to a non-breaking space &#160;
        # So we convert back

        def _fixParsedSource(self, aString):

            nbspfixedsource = aString.replace("&#160;", " ")

            #Now let's replace all double quotes inside the source with single quotes
            #so the entire block can be escaped with double quotes to make the eT ingester with double quotes

            sourceinternalsinglequotes = nbspfixedsource.replace('"','\'')

            return sourceinternalsinglequotes

        def _extractColumnContents(self, anIndex, aColumn, inputtype, tagset):

                # Horrible anIndex hack

                if anIndex < 3:
            
                    cellcontents = ""

                    #print "FIRST TRY: " + aColumn.text + ''.join(map(self.pather.tostring, aColumn)).strip()

                    if aColumn.text != None:
                        cellcontents = aColumn.text + "".join(map(self.pather.tostring, aColumn)).strip()
                    else:
                        cellcontents = "".join(map(self.pather.tostring, aColumn)).strip()

                    cleanedcellcontents = self._fixParsedSource(cellcontents)

                    self.travdict[inputtype].append("\t" + tagset[anIndex] + "\"" + cleanedcellcontents.encode("UTF-8") + "\"")

                return

        def _parsePrerequisites(self, rows):

            for row in rows:

                columns = self.pather.xpath("td", row)

                for idx, column in enumerate(columns):

                    self._extractColumnContents(idx, column, "prereqs", self.prerequisitestagset)

            #print "Hub..." + str(self.prerequisites)

        def _parseDescriptionPanels(self):

            panels = self.linkPageTree.xpath(self.XPATH_panels)

            for panel in panels:
            
                #print self.pather.tostring(panel)
                tweakedsource = self._fixParsedSource(self.pather.tostring(panel))

                self.travdict["stepdescription"].append("\"" + tweakedsource + "\"")

        def _parseRequiredInputs(self, rows):

            for row in rows:

                columns = self.pather.xpath("td", row)

                print "-"

                for idx, column in enumerate(columns):

                    if (re.search("N", self.pather.tostring(columns[3]))) != None:

                        #print self.pather.tostring(column)

                        self._extractColumnContents(idx, column, "required", self.reqinputstagset)

                    if (re.search("Y", self.pather.tostring(columns[3]))) != None:

                        self._extractColumnContents(idx, column, "optional", self.reqinputstagset)


        def _parseIMGTags(self):
                
            imgtags = self.linkPageTree.xpath(self.XPATH_img)

        def _parseHardwareGroup(self, rows):

            for row in rows:

                columns = self.pather.xpath("td", row)

                for idx, column in enumerate(columns):

                    self._extractColumnContents(idx, column, "hardwaregroup", self.hardwaregrouptagset)

            #print "Hub..." + str(self.prerequisites)

        def _parseRelationshipTasks(self, rows):

            for row in rows:

                columns = self.pather.xpath("td", row)

                for idx, column in enumerate(columns):

                    #print self.pather.tostring(column)

                    if idx == 0 or idx == 1:
                        self._extractColumnContents(idx, column, "hardwarerelationships", self.hardwarerelationshiptagset)

	def _parseTables(self):

            #print self.linkPageTree

            requiredinputstable = self.linkPageTree.xpath(self.XPATH_requiredinputs)

            for item in requiredinputstable:

                #print item.text.encode("UTF-8")

                if (re.search("Label", item.text) != None):

                    #print "Hey, something that matches 'Label'..." + item.text
                   
                    rows = self._getRows(item)
                    self._parseRequiredInputs(rows)

                if (re.match("PrerequisiteType", item.text) != None):

                    #print "Hey prereqs!"
                   
                    rows = self._getRows(item)
                    self._parsePrerequisites(rows)

                if (re.match("HardwareGroup", item.text) != None):

                    rows = self._getRows(item)
                    self._parseHardwareGroup(rows)

                if (re.match("RelationshipName", item.text) != None):

                    rows = self._getRows(item)
                    self._parseRelationshipTasks(rows)

        def _getRows(self, item):

            ancestorrow = item.getparent()
            ancestorbody = ancestorrow.getparent()
            aTable = ancestorbody.getparent()

            aTableSrc = self.pather.tostring(aTable)
            aTableParsed = self.pather.parsesource(aTableSrc)

            rows = self.pather.xpath("//tr", aTableParsed)

            return rows        

        def _parseTitle(self):

            self.travdict["title"] = self.pagetitle

        def hasChildren(self):

                if self.stepChildren["size"] > 0:
                    return True
                else:
                    return False

        def stepChildTitles(self):

                stepChildTitles = []

                for item in self.stepChildren["results"]:

                   stepChildTitles.append(item["title"]) 

                return stepChildTitles

        def shortdescription(self):

            print "ShortDescription: " + "\"" + self.travdict["title"] + "\""

        def hardwareGroup(self):
            
            if self.travdict["hardwaregroup"]:

                for item in self.travdict["hardwaregroup"]:

                    print item 

            else:

                pass

        def stepDescriptions(self):

            descriptionstring = "Description: "

            if self.travdict["stepdescription"]:

                for item in self.travdict["stepdescription"]:

                    stripped = lambda s: "".join(i for i in s if 31 < ord(i) < 127)

                    descriptionstring += stripped(item)

                print descriptionstring

            else:

                pass
               
        def prerequisites(self):

            if self.travdict["prereqs"]:

                print "Prerequisites:"

                for idx, item in enumerate(self.travdict["prereqs"]):
                    if (idx%3) == 0:
                        print "-"
                    print item
            else:

                pass

        def inputs(self):                            

            if self.travdict["required"]:
        
                print "RequiredInputs:"

                for idx, item in enumerate(self.travdict["required"]):
                    if (idx%3) == 0:
                        print "-"
                    print item

                if len(self.travdict["optional"]) > 0:
                    print "\nOptionalInputs:"
                    for idx, item in enumerate(self.travdict["optional"]):
                        if (idx%3) == 0:
                            print "-"
                        print item

            else:

                pass

        def hardwarerelationshiptasks(self):

            if self.travdict["hardwarerelationships"]:

                print "RelationshipTasks:"

                for idx, item in enumerate(self.travdict["hardwarerelationships"]):
                    if (idx%2) == 0:
                        print "-"
                    print item
            else:

                pass
