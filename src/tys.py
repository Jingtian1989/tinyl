import lexer


class Type(lexer.Word):
    """Type"""
    @classmethod
    def numeric(clz, p):
        if p == CHAR or p == INT or p == FLOAT:
            return True
        return False

    @classmethod
    def max(clz, p1, p2):
        if clz.numeric(p1) == False or clz.numeric(p2) == False:
            return None
        elif p1 == FLOAT or p2 == FLOAT:
            return FLOAT
        elif p1 == INT or p2 == INT:
            return INT
        else:
            return CHAR

    def __init__(self, s, tag, w):
        super(Type, self).__init__(s, tag)
        self.width = w


class Array(Type):
    """Array"""

    def __init__(self, sz, p):
        super(Array, self).__init__("[]", lexer.Tag.INDEX, sz * p.width)
        #number of elements
        self.size = sz
        #array of type
        self.of = p

    def __str__(self):
        return "[" + str(self.size) + "]" + str(self.of)


class Enviroment(object):
    """Enviroment"""

    def __init__(self, prev):
        super(Enviroment, self).__init__()
        self.prev = prev
        self.table = dict()

    def put(self, tok, i):
        self.table[tok] = i

    def get(self, tok):
        e = self
        while e is not None:
            found = e.table.get(tok)
            if found is not None:
                return found
            e = e.prev
        return None

INT     = Type("int", lexer.Tag.BASIC, 4)
FLOAT   = Type("float", lexer.Tag.BASIC, 8)
CHAR    = Type("char", lexer.Tag.BASIC, 1)
BOOL    = Type("bool", lexer.Tag.BASIC, 1)

