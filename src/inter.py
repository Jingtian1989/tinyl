import lexer
import type

#AST node
from src.type import Type


class Node(object):
    """Node"""
    labels = 0

    def __init__(self):
        super(Node, self).__init__()
        #line number in source code
        self.lexline = lexer.Lexer.line

    def error(self, s):
        raise Exception("error at line : %d, %s." % (self.lexline, s))

    def newlabel(self):
        self.labels = self.labels + 1
        return self.labels

    def emitlabel(self, i):
        print("L" + str(i) + ":")

    def emit(self, s):
        print('\t' + s)

#experation construction
class Expr(Node):
    """Expr"""

    def __init__(self, tok, ty):
        super(Expr, self).__init__()
        #operator
        self.op = tok
        #type
        self.type = ty

    #return an node that represent the experation
    #ie.E=E1+E2, it returns a expertaoin x1+x2, that x1, x2 contains the value of the e1 and e2.
    def gen(self, b = None, a = None):
        return self

    #reduce a experatoin to a node, that contains the value of the experation
    #ie. E, it returns a temp that contains the value of E.
    def reduce(self):
        return self

    #generate jump code for boolean experation
    #t and f represent the labels of the true and false exits
    #the special label 0 represents that past the control flow of B, goto the next instruction behind B.
    def jumping(self, t, f):
        self.emitjumps(self.__str__(), t, f)

    def emitjumps(self, test, t, f):
        if t != 0 and f != 0:
            self.emit("if " + test + "goto L" + t)
            self.emit("goto L" + f)
        elif t != 0:
            self.emit("if " + test + "goto L" + t)
        elif f != 0:
            self.emit("iffalse " + test + "goto L" + f)


    def __str__(self):
        return str(self.op)

#identifier
class Id(Expr):
    """Id"""

    def __init__(self, id, ty, b):
        super(Id, self).__init__(id, ty)
        self.offfset = b


#temporary variable
class Temp(Expr):
    """Temp"""
    count = 0

    def __init__(self, ty):
        super(Temp, self).__init__(lexer.TEMP, ty)
        self.count = self.count + 1
        self.number = self.count

    def __str__(self):
        return "t" + str(self.number)


#the top class of arithmetic and array access operations
class Op(Expr):
    """Op"""

    def __init__(self, tok, ty):
        super(Op, self).__init__(tok, ty)

    def reduce(self):
        x = self.gen()
        t = Temp(self.type)
        self.emit(str(t) + " = " + str(x))
        return t


class Arith(Op):
    """Arith"""

    def __init__(self, tok, x1, x2):
        super(Arith, self).__init__(tok, None)
        self.tok = tok
        self.exp1 = x1
        self.exp2 = x2
        self.type = type.Type.max(x1.type, x2.type)
        if self.type == None:
            self.error("type error")

    def gen(self):
        return Arith(self.op, self.exp1.reduce(), self.exp2.reduce())

    def __str__(self):
        return str(self.exp1) + " " + str(self.op) + " " + str(self.exp2)


class Unary(Op):
    """Unary"""

    def __init__(self, tok, expr):
        super(Unary, self).__init__(tok, None)
        self.expr = expr
        self.type = type.Type.max(Type.INT, expr.Type)
        if self.type == None:
            self.error("type error")

    def gen(self):
        return Unary(self.op, self.expr.reduce())

    def __str__(self):
        return str(self.op) + " " + str(self.expr)


#array access
class Access(Op):
    """Access"""

    def __init__(self, id, exp, ty):
        super(Access, self).__init__(lexer.Word("[]", lexer.Tag.INDEX), ty)
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
    def __init__(self, i = None, tok = None, ty = None):
        if i == None:
            super(Constant, self).__init__(tok, ty)
        else:
            super(Constant, self).__init__(lexer.Num(i), Type.INT)

    def jumping(self, t, f):
        if self == TRUE and t != 0:
            self.emit("goto L" + t)
        elif self == FALSE and f != 0:
            self.emit("goto L" + f)

TRUE    = Constant(tok = lexer.TRUE, ty = type.BOOL)
FALSE   = Constant(tok = lexer.FALSE, ty = type.BOOL)

#the top class of logical operations
class Logical(Expr):
    """Logical"""

    def __init__(self, tok, x1, x2):
        super(Logical, self).__init__(tok, None)
        self.exp1 = x1
        self.exp2 = x2
        self.type = self.check(x1.type, x2.type)
        if self.type == None:
            self.error("type error")

    def check(self, ty1, ty2):
        if ty1 == type.BOOL and ty2 == type.BOOL:
            return type.BOOL
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
        return str(self.exp1) + " " + str(self.op) + " " + str(self.exp2)


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
            self.emitlabel(label)


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
        a = self.exp1.reduce()
        b = self.exp2.reduce()
        test = str(a) + " " + str(self.op) + " " + str(b)
        self.emitjumps(test, t, f)


    #the top class of statement constructoin



class Stmt(Node):
    """Stmt"""
    def __init__(self):
        super(Stmt, self).__init__()
        #the label number after the stmt, used for control flow
        self.after = 0

    def gen(b, a):
        pass

Null = Stmt()
Enclosing = Null

class If(Stmt):
    """If"""

    def __init__(self, expr, stmt):
        super(If, self).__init__()
        self.expr = expr
        self.stmt = stmt
        if expr.type != Type.BOOL:
            expr.error("boolean required in if")

    def gen(self, b, a):
        label = self.newlabel()
        self.expr.jumping(0, a)
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

    def gen(self, b, a):
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
        if expr.type != type.BOOL:
            expr.error("boolean required in while")

    def gen(self, b, a):
        self.after = a
        self.expr.jumping(0, a)
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

    def init(self, expr, stmt):
        self.expr = expr
        self.stmt = stmt

    def gen(self, b, a):
        self.after = a
        label = self.newlabel()
        self.stmt.gen(b, label)
        self.emitlabel(label)
        self.expr.jumping(b, 0)

#assign statement for 'identifier = experation'
class Set(Stmt):
    """Set"""

    def __init__(self, id, expr):
        super(Set, self).__init__()
        self.id = id
        self.expr = expr
        if self.check(id.type, expr.type) == None:
            self.error("type error")

    def check(self, p1, p2):
        if type.Type.numeric(p1) and type.Type.numeric(p2):
            return p2
        elif p1 == type.BOOL and p2 == type.BOOL:
            return p2
        else:
            return None

    def gen(self, b, a):
        self.emit(str(self.id) + " = " + str(self.expr))

#assign statement for array assign
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
        if type(p1) == type.Array or type(p2) == type.Array:
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


#statement sequence
class Seq(Stmt):
    """Seq"""

    def __init__(self, stmt1, stmt2):
        super(Seq, self).__init__()
        self.stmt1 = stmt1
        self.stmt2 = stmt2
    #null statement do not generate instructions
    def gen(self, b, a):
        if self.stmt1 == Null:
            self.stmt2.gen(b, a)
        elif self.stmt2 == Null:
            self.stmt1.gen(b, a)
        else:
            label = self.newlabel()
            self.stmt1.gen(b, label)
            self.emitlabel(label)
            self.stmt2.gen(label, a)


class Break(Stmt):
    """Break"""

    def __init__(self):
        super(Break, self).__init__()
        if Enclosing == Null:
            self.error("unenclosed break")
            #keep track of the outer ring
        self.stmt = Enclosing

    def gen(self, b, a):
        self.emit("goto L" + str(self.stmt.after))