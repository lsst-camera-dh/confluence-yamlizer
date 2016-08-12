
import argparse

# ==============================
# Common elements

REGEX_docnumtoken = ",|:|;"
REGEX_docfilelisttoken = ",|;"
REGEX_updatestringtoken = ":"
REGEX_updatestringkeys = "="

#===============================
# Arguments for lcarecord.py

cymlparser = argparse.ArgumentParser(description='Fetch eTraveler content from Confluence pages and parse into YAML.')

#cymlparser.add_argument("LCAcommand", metavar='"command"',  
#                   help='Command to execute, one of "status", "create", "update", "download", "upload".')

cymlparser.add_argument("--pagetitle", required=True,  
                   help='Title of a page containing formatted eTraveler content.')

cymlparser.add_argument("--space", required=True, 
                   help='Confluence space of the page containing formatted eTraveler content.')

cymlparser.add_argument("--nameprefix", required=True, 
                   help='Process step name, used as is for the Name of the top-level traveler step (e.g., "REB-ASY"), then used as a prefix to construct Name fields for child steps (e.g., "REB-ASY_step1").')

cymlparser.add_argument("--subsystem", required=True, 
                   help='Subsystem to which the traveler belongs.')


