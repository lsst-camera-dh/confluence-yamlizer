
# Python 2.7.X Requests library oddity wrt TLS. Needs this wrapper
# See http://stackoverflow.com/questions/14102416/python-requests-requests-exceptions-sslerror-errno-8-ssl-c504-eof-occurred

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

import ssl

class MyAdapter(HTTPAdapter):

	def init_poolmanager(self, connections, maxsize, block=False):

		self.poolmanager = PoolManager(num_pools=connections,
                                           maxsize=maxsize,
                                           block=block,
                                           ssl_version=ssl.PROTOCOL_TLSv1)
