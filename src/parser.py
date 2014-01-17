from type import *
from lexer import *
class Parser(object):
	"""Parser"""
	def __init__(self, lexer):
		super(Parser, self).__init__()
		self.lexer = lexer #lexical analyzer for this parser
		self.look  = None  #lookahead tagen
		self.top   = None  #current or top symbol table
		self.used  = 0 	   #storage used for declarations

		self.move()

	def move(self):
		self.look = self.lexer.scan()

	def error(self, s):
		raise Exception("error at line : %d, %s."%(self.lexer.line, s))

	def match(self, t):
		if self.look == t:
			self.move()
		else:
			self.error("syntax error")
	def program(self):
		s = self.block()
		begin = s.newlabel()
		after = s.newlabel()
		s.emitlabel(begin)
		s.gen(begin, after)
		s.emitlabel(after)

	def block(self):
		self.match("{")
		savedEnv = self.top
		self.top = Enviroment(self.top)
		self.decls()
		s = self.stmts()
		self.match("}")
		self.top = savedEnv
		return s

	def decls(self):
		while self.look == Tag.BASIC:
			ty  = self.type()
			tok = self.look
			self.match(Tag.ID)
			self.match(';')
			id = Id(tok, ty, self.used) 
			self.top.put(tok, id)
			self.used = self.used + ty.width

	def type(self):
		ty = self.look
		self.match(Tag.BASIC)
		if self.look != '[':
			return ty
		else:
			return self.dims(ty)

	def dims(self, ty):
		self.match('[')
		tok = self.look
		self.match(Tag.NUM)
		self.match(']')
		if self.look.tag == '[':
			ty = self.dims(ty)
		return Array(tok.value, ty)

	def stmts(self):
		if self.look == '}':
			return Stmt.Null
		else:
			return Seq(self.stmt(), self.stmts())
	def stmt(self):
		if self.look.tag == ';':
			self.move()
			return Stmt.Null
		elif self.look.tag == Tag.IF:
			self.match(Tag.IF)
			self.match('(')
			x = self.bool()
			self.match(')')
			s1 = self.stmt()
			if self.look.tag != Tag.ELSE:
				return If(x, s1)
			self.match(Tag.ELSE)
			s2 = self.stmt()
			return ELSE(x, s1, s2)
		elif self.look.tag == Tag.WHILE:
			whilenode = While()
			savedStmt = Stmt.Enclosing
			Stmt.Enclosing = whilenode
			self.match(Tag.WHILE)
			self.match('(')
			x = self.bool()
			self.match(')')
			s1 = self.stmt()
			whilenode.init(x, s1)
			Stmt.Enclosing = savedStmt
			return whilenode
		elif self.look.tag == Tag.DO:
			donode = Do()
			savedStmt = Stmt.Enclosing
			Stmt.Enclosing = donode
			self.match(Tag.DO)
			s1 = self.stmt()
			self.match(Tag.WHILE)
			self.match('(')
			x = self.bool()
			self.match(')')
			self.match(';')
			donode.init(s1, x)
			Stmt.Enclosing = savedStmt
			return donode
		elif self.look.tag == Tag.BREAK:
			self.match(Tag.BREAK);
			self.match(';')
			return Break()
		elif self.look.tag == '{':
			return self.block()
		else:
			return self.assign()

	def assign(self):
		stmt = None
		tok	 = self.look
		self.match(Tag.ID)
		id = top.get(tok)
		if id == None:
			self.error(str(tok) + "undeclared")
		if self.look.tag == '=':
			self.move()
			stmt = Set(id, self.bool())
		else:
			x = self.offset(id)
			self.match('=')
			stmt = SetElem(x, self.bool())
		self.match(';')
		return stmt
	def bool(self):
		x = self.join()
		while self.look.tag == Tag.OR:
			tok = self.look
			self.move()
			x = Or(tok, x, self.join())
		return x

	def join(self):
		x = self.equality()
		while self.look.tag == Tag.AND:
			tok == self.look
			self.move()
			x = And(tok, x, self.equality())
	def equality(self):
		x = self.rel()
		while self.look.tag == Tag.EQ or self.look.tag == Tag.NE:
			tok = self.look
			self.move()
			x = Rel(tok, x, self.rel())

	def rel(self):
		x = self.expr()
		if self.look.tag == '<' or self.look.tag == Tag.LE or self.look.tag == Tag.GE or self.look.tag == '>':
			tok = self.look
			self.move()
			return Rel(tok, x, self.expr())
	def expr(self):
		x = self.term()
		while self.look.tag == '+' or self.look.tag == '-':
			tok = self.look.tok
			self.move()
			x = Arith(tok, x, self.term())
		return x

	def term(self):
		x = self.unary()
		while self.look.tag == '*' or self.look.tag == '/':
			tok = self.look
			self.move()
			x = Arith(tok, x, self.unary())

	def unary(self):
		if self.look.tag == '-':
			self.move()
			return Unary(Word.MINUS, self.unary())
		elif self.look.tag == '!':
			tok = self.look
			self.move()
			return Not(tok, self.unary())
		else:
			return self.factor()

	def factor(self):
		x = None
		if self.look.tag == '(':
			self.move()
			x = self.bool()
			self.match('}')
			return x
		elif self.look.tag == Tag.NUM:
			x = Constant(self.look, Type.INT)
			self.move()
			return x
		elif self.look.tag == Tag.REAL:
			x = Real(self.look, Type.FLOAT)
			self.move()
			return x
		elif self.look.tag == Tag.TRUE:
			x = Constant.TRUE
			self.move()
			return x
		elif self.look.tag == Tag.FALSE:
			x = Constant.FALSE
			self.move()
			return x
		elif self.look.tag == Tag.ID:
			s = str(self.look)
			id = top.get(self.look)
			if id == None:
				self.error(str(self.look) + "undeclared")
			self.move()
			if self.look.tag != '[':
				return id
			else:
				return self.offset(id)
		else:
			self.error("syntax error")
			return x
	def offset(self, id):
		ty = id.type
		self.match('[')
		i = self.bool()
		self.match(']')
		ty = type.of
		w = Constant(ty.width)
		t1 = Arith(Token('*'), i, w)
		loc = t1
		while self.look.tag == '[':
			self.match('[')
			i = self.bool()
			self.match(']')
			ty = ty.of
			w = Constant(ty.width)
			t1 = Arith(Token('*'), i, w)
			t2 = Arith(Token('+'), loc, t1)
			loc = t2
		return Access(id, loc, ty)


