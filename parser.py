import ply.yacc as yacc
import pandas as pd
from numpy import integer, floating
import os

from lexer import tokens

tables = {}

def pretty_print(df):
    sizes = [max(len(col), df[col].apply(lambda x: len(str(x))).max()) for col in df.columns]
        
    print(end='+')
    for size in sizes:
        print('-' * (size + 2), end='+')
    print()

    print(end='|')
    for col, size in zip(df.columns, sizes):
        print(end=' ')
        print(col.ljust(size), end='')
        print(end=' |')
    print()

    print(end='+')
    for size in sizes:
        print('-' * (size + 2), end='+')
    print()

    for i in df.index:
        row = df.loc[i]
        print(end='|')
        for col, size in zip(df.columns, sizes):
            print(end=' ')
            val = row[col]
            if isinstance(val, (int, float, integer, floating)):
                print(str(row[col]).rjust(size), end='')
            else:
                print(str(row[col]).ljust(size), end='')
            print(end=' |')
        print()
    
    print(end='+')
    for size in sizes:
        print('-' * (size + 2), end='+')
    print()


def p_start(p):
    'start : statement SEMICOLON'
    pass


def p_datatype(p):
    '''datatype : VARCHAR
                | INT
                | FLOAT'''
    if p[1] == 'int':
        p[0] = int
    elif p[1] == 'float':
        p[0] = float
    elif p[1] == 'varchar':
        p[0] = str

def p_literal(p):
    '''literal : INT_NUMBER
               | FLOAT_NUMBER
               | STRING'''
    p[0] = p[1]


def p_show_tables(p):
    'statement : SHOW TABLES'
    if tables:
        pretty_print(pd.DataFrame({'Tables': list(tables.keys())}))
    else:
        print('Empty set')


def p_create_table(p):
    'statement : CREATE TABLE ID LPAREN create_table_col_list RPAREN'
    if p[3] in tables:
        print(f'ERROR: Table \'{p[3]}\' already exists')
    else:
        tables[p[3]] = pd.DataFrame(columns=p[5].keys()).astype(p[5])
        print('Query OK, 0 rows affected\n')

def p_create_table_if_not_exists(p):
    'statement : CREATE TABLE IF NOT EXISTS ID LPAREN create_table_col_list RPAREN'
    if p[6] not in tables:
        tables[p[6]] = pd.DataFrame(columns=p[8].keys()).astype(p[8])
        print('Query OK, 0 rows affected\n')
    else:
        print('Query OK, 0 rows affected, 1 warning\n')

def p_create_table_col_list(p):
    '''create_table_col_list : create_table_col_list COMMA ID datatype
                             | ID datatype'''
    if p[2] != ',':
        p[0] = {p[1]: p[2]}
    else:
        p[1][p[3]] = p[4]
        p[0] = p[1]


def p_drop_table(p):
    'statement : DROP TABLE ID'
    if p[3] in tables:
        p[0] = tables.pop(p[3])
        print('Query OK, 0 rows affected\n')
    else:
        print(f'Error: Unknown table \'{p[3]}\'')


def p_insert(p):
    'statement : INSERT INTO ID VALUES insert_val_row_list'
    if p[3] in tables:
        df = tables[p[3]]
        dtypes = df.dtypes
        for row in p[5]:
            df.loc[len(df.index)] = row
        tables[p[3]] = df.astype(dtypes)
        print(f'Query OK, {len(p[5])} rows affected\n')
    else:
        print(f'Error: Table \'{p[3]}\' doesn\'t exist')

def p_insert_val_row_list(p):
    '''insert_val_row_list : insert_val_row_list COMMA LPAREN insert_val_list RPAREN
                           | LPAREN insert_val_list RPAREN'''
    if p[2] != ',':
        p[0] = [p[2]]
    else:
        p[1].append(p[4])
        p[0] = p[1]

def p_insert_val_list(p):
    '''insert_val_list : insert_val_list COMMA literal
                       | literal'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]


def p_select(p):
    '''statement : SELECT STAR FROM ID
                 | SELECT select_col_list FROM ID
                 | SELECT STAR FROM ID WHERE condition
                 | SELECT select_col_list FROM ID WHERE condition'''

    if p[4] not in tables:
        print(f'Error: Table \'{p[4]}\' doesn\'t exist')
        return
    
    df = tables[p[4]]

    if len(p) > 5:
        df = df[df.apply(p[6], axis=1)]

    if p[2] != '*':
        df = df[p[2]]

    if not len(df.index):
        print("Empty set")
    else:
        pretty_print(df)
        print(f'{len(df.index)} rows in set\n')

def p_select_col_list(p):
    '''select_col_list : select_col_list COMMA ID
                       | ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]


def p_update(p):
    '''statement : UPDATE ID SET update_collist
                 | UPDATE ID SET update_collist WHERE condition'''
    if p[2] not in tables:
        print(f'Error: Table \'{p[2]}\' doesn\'t exist')
        return
    
    c = 0
    df = tables[p[2]]
    for i in df.index:
        if len(p) == 7 and not p[6](df.loc[i]):
            continue
        for col in p[4]:
            df.loc[i, col] = p[4][col]
        c += 1
    tables[p[2]] = df
    print(f"Query OK, {c} rows affected\n")

def p_update_collist(p):
    '''update_collist : update_collist COMMA ID EQ expression
                      | ID EQ expression'''
    if len(p) == 4:
        p[0] = {p[1]: p[3](None)}
    elif len(p) == 6:
        p[1][p[3]] = p[5](None)
        p[0] = p[1]


def p_delete_from(p):
    '''statement : DELETE FROM ID
                 | DELETE FROM ID WHERE condition'''
    if p[3] not in tables:
        print(f'Error: Table \'{p[3]}\' doesn\'t exist')
        return
    
    df = tables[p[3]]
    c = df.shape[0]
    if len(p) == 6:
        df = df[~df.apply(p[5], axis=1)]
    else:
        df.drop(df.index, inplace=True)
    tables[p[3]] = df
    c -= df.shape[0]
    print(f"Query OK, {c} rows affected\n")


def p_condition(p):
    '''condition : condition OR cond_term
                 | cond_term'''
    q = p[:]
    if len(q) == 2:
        p[0] = lambda row: q[1](row)
    elif len(q) == 4:
        p[0] = lambda row: q[1](row) or q[3](row)

def p_cond_term(p):
    '''cond_term : cond_term AND cond
                 | cond'''
    q = p[:]
    if len(q) == 2:
        p[0] = lambda row: q[1](row)
    elif len(q) == 4:
        p[0] = lambda row: q[1](row) and q[3](row)

def p_cond(p):
    '''cond : expression EQ expression
            | expression NE expression
            | expression LE expression
            | expression GE expression
            | expression LT expression
            | expression GT expression'''
    q = p[:]
    if q[2] == '=':
        p[0] = lambda row: q[1](row) == q[3](row)
    elif q[2] == '<>':
        p[0] = lambda row: q[1](row) != q[3](row)
    elif q[2] == '<=':
        p[0] = lambda row: q[1](row) <= q[3](row)
    elif q[2] == '>=':
        p[0] = lambda row: q[1](row) >= q[3](row)
    elif q[2] == '<':
        p[0] = lambda row: q[1](row) < q[3](row)
    elif q[2] == '>':
        p[0] = lambda row: q[1](row) > q[3](row)

def p_cond_paren(p):
    'cond : LPAREN condition RPAREN'
    q = p[:]
    p[0] = lambda row: q[2](row)


def p_expression_plus(p):
    'expression : expression PLUS term'
    q = p[:]
    p[0] = lambda row: q[1](row) + q[3](row)

def p_expression_minus(p):
    'expression : expression MINUS term'
    q = p[:]
    p[0] = lambda row: q[1](row) - q[3](row)

def p_expression_term(p):
    'expression : term'
    q = p[:]
    p[0] = lambda row: q[1](row)

def p_term_times(p):
    'term : term STAR factor'
    q = p[:]
    p[0] = lambda row: q[1](row) * q[3](row)

def p_term_div(p):
    'term : term DIVIDE factor'
    q = p[:]
    p[0] = lambda row: q[1](row) / q[3](row)

def p_term_factor(p):
    'term : factor'
    q = p[:]
    p[0] = lambda row: q[1](row)

def p_factor_int(p):
    'factor : INT_NUMBER'
    q = p[:]
    p[0] = lambda row: int(q[1])

def p_factor_float(p):
    'factor : FLOAT_NUMBER'
    q = p[:]
    p[0] = lambda row: float(q[1])

def p_factor_str(p):
    'factor : STRING'
    q = p[:]
    p[0] = lambda row: str(q[1])

def p_factor_col(p):
    'factor : ID'
    q = p[:]
    p[0] = lambda row: row.get(q[1])

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    q = p[:]
    p[0] = lambda row: q[2](row)


def p_error(p):
    print(p)
    print('You have an error in your SQL syntax')

parser = yacc.yacc()


if os.name == 'nt':
    os.system('cls')
elif os.name == 'posix':
    os.system('clear')

while True:
    try:
        if not (s := input("mysql> ").strip()):
            continue
        while not s or s[-1] != ';':
            s += ' ' + input("    -> ").strip()
    except EOFError:
        break
    parser.parse(s)
