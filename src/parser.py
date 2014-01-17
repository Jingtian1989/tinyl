import type
import lexer
import inter


class Parser(object):
    """Parser"""

    def __init__(self, lexer):
        super(Parser, self).__init__()
        self.lexer = lexer #lexical analyzer for this parser
        self.look = None  #lookahead tagen
        self.top = None  #current or top symbol table
        self.used = 0       #storage used for declarations

        self.move()

    def move(self):
        self.look = self.lexer.scan()

    def error(self, s):
        raise Exception("error at line : %d, %s." % (self.lexer.line, s))

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
        self.top = type.Enviroment(self.top)
        self.decls()
        s = self.stmts()
        self.match("}")
        self.top = savedEnv
        return s

    def decls(self):
        while self.look == lexer.Tag.BASIC:
            ty = self.type()
            tok = self.look
            self.match(lexer.Tag.ID)
            self.match(';')
            id = inter.Id(tok, ty, self.used)
            self.top.put(tok, id)
            self.used = self.used + ty.width

    def type(self):
        ty = self.look
        self.match(lexer.Tag.BASIC)
        if self.look != '[':
            return ty
        else:
            return self.dims(ty)

    def dims(self, ty):
        self.match('[')
        tok = self.look
        self.match(lexer.Tag.NUM)
        self.match(']')
        if self.look.tag == '[':
            ty = self.dims(ty)
        return type.Array(tok.value, ty)

    def stmts(self):
        if self.look == '}':
            return inter.Stmt.Null
        else:
            return inter.Seq(self.stmt(), self.stmts())

    def stmt(self):
        if self.look.tag == ';':
            self.move()
            return inter.Stmt.Null

        elif self.look.tag == lexer.Tag.IF:
            self.match(lexer.Tag.IF)
            self.match('(')
            x = self.bool()
            self.match(')')
            s1 = self.stmt()
            if self.look.tag != lexer.Tag.ELSE:
                return inter.If(x, s1)
            self.match(lexer.Tag.ELSE)
            s2 = self.stmt()
            return inter.Else(x, s1, s2)

        elif self.look.tag == lexer.Tag.WHILE:
            whilenode = inter.While()
            savedStmt = inter.Stmt.Enclosing
            inter.Stmt.Enclosing = whilenode
            self.match(lexer.Tag.WHILE)
            self.match('(')
            x = self.bool()
            self.match(')')
            s1 = self.stmt()
            whilenode.init(x, s1)
            inter.Stmt.Enclosing = savedStmt
            return whilenode

        elif self.look.tag == lexer.Tag.DO:
            donode = inter.Do()
            savedStmt = inter.Stmt.Enclosing
            lexer.Stmt.Enclosing = donode
            self.match(lexer.Tag.DO)
            s1 = self.stmt()
            self.match(lexer.Tag.WHILE)
            self.match('(')
            x = self.bool()
            self.match(')')
            self.match(';')
            donode.init(s1, x)
            inter.Stmt.Enclosing = savedStmt
            return donode

        elif self.look.tag == lexer.Tag.BREAK:
            self.match(lexer.Tag.BREAK);
            self.match(';')
            return inter.Break()

        elif self.look.tag == '{':
            return self.block()

        else:
            return self.assign()

    def assign(self):
        stmt    = None
        tok     = self.look
        self.match(lexer.Tag.ID)
        aid     = self.top.get(tok)
        if aid == None:
            self.error(str(tok) + "undeclared")
        if self.look.tag == '=':
            self.move()
            stmt = inter.Set(aid, self.bool())
        else:
            x = self.offset(aid)
            self.match('=')
            stmt = inter.SetElem(x, self.bool())
        self.match(';')
        return stmt

    def bool(self):
        x = self.join()
        while self.look.tag == lexer.Tag.OR:
            tok = self.look
            self.move()
            x = inter.Or(tok, x, self.join())
        return x

    def join(self):
        x = self.equality()
        while self.look.tag == lexer.Tag.AND:
            tok = self.look
            self.move()
            x = inter.And(tok, x, self.equality())

    def equality(self):
        x = self.rel()
        while self.look.tag == lexer.Tag.EQ or self.look.tag == lexer.Tag.NE:
            tok = self.look
            self.move()
            x = inter.Rel(tok, x, self.rel())

    def rel(self):
        x = self.expr()
        if self.look.tag == '<' or self.look.tag == lexer.Tag.LE or self.look.tag == lexer.Tag.GE or self.look.tag == '>':
            tok = self.look
            self.move()
            return inter.Rel(tok, x, self.expr())

    def expr(self):
        x = self.term()
        while self.look.tag == '+' or self.look.tag == '-':
            tok = self.look.tok
            self.move()
            x = inter.Arith(tok, x, self.term())
        return x

    def term(self):
        x = self.unary()
        while self.look.tag == '*' or self.look.tag == '/':
            tok = self.look
            self.move()
            x = inter.Arith(tok, x, self.unary())

    def unary(self):
        if self.look.tag == '-':
            self.move()
            return inter.Unary(lexer.MINUS, self.unary())
        elif self.look.tag == '!':
            tok = self.look
            self.move()
            return inter.Not(tok, self.unary())
        else:
            return self.factor()

    def factor(self):
        x = None
        if self.look.tag == '(':
            self.move()
            x = self.bool()
            self.match('}')
            return x
        elif self.look.tag == lexer.Tag.NUM:
            x = inter.Constant(self.look, type.INT)
            self.move()
            return x
        elif self.look.tag == lexer.REAL:
            x = lexer.Real(self.look, type.FLOAT)
            self.move()
            return x
        elif self.look.tag == lexer.TRUE:
            x = inter.TRUE
            self.move()
            return x
        elif self.look.tag == lexer.Tag.FALSE:
            x = inter.FALSE
            self.move()
            return x
        elif self.look.tag == lexer.Tag.ID:
            aid = self.top.get(self.look)
            if aid == None:
                self.error(str(self.look) + "undeclared")
            self.move()
            if self.look.tag != '[':
                return aid
            else:
                return self.offset(aid)
        else:
            self.error("syntax error")
            return x

    def offset(self, id):
        ty = id.type
        self.match('[')
        i = self.bool()
        self.match(']')
        ty = type.of
        w = inter.Constant(i = ty.width)
        t1 = inter.Arith(lexer.Token('*'), i, w)
        loc = t1
        while self.look.tag == '[':
            self.match('[')
            i = self.bool()
            self.match(']')
            ty = ty.of
            w = inter.Constant(i = ty.width)
            t1 = inter.Arith(lexer.Token('*'), i, w)
            t2 = inter.Arith(lexer.Token('+'), loc, t1)
            loc = t2
        return inter.Access(id, loc, ty)


