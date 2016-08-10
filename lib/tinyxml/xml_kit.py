
from lxml import etree
import re

class XMLKit:

	def __init__(self):
		
		pass


	def XMLfile(self, xmlfilepath):

		parser = etree.XMLParser(recover=True, encoding="utf-8")
		
		f = open(xmlfilepath, "rb")

		xml_root = etree.parse(f, parser)

		return xml_root		


	def XSLtransformer(self, xslfilepath):

		f = open(xslfilepath, "r")

		xslt_root = etree.XML(f.read())

		transformer = etree.XSLT(xslt_root)

		return transformer

	

	def removeInvalidComments(self, sourcehtml):
		
		htmlcopy = "" 

		for line in sourcehtml:

			print "LINEBYLINE" + line.encode("utf-8")
	
			if re.match("\\*", line):
				linecopy = ""
			else:
				linecopy = line
			htmlcopy += linecopy

		print htmlcopy.encode("utf-8")
			
		return htmlcopy

	def clean(self, sourcehtml):

		editlist = []

		# Comment out if problems
		#maybeclean = sourcehtml.encode('utf-8')

		entities = [
		    ('&nbsp;', u'\u00a0'),
		    ('&', '&amp;'),
		    (chr(20), u'\u2014'),
		    (chr(28), u'\u0022'),
		    (chr(29), u'\u0022'),
		    (chr(25), u'\u0027')
		    ]

		for before, after in entities:
			
			#maybeclean = maybeclean.replace(before, after.encode('utf-8'))
			sourcehtml = sourcehtml.replace(before, after.encode('utf-8'))

		return sourcehtml 

        # Some systems don't output self-closing IMG tags. Confluence, how could you?	
        def replaceBadIMGTags(self, sourceHTML):

                if (re.search("<img", sourceHTML)) != None:

                    #for m in re.findall('(<span class="confluence-embedded-file.*)(<img.+">)(<\/span>)', sourceHTML):
                    for m in re.findall('<img[^>]+="[^">]+">', sourceHTML):

                        aThing = m.replace('">','"/>')

                        sourceHTML = sourceHTML.replace(m, aThing)

                return sourceHTML 

        # Something about the following method is assigning parsedsource to this instantiatedi XMLKit object
        # and making subsequence e.g. xpath calls parse the whole tree
	def parsesource(self, sourcehtml):

		parsedsource = etree.XML(sourcehtml)

		return parsedsource

	# Skip all of the <head> element crap and skip right to the <body> section. Need to extract it/
	def extract(self, parsedsource):

		bodyelement = parsedsource.find("body")

		return bodyelement

	def transform(self, xsltransformer, parsedsource):

		resultdoc = xsltransformer(parsedsource)

		return resultdoc

	def xpath(self, expression, parsedsource):

		search = etree.XPath(expression)

		result = search(parsedsource)

		return result

	def tostring(self, element):

		return etree.tostring(element)

	def setclean(self, source):

		self.cleanedsource = source

	def test(self):
		
		pass


def main():

	kit = XMLKit()

	kit.test()	


if __name__ == "__main__":

	import sys

	status = main()
	sys.exit(status)
