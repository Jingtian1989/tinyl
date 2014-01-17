import type

#constants of the lexical unit
class Tag(object):
	"""Tag"""
	AND 	= 256
	BASIC 	= 257
	BREAK 	= 258
	DO		= 259
	ELSE 	= 260
	EQ 		= 261
	FALSE	= 262
	GE		= 263
	ID 		= 264
	IF		= 265
	INDEX	= 266
	LE		= 267
	MINUS	= 268
	NE		= 269
	NUM		= 270
	OR		= 271
	REAL	= 272
	TEMP	= 273
	TRUE	= 274
	WHILE	= 275

#top class of lexical unit
class Token(object):
	"""Token"""
	def __init__(self, tag):
		super(Token, self).__init__()
		#help make grammer descision
		self.tag = tag
		
	def __str__(self):
		return str(self.tag)

#key words and identifier
class Word(Token):
	"""Word"""
	def __init__(self, lexeme, tag):
		super(Word, self).__init__(tag)
		self.lexeme = lexeme
		
	def __str__(self):
		return self.lexeme

#float
class Real(Token):
	"""Real"""
	def __init__(self, v):
		super(Real, self).__init__(Tag.REAL)
		self.value = v

	def __str__(self):
		return str(self.value)


#integer
class Num(Token):
	"""Num"""
	def __init__(self, v):
		super(Num, self).__init__(Tag.NUM)
		self.value = v

	def __str__(self):
		return str(self.value)



#operators
AND     = Word("&&", Tag.AND)
OR 	    = Word("||", Tag.OR)
EQ 	    = Word("==", Tag.EQ)
NE 	    = Word("!=", Tag.NE)
LE 	    = Word("<=", Tag.LE)
GE      = Word(">=", Tag.GE)

MINUS   = Word("minus", Tag.MINUS)
TRUE    = Word("true", 	Tag.TRUE)
FALSE   = Word("false",	Tag.FALSE)
TEMP    = Word("t", 	Tag.TEMP)

class Lexer(object):
	"""Lexer"""
	line = 1

	def __init__(self, text):
		super(Lexer, self).__init__()
		self.peek   = ' '
		self.words  = dict()
		self.text   = text
		self.cursor = 0
		
		#reserve key words
		self.reserve(Word("if", Tag.IF))
		self.reserve(Word("else", Tag.ELSE))
		self.reserve(Word("while", Tag.WHILE))
		self.reserve(Word("do", Tag.DO))
		self.reserve(Word("break", Tag.BREAK))

		self.reserve(TRUE)
		self.reserve(FALSE)

		self.reserve(type.INT)
		self.reserve(type.CHAR)
		self.reserve(type.BOOL)
		self.reserve(type.FLOAT)


	def isdigit(self, v):
		if v >= '0' and v <= '9':
			return True
		return False

	def isletter(self, v):
		if (v >= 'a' and v <= 'z') or (v >= 'A' and v <= 'Z'):
			return True
		return False

	def isletterOrdigit(self, v):
		return self.isletter(v) or self.isdigit(v)


	def reserve(self, word):
		self.words[word.lexeme] = word

	
	def __readchar(self):
		if self.cursor < len(self.text):
			self.peek = self.text[self.cursor]
			self.cursor = self.cursor + 1
		else:
			self.peek = None

	def __readcharc(self, c):
		self.__readchar()
		if self.peek != c:
			return False
		self.peek = ' '
		return True
	def scan(self):
		while self.peek == ' ' or self.peek == '\t' or self.peek == '\n':
			if self.peek == '\n':
				self.line = self.line + 1
			self.__readchar()

		if self.peek == '&':
			if self.__readcharc('&'):
				return AND
			else:
				return Token('&')
		elif self.peek == '|':
			if self.__readcharc('|'):
				return OR
			else:
				return Token('|')
		elif self.peek == '=':
			if self.__readcharc('='):
				return EQ
			else:
				return Token('=')
		elif self.peek == '!':
			if self.__readcharc('='):
				return NE
			else:
				return Token('!')
		elif self.peek == '<':
			if self.__readcharc('='):
				return LE
			else:
				return Token('<')
		elif self.peek == '>':
			if self.__readcharc('='):
				return GE
			else:
				return Token('>')
		
		if self.isdigit(self.peek):
			v = 0
			while self.isdigit(self.peek):
				v = 10 * v + int(self.peek)
				self.__readchar()
			if self.peek != '.':
				return Num(v)
			
			x = float(v)
			d = float(10)
			while True:
				self.__readchar()
				if self.isdigit(self.peek) is not True:
					break
				x = x + int(self.peek)/d
				d = d * 10
			return Real(x)

		if self.isletter(self.peek):
			s = ""
			while self.isletterOrdigit(self.peek):
				s += self.peek
				self.__readchar()
			if self.words.get(s) is not None:
				return self.words.get(s)
			w = Word(s, Tag.ID)
			self.words[s] = w
			return w

		tok = Token(self.peek)
		self.peek = ' '
		return tok	
	