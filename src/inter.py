from lexer 	import *
from type 	import *
#抽象语法树中的结点被实现为类Node的对象
#Node有两个子类，对应于表达式结点的Expr和对应于语句结点的Stmt
class Node(object):
	"""Node"""
	
	labels = 0
	def __init__(self):
		super(Node, self).__init__()
		#为了报告错误lexline记录本结点对应的构造在源程序中的行号
		self.lexline = Lexer.line

	def error(self, s):
		raise Exception("error at line : %d, %s."%(self.lexline, s))

	def newlabel(self):
		self.labels = self.labels + 1
		return self.labels
	def emitlabel(self, i):
		print("L" + str(i) + ":")

	def emit(self, s):
		print("\t" + s)

#表达式构造被实现为Expr的子类，op和type分别表示一个结点上的运算符和类型
class Expr(Node):
	"""Expr"""
	def __init__(self, tok, ty):
		super(Expr, self).__init__()
		self.op 	= tok
		self.type	= ty
	#返回了一个项，该项可以作为一个三地址指令的右部
	#给定一个表达式E=E1+E2,gen返回一个项x1+x2，其中x1和x2分别存放E1和E2值的地址
	def gen(self):
		return self
	#把一个表达式计算成为一个单一的地址
	#也就是说，它返回一个常量、一个标识符、或者一个临时名字。给定表达式E，方法reduce
	#返回一个存放E的值的临时变量t
	def reduce(self):
		return self
	#布尔表达式B的跳转代码由方法jumping生成，t和f分辨称为表达式B的true出口和false出口
	#如果B的值为真，代码中就包含一个目标为t的跳转指令，如果B的值为假，就有一个目标为f
	#的指令。按照惯例，特殊标号0表示控制流从B穿越，到达B的代码之后的下一条指令
	def jumping(self, t, f):
		self.emitjumps(self.__str__(), t, f)

	def emitjumps(self, test, t, f):
		if t != 0 && f != 0:
			emit("if " + test + "goto L" + t)
			emit("goto L"+ f)
		elif t != 0 :
			emit("if " + test + "goto L" + t)
		elif f != 0:
			emit("iffalse " + test + "goto L" + f)
		
			
	def __str__(self):
		return str(self.op)

#标识符就是一个地址，类Id从类Expr中继承了gen和reduce的默认实现
#对应于一个标识符的类Id的结点是一个叶子结点
class Id(Expr):
	"""Id"""
	def __init__(self, id, ty, b):
		super(Id, self).__init__(id, ty)
		#offset保存了这个标示符的相对位置
		self.offfset = b

		


#临时变量
class Temp(Expr):
	"""Temp"""
	count = 0
	def __init__(self, ty):
		#临时变量的类型参数
		super(Temp, self).__init__(Word.TEMP, ty)
		self.count = self.count + 1
		self.number = count
	def __str__(self):
		return "t" + str(self.number)

		
#运算符的父类，子类包括表示算数运算符的子类Arith、表示单目运算符的子类
#Unary、表示数组访问的子类Access	
class Op(Expr):
	"""Op"""
	def __init__(self, tok, ty):
		super(Op, self).__init__(tok, ty)
	
	def reduce(self):
		Expr x = self.gen()
		Temp t = Temp(self.type)
		self.emit(str(t) + " = " + str(x))
		return t


#算数运算符，实现双目运算	
class Arith(Op):
	"""Arith"""
	def __init__(self, tok, x1, x2):
		super(Arith, self).__init__(tok, None)
		self.tok = tok
		self.exp1 = x1
		self.exp2 = x2
		self.type = Type.max(exp1.type, exp2.type)
		if self.type == None:
			self.error("type error")

	def gen(self):
		return Arith(self.op, exp1.reduce(), exp2.reduce())
		
	def __str__(self):
		return str(self.exp1) + " " + str(self.op) + " " + str(self.exp2)

class Unary(Op):
	"""Unary"""
	def __init__(self, tok, expr):
		super(Unary, self).__init__(tok, None)
		self.expr = expr
		self.type = Type.max(Type.INT, expr.Type)
		if self.type == None:
			self.error("type error")

	def gen(self):
		return Unary(op, expr.reduce())

	def __str__(self):
		return str(self.op) + " " + str(self.expr)
		

#数组访问
class Access(Op):
	"""Access"""
	def __init__(self, id, exp, ty):
		super(Access, self).__init__(Word("[]", Tag.INDEX), ty)
		self.array = id
		self.index = exp

	def gen(self):
		return Access(self.array, self.index.reduce(), self.type)

	def jumping(self, t, f):
		self.emitjumps(str(self.reduce()), t, f)

	def __str__(self):
		return str(self.array) + "[" + str(self.index) + "]"


class Constant(Expr):
	"""Constant"""
	TRUE 	= Constant(Word.TRUE, Type.BOOL)
	FALSE 	= Constant(Word.FALSE, Type.BOOL)

	def __init__(self, tok, ty):
		super(Constant, self).__init__(tok, ty)
	
	def __init__(self, i):
		super(Constant, self).__init__(Num(i), Type.INT)
	
	def jumping(self, t, f):
		if self == self.TRUE and t != 0:
			self.emit("goto L" + t)
		elif self == self.FALSE and f != 0:
			self.emit("goto L" + f)

		
#类Logical为类Or、And和Not提供一些常见的功能
class Logical(Expr):
	"""Logical"""
	def __init__(self, tok, x1, x2):
		super(Logical, self).__init__(tok, None)
		self.exp1 = x1
		self.exp2 = x2
		self.type = self.check(x1.type, x2.type)
		if self.type == None:
			error("type error")

	def check(self, ty1, typ2):
		if ty1 == Type.BOOL and ty2 == Type.BOOL:
			return Type.BOOL
		return None

	def gen(self):
		f = self.newlabel()
		a = self.newlabel()
		temp = Temp(self.type)
		self.jumping(0, f)
		self.emit(str(temp) + " = true")
		self.emit("goto L" + str(a))
		self.emitlabel(f)
		self.emit(str(temp) + " = false")
		self.emit(a)
		return temp

	def __str__(self):
		return str(exp1) + " " + str(self.op) + " " + str(exp2)

class And(Logical):
	"""And"""
	def __init__(self, tok, x1, x2):
		super(And, self).__init__(tok, x1, x2)
	
	def jumping(self, t, f):
		label = 0
		if f != 0:
			label = f
		else:
			label = self.newlabel()
		self.exp1.jumping(0, label)	
		self.exp2.jumping(t, f)
		if f == 0:
			self.emitlabel(label)

class Or(Logical):
	"""Or"""
	def __init__(self, tok, x1, x2):
		super(Or, self).__init__(tok, x1, x2)
	
	def jumping(self, t, f):
		label = 0
		if t != 0:
			label = t
		else:
			label = self.newlabel()
		self.exp1.jumping(label, 0)
		self.exp2.jumping(t, f)
		if t == 0:
			emitlabel(label)

class Not(Logical):
	"""Not"""
	def __init__(self, tok, x2):
		super(Not, self).__init__(tok, x2, x2)
	
	def jumping(self, t, f):
		self.exp2.jumping(f, t)

	def __str__(self):
		return str(self.op) + " " + str(self.exp2)


class Rel(Logical):
	"""Rel"""
	def __init__(self, tok, x1, x2):
		super(Rel, self).__init__(tok, x1, x2)
	
	def jumping(self, t, f):
		a = exp1.reduce()
		b = exp2.reduce()
		test = str(a) + " " + str(self.op) + " " + str(b)
		self.emitjumps(test, t, f) 
		
#每个语句构造被实现为Stmt的一个子类，一个构造的组成部分对应的字段是相应
#子类的对象
class Stmt(Node):
	"""Stmt"""
	Null = Stmt()
	Enclosing = Stmt.Null
	def __init__(self):
		super(Stmt, self).__init__()
		#标号a存在在字段after，当任何内层的break语句要跳出这个外层构造时
		#就可以使用这些标号
		self.after = 0
	#b标记这个语句的代码的开始处，a标记这个语句的代码之后的第一条指令
	def gen(b, a):
		pass

class If(Stmt):
	"""If"""
	def __init__(self, expr, stmt):
		super(If, self).__init__()
		self.expr = expr
		self.stmt = stmt
		if expr.type != Type.BOOL:
			expr.error("boolean required in if")

	def gen(b, a):
		label = self.newlabel()
		self.expr.jumping(0,a)
		self.emitlabel(label)
		self.stmt.gen(label, a)

class Else(Stmt):
	"""Else"""
	def __init__(self, expr, stmt1, stmt2):
		super(Else, self).__init__()
		self.expr = expr
		self.stmt1 = stmt1
		self.stmt2 = stmt2
		if expr.type != Type.BOOL:
			expr.error("boolean required in if")

	def gen(b, a):
		label1 = self.newlabel()
		label2 = self.newlabel()
		self.expr.jumping(0, label2)
		self.emitlabel(label1)
		self.stmt1.gen(label1, a)
		self.emit("goto L" + a)
		self.emitlabel(label2)
		self.stmt2.gen(label2, a)

class While(Stmt):
	"""While"""
	def __init__(self):
		super(While, self).__init__()
		self.expr = None
		self.stmt = None

	def init(self, expr, stmt):
		self.expr = expr
		self.stmt = stmt
		if expr.type != Type.BOOL:
			expr.error("boolean required in while")
	def gen(self, b, a):
		self.after = a
		self.expr.jumping(0,a)
		label = self.newlabel()
		self.emitlabel(label)
		self.stmt.gen(label, b)
		self.emit("goto L" + str(b))

					


class Do(Stmt):
	"""Do"""
	def __init__(self):
		super(Do, self).__init__()
		self.expr = None
		self.stmt = None

	def init(expr, stmt):
		self.expr = expr
		self.stmt = stmt

	def gen(b, a):
		self.after = a
		label = self.newlabel()
		self.stmt.gen(b, label)
		self.emitlabel(label)
		self.expr.jumping(b, 0)

#类Set实现了左部为标识符且右部为一个表达式的赋值语句
class Set(Stmt):
	"""Set"""
	def __init__(self, id, expr):
		super(Set, self).__init__()
		self.id = id
		self.expr = expr
		if self.check(self.id.type, self.expr.type) == None:
			self.error("type error")

	def check(self, p1, p2):
		if Type.numeric(p1) and Type.numeric(p2):
			return p2
		elif p1 == Type.BOOL and p2 == Type.BOOL:
			return p2
		else:
			return None

	def gen(self, b, a):
		self.emit(str(self.id) + " = " + str(self.expr))
		
#类SetElem实现了对数组元素的赋值
class SetElem(Stmt):
	"""SetElem"""
	def __init__(self, access, expr):
		super(SetElem, self).__init__()
		self.array = access.array
		self.index = access.index
		self.expr = expr
		if self.check(access.type, expr.type) == None:
			self.error("type error")

	def check(self, p1, p2):
		if type(p1) == Array or type(p2) == Array:
			return None
		elif p1 == p2:
			return p2
		elif Type.numeric(p1) and Type.numeric(p2):
			return p2
		else:
			return None

	def gen(self, b, a):
		s1 = str(self.index.reduce())
		s2 = str(self.expr.reduce())
		self.emit(str(self.array) + " [ " + s1 + " ] = " + s2)
		

#类Seq实现一个语句序列
class Seq(Stmt):
	"""Seq"""
	def __init__(self, stmt1, stmt2):
		super(Seq, self).__init__()
		self.stmt1 = stmt1
		self.stmt2 = stmt2

	def gen(self, b, a):
		#空语句不会产生任何代码
		if self.stmt1 == Stmt.Null:
			self.stmt2.gen(b, a)
		elif self.stmt2 == Stmt.Null:
			self.stmt1.gen(b, a)
		else:
			label = self.newlabel()
			self.stmt1.gen(b, label)
			self.emitlabel(label)
			stmt2.gen(label,a)

class Break(Stmt):
	"""Break"""
	def __init__(self):
		super(Break, self).__init__()
		if Stmt.Enclosing == Stmt.Null:
			self.error("unenclosed break")
		#使用字段stmt保存它的外围语句构造（语法分析器保证Stmt.Enclosing表示了其
		#外围构造对应的语法树结点).一个Break对象的代码是一个目标为标号stmt.after
		#的跳转指令，这个标号标记了紧跟在stmt的代码之后的指令。
		self.stmt = Stmt.Enclosing

	def gen(self, b, a):
		self.emit("goto L" + str(self.stmt.after))