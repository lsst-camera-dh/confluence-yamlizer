
import sys
import logging

'''
	Python's logging library allows you to create multiple loggers with IDs
	and then configure how output of each logger is handled (to console, to file, etc.)

	So this generic logging interface just needs the user to choose the logger ID once, then with each message say severity and error description

'''

class Logger:
	
	# Set this up so user passes the name of a logging facility (e.g., "reddoc.serverlog")
	# Future proofing: modify the constructor to allow you to tie in different logging library
	def __init__(self, loggertype):
		pass

	# Need to make message a list so user can pass variable number of arguments - a string plus exception message plus something else...
	def log(self, severity, message, additional):
		print severity, message, additional
		# print severity, message	


