from chord.settings import SIZE
import hashlib

# Helper function to determine if a key falls within a range
def inrange(c, a, b):
	# is c in [a,b)?, if a == b then it assumes a full circle
	# on the DHT, so it returns True.
	a = a % SIZE
	b = b % SIZE
	c = c % SIZE
	if a < b:
		return a <= c and c < b
	return a <= c or c < b

class Address(object):
	def __init__(self, ip, port):
		self.ip = ip
		self.port = int(port)

	def __hash__(self):
		return int(hashlib.sha256(("%s:%s" % (self.ip, self.port)).encode("utf-8")).hexdigest(),16) % SIZE

	def __cmp__(self, other):
		return other.__hash__() < self.__hash__()

	def __eq__(self, other):
		return other.__hash__() == self.__hash__()

	def __str__(self):
		return "[\"%s\", %s]" % (self.ip, self.port)
