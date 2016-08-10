
import sys

import requests, json 

import re

from tinylogging import logging
from tinyxml import xml_kit
from https import requests_tlsadapter

class ConfluenceFetcher:

	def __init__(self):

		self.logger = logging.Logger("reddoc.fetcher") 
		self.xmlkit = xml_kit.XMLKit()

		self.s = requests.Session()
		self.s.mount("https://", requests_tlsadapter.MyAdapter())

		self.thisPage = None
		self.thisPageTitle = None
		self.thisPageContents = None
		self.thisPageHTMLContents = None
		self.thisPageHistory = None
                self.thisPageChildren = None	
	
		self.pageID = None
		self.pageSpace = None
		self.thisRenderedPage = None

		# The following regex matches the pageID and attachment filename portion of a Confluence attachments URL
		# when that URL contains a "modificationDate" string. Group 2 captures the pageID, group 3 the filename 
		self.RE_pageidinurl_moddate = "(attachments/)([0-9]*)(/)(.*)(\?)"

		# The following regex matches the pageID and attachment filename portion of a Confluence attachments URL
		# when that URL does not contain a "modificationDate" string. Group 2 captures the pageID, group 3 the filename 
		self.RE_pageidinurl = "(attachments/)([0-9]*)(/)(.*)"

	def _page(self, space, pagetitle):

		try:
			# Assume for now we only want the rendered HTML, so expand:body.view by default
			response = self.s.get("https://confluence.slac.stanford.edu/rest/api/content/",
						params={'title':pagetitle, 'spaceKey':space, 'expand':'body.view'},
						auth=('userid','password'))
			#renderedPage = self.rpcserver.confluence2.getParenderContent(self.confluencetoken, space, str(page["id"]), page["content"])
			#self.logger.log("INFO","Fetched page(s) from Confluence", None)
		except requests.exceptions.ConnectionError, err:
			self.logger.log("FATAL","Requests library Connection Error while fetching from Confluence", err)
		#except ResponseError, err:
		#	self.logger.log("FATAL","Response Error while fetching from Confluence", err.faultString)
		#except UnicodeDecodeError, err:
		#	self.logger.log("FATAL","Unicode Decode Error while fetching from Confluence", [err, str(sys.exc_info())])
		except:
			self.logger.log("FATAL","Other Error while fetching from Confluence", str(sys.exc_info))

		self.thisPage = response.json()

                #print self.thisPage

		self.pageID = self.thisPage["results"][0]["id"]
		self.pageSpace = space
		self.thisPageHTMLContents = self.thisPage["results"][0]["body"]["view"]["value"]

		#print self.thisPage

		# The following saves the page in Confluence storage format
		# Namespace declarations must be added to make that useful
		#self.thisPageContents = response["content"]
		#self._addNamespace()

		# Ask the server for the full HTML-rendered version of the page
		# self.thisRenderedPage = self._renderPage()

	def _addNamespace(self):

		# Confluence storage format does not come with root elements or namespace declarations
		# Bad, bad Confluence. Must add root and namespaces

		tmpPageContent = '' 

		tmpPageContent += '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ac="http://123" xmlns:ri="http://456">'
		tmpPageContent += self.thisPageContents
		tmpPageContent += '</html>'

		self.thisPageContents = tmpPageContents

		#print self.thisPageContents

	def _getHistory(self):

		try:
			response = self.s.get("https://confluence.slac.stanford.edu/rest/api/content/"+self.pageID+"/history",
						auth=('userid','password'))
			#self.logger.log("INFO","Fetched page(s) from Confluence", None)
		except:
			self.logger.log("FATAL","Other Error while fetching from Confluence", str(sys.exc_info))

		#print response.json()

		self.thisPageHistory = response.json()

		#for item in self.thisPageHistory:
		#	print item

        def _getChildren(self):

		try:
			response = self.s.get("https://confluence.slac.stanford.edu/rest/api/content/"+self.pageID+"/child/page",
						auth=('userid','password'))
			#self.logger.log("INFO","Fetched page(s) from Confluence", None)
		except:
			self.logger.log("FATAL","Other Error while fetching from Confluence", str(sys.exc_info))

		#print response.json()

		self.thisPageChildren = response.json()

		#for item in self.thisPageChildren:
                #        print self.thisPageChildren["size"] 
    		#	print item

	def setPage(self, space, pagetitle):

		self.thisPageTitle = pagetitle

		self._page(space, pagetitle)
		self._getHistory()
                self._getChildren()


	def page(self):
		
		return self.thisPage		

	def renderedPage(self):

		return self.thisPageHTMLContents

	def pageContents(self):

		return self.thisPageContents

	def pageHistory(self):

		return self.thisPageHistory

        def pageChildren(self):

                return self.thisPageChildren

	def pageID(self):

		return self.pageID

	# Interface/return. Take rendered page as argument, look for embedded img tags and retrieve the images from confluence. Return list of image blobs.
	
	# The rendered HTML will have no breadcrumbs to show what page an image added via the include macro is attached to. Can search globally or pacticular space for attachment filename, but what about non-uniqueness?
	#	Add code to order attachments by: (1) attached to a child page, (2) attachment in same space as page, (3) others. Be sure to log any cases where there were non-unique filenames.	
        #       If possible, might want to just use urllib/httplib to get the attachment by HTTPS since it already unambiguously points to what you need....

	# Need to test and address: (a) import macro effects with various combinations of: Gliffy insert, image attachment insert, image thumbnail insert

	def imageURLs(self, renderedpage):
		
		# Refactor - this code is called in several places		
		cleanedsource = self.xmlkit.clean(renderedpage)

		# print cleanedsource

		parsedsource = self.xmlkit.parsesource(cleanedsource)

		# This XPath handles, in order, inserted attachments without thumbnails, inserted attachments with thumbnails, inserted Gliffy images
		# More complex cases will involve images (thumbs or full) nested inside Confluence tables and section+column constructs
		imagesrcs = self.xmlkit.xpath("//*/p/span[@class='image-wrap']/img/@src | //*/p/span[@class='image-wrap']/a/@href | //*/caption/following-sibling::tr/td/img/@src", parsedsource)

		
		# print "Here the raw URLs of embedded images: " + str(imagesrcs)

		imageIDs = self.imageIDs(imagesrcs)

		return imageIDs

		# fixedurls = self._fixurls(imagesrcs)	
		# print "Here are the fixed URLs of embedded images: " + str(fixedurls)

		# OK! So the URLs will contain the pageID of the graphic attachment's parent page, so parse out that ID then just use getAttachment to pull down...
		# Some URLs have attachment modification date/version strings at the end, so test for "modificationDate" in the URL, regex one way, otherwise regex another way

		# imagefilenames = self._imagefilenames(imagesrcs)

	def imageIDs(self, urllist):
		
		tuplelist = []
		
		for item in urllist:

			idtuple = tuple()

			amatch = re.search("modificationDate", item)
	
			if (amatch == None): 
				bmatch = re.search(self.RE_pageidinurl, item)
				idtuple = (bmatch.group(2), bmatch.group(4))
				tuplelist.append(idtuple)

			else:
				bmatch = re.search(self.RE_pageidinurl_moddate, item)
				idtuple = (bmatch.group(2), bmatch.group(4))
				tuplelist.append(idtuple)

		return tuplelist

	def listAttachments(self, pageID):

		attachmentslist = []

		attachmentslist = self.rpcserver.confluence2.getAttachments(self.confluencetoken, pageID)

		#for item in attachmentslist:
		#	print item["fileName"].encode("UTF-8")

		return attachmentslist

	def attachments(self, filenamelist): 

		print "Entered!"

		filedata = dict()

		for item in filenamelist:

			#f = open(item[1], "wb")

			try:
				# Note, when Confluence 4 installed, access the version 2 API by changing the following to 'rpcserver.confluence2....'
				# In fact, change all confluence1 references... 
				attachment = self.rpcserver.confluence2.getAttachmentData(self.confluencetoken, self.pageID, item, str(0))
				self.logger.log("INFO","Fetched attachment from Confluence", None)
			except XMLRPCFault, err:
				self.logger.log("FATAL","XML-RPC Error while fetching from Confluence", err.faultString)
			except ResponseError, err:
				self.logger.log("FATAL","Response Error while fetching from Confluence", err.faultString)
			except UnicodeDecodeError, err:
				self.logger.log("FATAL","Unicode Decode Error while fetching from Confluence", [err, str(sys.exc_info())])
			except:
				self.logger.log("FATAL","Other Error while fetching from Confluence", str(sys.exc_info()))

			filedata[item] = attachment.data

			# f.close()

		 	yield filedata


	''' def _fixurls(self, imagesrcs):

		# Need to prepend the baseurl as needed

		fixedurls = []

		for item in imagesrcs:
		
			if (re.match("^https", item) == None):
				fixeditem = self.urldomain + item
				# print fixeditem
				fixedurls.append(fixeditem)
			else:
				# print re.match("(?<=https:)(.*)", item) 
				fixedurls.append(item)	

		return fixedurls
		 '''

class LocalApp:

	def __init__(self, args):

		self.unit_args = args

	def main(self):

		args = self.unit_args.fetchparser.parse_args()
		
		#from confluence import confluence_server as cs

		#server = cs.ConfluenceServer()
		#rpcinterface, token = server.connect()
		fetcher = ConfluenceFetcher()

		aPage = fetcher.setPage(args.space, args.page) 

		if (args.fetchcommand == "pageinfo"):
			print "PageID: " + fetcher.pageID
		if (args.fetchcommand == "attachmentsinfo"):
			print fetcher.listAttachments(fetcher.pageID)
		if (args.fetchcommand == "renderedpage"):
			print(fetcher.renderedPage()).encode("UTF-8")

if __name__ == "__main__":

	import sys

	sys.path.append("./config")
	import fetcher_args

	app = LocalApp(fetcher_args)

	status = app.main()
	sys.exit(status)
