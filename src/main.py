import ply.lex as lex
import ply.yacc as yacc
import sys

from nodes import *

reserved = {
   'in'     : 'IN',
   'not'    : 'NOT',
   'and'    : 'AND',
   'or'     : 'OR',
   'print'  : 'PRINT',
   'if'     : 'IF',
   'else'   : 'ELSE',
   'while'  : 'WHILE'
}

tokens = [
    # types
    'NUMBER',
    'STRING',
    # operators
    'MULTIPLY',
    'DIVIDE',
    'MODULUS',
    'POWER',
    'FLOOR_DIVIDE',
    'PLUS',
    'MINUS',
    'LESS_THAN_OR_EQUAL',
    'LESS_THAN',
    'NOT_EQUAL',
    'GREATER_THAN_OR_EQUAL',
    'GREATER_THAN',
    'EQUAL_EQUAL',
    'EQUALS',
    # symbols
    'LEFT_PARENTHESIS',
    'RIGHT_PARENTHESIS',
    'LEFT_BRACKET',
    'RIGHT_BRACKET',
    'LEFT_BRACE',
    'RIGHT_BRACE',
    'COMMA',
    'SEMI_COLON',
    #words
    'NAME'
] + list(reserved.values())

t_LEFT_PARENTHESIS = r'\('
t_RIGHT_PARENTHESIS = r'\)'
t_LEFT_BRACKET = r'\['
t_RIGHT_BRACKET = r'\]'
t_LEFT_BRACE = r'\{'
t_RIGHT_BRACE = r'\}'
t_COMMA = r'\,'
t_SEMI_COLON = r'\;'
t_PLUS  = r'\+'
t_MINUS = r'\-'
t_POWER = r'\*\*'
t_MULTIPLY = r'\*'
t_FLOOR_DIVIDE = r'\/\/'
t_DIVIDE = r'\/'
t_MODULUS = r'\%'
t_LESS_THAN_OR_EQUAL = r'<='
t_LESS_THAN = r'<'
t_NOT_EQUAL = r'<>'
t_GREATER_THAN_OR_EQUAL = r'>='
t_GREATER_THAN = r'>'
t_EQUAL_EQUAL = r'=='
t_EQUALS = r'='

t_ignore = ' \t\n'

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = StringNode(t.value)
    return t

def t_NUMBER(t):
    r'-?\d*(\d\.|\.\d)\d* | \d+'
    try: t.value = NumberNode(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

def t_NAME(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t

def t_error(t): raise SyntaxError

# passing to the parser
lexer = lex.lex()

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NOT'),
    ('left', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'NOT_EQUAL', 'GREATER_THAN_OR_EQUAL', 'GREATER_THAN', 'EQUAL_EQUAL'),
    ('left', 'IN'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'FLOOR_DIVIDE'),
    ('left', 'POWER'),
    ('left', 'MODULUS'),
    ('left', 'MULTIPLY', 'DIVIDE')
)

def p_start(p):
    '''
    start : block
    '''
    p[1].execute()

def p_statement_block(p):
    '''
    block : LEFT_BRACE statements RIGHT_BRACE
    '''
    p[0] = BlockNode(p[2])

def p_statement(p):
    '''
    statement : loop
              | conditional
              | block
              | assign
              | print
    '''
    p[0] = p[1]

def p_empty_statement(p):
    '''
    statements : empty
    '''
    p[0] = []

def p_single_statement(p):
    '''
    statements : statement
    '''
    p[0] = [p[1]]
def p_many_statements(p):
    '''
    statements : statements statement
    '''
    p[0] = p[1] + [p[2]]

def p_conditional_statement(p):
    '''
    conditional : if_statement
                | if_statement else_statement
    '''
    if len(p) == 2: p[0] = ConditionalNode(p[1], None) # if only
    else: p[0] = ConditionalNode(p[1], p[2])

def p_if_statement(p): # not block bc single statements
    '''
    if_statement : IF LEFT_PARENTHESIS expression RIGHT_PARENTHESIS statement
    '''
    p[0] = IfNode(p[3], p[5])

def p_else_statement(p):
    '''
    else_statement : ELSE statement
    '''
    p[0] = ElseNode(p[2])

def p_while_statement(p):
    '''
    loop : WHILE LEFT_PARENTHESIS expression RIGHT_PARENTHESIS statement
    '''
    p[0] = WhileNode(p[3], p[5])

def p_assign_statement(p):
    '''
    assign : NAME EQUALS expression SEMI_COLON
           | NAME LEFT_BRACKET expression RIGHT_BRACKET EQUALS expression SEMI_COLON
    '''
    p[1] = NameNode(p[1])
    if len(p) == 5: p[0] = AssignNode(p[1], p[3], None) # assign a variable
    else: p[0] = AssignNode(p[1], p[3], p[6]) # assign index in a list

def p_print_statement(p):
    '''
    print : PRINT LEFT_PARENTHESIS expression RIGHT_PARENTHESIS SEMI_COLON
    '''
    p[0] = PrintNode(p[3])

def p_parenthesis_expression(p):
    '''
    expression : LEFT_PARENTHESIS expression RIGHT_PARENTHESIS
    '''
    p[0] = ParensNode(p[2])

def p_index_expression(p):
    '''
    expression : expression LEFT_BRACKET expression RIGHT_BRACKET
    '''
    p[0] = IndexNode(p[1], p[3])

def p_binary_operation(p):
    '''
    expression : expression MULTIPLY expression
               | expression DIVIDE expression
               | expression MODULUS expression
               | expression POWER expression
               | expression FLOOR_DIVIDE expression
               | expression PLUS expression
               | expression MINUS expression
               | expression IN expression
               | expression LESS_THAN expression
               | expression LESS_THAN_OR_EQUAL expression
               | expression NOT_EQUAL expression
               | expression GREATER_THAN expression
               | expression GREATER_THAN_OR_EQUAL expression
               | expression EQUAL_EQUAL expression
               | expression AND expression
               | expression OR expression

    '''
    p[0] = BopNode(p[2], p[1], p[3])

def p_unary_operation(p):
    '''
    expression : NOT expression
    '''
    p[0] = UopNode('not', p[2])

def p_list_empty(p):
    '''
    list : empty
    '''
    p[0] = []

def p_list_start(p):
    '''
    list : expression
    '''
    p[0] = [p[1]]    

def p_list_tail(p):
    '''
    list : list COMMA expression
    '''
    p[0] = p[1] + [p[3]]

def p_expression(p):
    '''
    expression : NAME
               | NUMBER
               | STRING
               | LEFT_BRACKET list RIGHT_BRACKET
    '''
    if len(p) != 4:
        if not (isinstance(p[1], NumberNode) or isinstance(p[1], StringNode)):
            p[0] = NameNode(p[1])
        else: p[0] = p[1] # not name node
    else: p[0] = ListNode(p[2]) # list

def p_error(p): raise SyntaxError

def p_empty(p):
    '''
    empty : 
    '''
    pass

def main(): #parse code
    if len(sys.argv) != 2: sys.exit("Expected exactly 1 input file as an argument")
    inputFile = open(str(sys.argv[1]), "r")
    parser = yacc.yacc()

    code = ""
    for line in inputFile: code += line
    try: parser.parse(code)
    except SyntaxError: print("Syntax Error")
    except (TypeError, ZeroDivisionError, IndexError, KeyError, SemanticError):
        print("Semantic Error")

    inputFile.close()

    # while True:
    # try: s = input('>> ')
    # except EOFError: break
    # try: parser.parse(s)
    # except SyntaxError: print("Syntax Error")
    # except (TypeError, ZeroDivisionError, IndexError, KeyError, SemanticError):
    #     print("Semantic Error")

main()