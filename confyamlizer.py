
class Application:

	def __init__(self, args, config, etpp):

            self.args = args.cymlparser.parse_args()
            self.config = config

            self.etpp = etpp.eTPageParser(self.args.space, self.args.pagetitle) 

	def main(self):

            # Get the Name, Desciption, other content from the top-level node
            print "Name: " + "\"" + self.args.nameprefix + "\""
            print "\n"
            self.etpp.shortdescription()
            print "\n"
            self.etpp.hardwareGroup()
            print "\n"
            self.etpp.stepDescriptions()
            print "\n"
            self.etpp.prerequisites()
            print "\n"
            self.etpp.inputs()
            print "Version: next"
            print "\n"
            print "Sequence:\n"
            print "-\n"

            # All of them will have children, now gather Step Name, Description, Inputs from step child pages
            if self.etpp.hasChildren():
                stepChildTitles = self.etpp.stepChildTitles()

                for index, item in enumerate(stepChildTitles):
                    self.etpp = etpp.eTPageParser(self.args.space, item)
                    print "Name: " + "\"" + self.args.nameprefix + "_step" + str(index+1) + "\""
                    self.etpp.shortdescription()
                    print "Version: next"
                    print "\n"
                    self.etpp.stepDescriptions()
                    print "\n"
                    self.etpp.prerequisites()
                    print "\n"
                    self.etpp.inputs()

if __name__ == "__main__":

	import sys
	from datetime import datetime

	sys.path.append("./config")
	import cyml_config
	import cyml_args

	sys.path.append("./src")
        import eTPageParser as etpp

	app = Application(cyml_args, cyml_config, etpp)

	status = app.main()
	sys.exit(status)
