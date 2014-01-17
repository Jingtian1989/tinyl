from lexer import *

class Type(Word):
	INT 	= Type("int", 	Tag.BASIC, 4)
	FLOAT 	= Type("float", Tag.BASIC, 8)
	CHAR 	= Type("char", 	Tag.BASIC, 1)
	BOOL 	= Type("bool", 	Tag.BASIC, 1)

	@classmethod
	def numeric(clz, p):
		if p == clz.CHAR or p == clz.INT or p == clz.FLOAT:
			return True
		return False

	@classmethod
	def max(clz, p1, p2):
		if clz.numeric(p1) == False or clz.numeric(p2) == False:
			return None
		elif p1 == clz.FLOAT or p2 == clz.FLOAT:
			return clz.FLOAT
		elif p1 == clz.INT or p2 == clz.INT:
			return clz.INT
		else:
			return clz.CHAR

	"""Type"""
	def __init__(self, s, tag, w):
		super(Type, self).__init__(s, tag)
		self.width = w



class Array(Type):
	"""Array"""
	def __init__(self, sz, p):
		super(Array, self).__init__("[]", Tag.INDEX, sz*p.width)
		self.size = sz 	#number of elements
		self.of = p 	#array of type

	def __str__(self):
		return "[" + str(self.size) + "]" + str(self.of)
		

class Enviroment(object):
	"""Enviroment"""
	def __init__(self, prev):
		super(Enviroment, self).__init__()
		self.prev 	= prev
		self.table 	= dict()

	def put(self, tok, i):
		table[tok] = i
	def get(self, tok):
		e = self
		while e is not None:
			found = e.table.get(tok)
			if found is not None:
				return found
			e = e.prev
		return None
		