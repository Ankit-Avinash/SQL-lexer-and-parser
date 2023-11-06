import ply.lex as lex

tokens = (
    'FLOAT_NUMBER',
    'INT_NUMBER',
    'STRING',

    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',

    'LPAREN',
    'RPAREN',

    'EQ',
    'NE',
    'LE',
    'GE',
    'LT',
    'GT',

    'COMMA',
    'STAR',

    'AND',
    'OR',

    'SEMICOLON',
    'COMMENT',

    'ID',
)

reserved = {
    'databases': 'DATABASES',
    'database': 'DATABASE',
    'tables': 'TABLES',
    'table': 'TABLE',

    'show': 'SHOW',
    'create': 'CREATE',
    'drop': 'DROP',
    'use': 'USE',
    'desc': 'DESC',
    'insert': 'INSERT',
    'into': 'INTO',
    'delete': 'DELETE',
    'from': 'FROM',
    'select': 'SELECT',
    'update': 'UPDATE',

    'unique': 'UNIQUE',
    'primary': 'PRIMARY',
    'key': 'KEY',
    'default': 'DEFAULT',
    'check': 'CHECK',

    'not': 'NOT',
    'and': 'AND',
    'or': 'OR',

    'if': 'IF',
    'exists': 'EXISTS',
    'values': 'VALUES',
    'from': 'FROM',
    'distinct': 'DISTINCT',
    'all': 'ALL',
    'where': 'WHERE',
    'set': 'SET',
    'in': 'IN',
    'is': 'IS',

    'char': 'CHAR',
    'varchar': 'VARCHAR',
    'int': 'INT',
    'float': 'FLOAT',
    'null': 'NULL'
}

tokens += tuple(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
t_DIVIDE = r'/'

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_EQ = r'='
t_NE = r'<>'
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'

t_AND = r'&&'
t_OR = r'\|\|'

t_COMMA = r','

t_SEMICOLON = r';'
t_ignore_COMMENT = r'--.*\n|/\*[\s\S]*?\*/'

def t_FLOAT_NUMBER(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r"'[a-zA-Z_][a-zA-Z_0-9]*'"
    t.value = str(t.value[1:-1])
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(),'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore  = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()


if __name__ == '__main__':
    data = '''
    -- blah blah blah
    select * from student where age >= 10.5 age <= 20;
    '''

    lexer.input(data)

    for tok in lexer:
        print(tok)