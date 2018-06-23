from errors import *

env = {}

class Node:
    def __init__(self): pass
    def evaluate(self): return 0
    def execute(self): return 0

# EXPRESSION NODES
class NumberNode(Node):
    def __init__(self, v):
        if('.' in v): self.value = float(v)
        else: self.value = int(v)

    def evaluate(self): return self.value

class StringNode(Node):
    def __init__(self, v):
        self.value = str(v)
        self.value = self.value.strip("\"")

    def evaluate(self): return self.value

class ListNode(Node):
    def __init__(self, v): self.value = v

    def evaluate(self): #evaluate each item in list
        for i in range(0, len(self.value)):
            self.value[i] = self.value[i].evaluate()
        return self.value

class NameNode(Node):
    def __init__(self, v): self.value = v

    def evaluate(self): return env[self.value]

class IndexNode(Node):
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def evaluate(self): return self.v1.evaluate()[self.v2.evaluate()]

class ParensNode(Node):
    def __init__(self, v1): self.v1 = v1
    def evaluate(self): return self.v1.evaluate()

class BopNode(Node):
    def __init__(self, op, v1, v2):
        self.v1 = v1
        self.v2 = v2
        self.op = op

    def evaluate(self):
        self.checkTypeSemantics()
        if (self.op == '+'): return self.v1.evaluate() + self.v2.evaluate()
        elif (self.op == '-'): return self.v1.evaluate() - self.v2.evaluate()
        elif (self.op == '*'): return self.v1.evaluate() * self.v2.evaluate()
        elif (self.op == '/'): return self.v1.evaluate() / self.v2.evaluate()
        elif (self.op == '%'): return self.v1.evaluate() % self.v2.evaluate()
        elif (self.op == '**'): return self.v1.evaluate() ** self.v2.evaluate()
        elif (self.op == '//'): return self.v1.evaluate() // self.v2.evaluate()
        elif (self.op == 'in'): return 1 if self.v1.evaluate() in self.v2.evaluate() else 0
        elif (self.op == '<='): return 1 if self.v1.evaluate() <= self.v2.evaluate() else 0
        elif (self.op == '<'): return 1 if self.v1.evaluate() < self.v2.evaluate() else 0
        elif (self.op == '<>'): return 1 if self.v1.evaluate() != self.v2.evaluate() else 0
        elif (self.op == '>'): return 1 if self.v1.evaluate() > self.v2.evaluate() else 0
        elif (self.op == '>='): return 1 if self.v1.evaluate() >= self.v2.evaluate() else 0
        elif (self.op == '=='): return 1 if self.v1.evaluate() == self.v2.evaluate() else 0
        elif (self.op == 'and'): return 1 if self.v1.evaluate() != 0 and self.v2.evaluate() else 0
        elif (self.op == 'or'): return 1 if self.v1.evaluate() != 0 or self.v2.evaluate() else 0

    def checkTypeSemantics(self):
        if self.op == '-' or self.op == '*' or self.op == '/' or self.op == '%' or self.op == '**' or self.op == '//' \
        or self.op == '<=' or self.op == '<' or self.op == '<>' or self.op == '>' or self.op == '>=' or self.op == '==':
            if not (isinstance(self.v1.evaluate(), int) or isinstance(self.v1.evaluate(), float)) or \
            not (isinstance(self.v2.evaluate(), int) or isinstance(self.v2.evaluate(), float)):
                raise SemanticError
        if self.op == 'and' or self.op == 'or':
            if not (isinstance(self.v1.evaluate(), int)) or not (isinstance(self.v2.evaluate(), int)):
                raise SemanticError

class UopNode(Node):
    def __init__(self, op, v1):
        self.v1 = v1
        self.op = op

    def evaluate(self):
        self.checkTypeSemantics()
        if (self.op == 'not'):
            return 1 if not self.v1.evaluate() else 0

    def checkTypeSemantics(self):
        if self.op == 'not':
            if not (isinstance(self.v1.evaluate(), int)):
                raise SemanticError

# STATEMENT NODES
class PrintNode(Node):
    def __init__(self, v): self.value = v
    def evaluate(self): return self.value
    def execute(self):
        expression = self.value.evaluate()
        print(expression)

class AssignNode(Node):
    def __init__(self, v1, v2, v3):
        self.v1 = v1 # name node
        self.v2 = v2
        self.v3 = v3 # optional index

    def execute(self):
        if self.v3 != None: env[self.v1.value][self.v2.evaluate()] = self.v3.evaluate()
        else: env[self.v1.value] = self.v2.evaluate()
        #print(env)

class BlockNode(Node):
    def __init__(self, v): self.value = v
    def execute(self):
        if len(self.value) != []: # if no statements ie {}
            for statement in self.value:
                statement.execute()

class WhileNode(Node):
    def __init__(self, v1, v2):
        self.v1 = v1 # expression
        self.v2 = v2 # block

    def execute(self):
        counter = 0
        while self.v1.evaluate() != 0:
            self.v2.execute()
            counter+=1

class ConditionalNode(Node):
    def __init__(self, v1, v2):
        self.v1 = v1 # if node
        self.v2 = v2 # else node

    def execute(self):
        if self.v1.evaluate() == True:
            self.v1.execute()
        else:
            if self.v2 != None:
                self.v2.execute()

class IfNode(Node):
    def __init__(self, v1, v2):
        self.v1 = v1 # expression
        self.v2 = v2 # block
        
    def evaluate(self):
        if self.v1.evaluate() != 0: return True
        else: return False
    def execute(self): self.v2.execute()

class ElseNode(Node):
    def __init__(self, v1): self.v1 = v1 # block
    def execute(self): self.v1.execute()