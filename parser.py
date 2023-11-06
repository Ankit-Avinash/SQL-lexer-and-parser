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
                 | SELECT select_col_list FROM ID'''
    if p[4] in tables:
        df = tables[p[4]]
        if p[2] == '*':
            pretty_print(df)
        else:
            pretty_print(df[p[2]])
        print(f'{len(df.index)} rows in set\n')
    else:
        print(f'Error: Table \'{p[4]}\' doesn\'t exist')

def p_select_col_list(p):
    '''select_col_list : select_col_list COMMA ID
                       | ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]


def p_error(p):
    print('You have an error in your SQL syntax')

parser = yacc.yacc()


os.system('cls')
while True:
    try:
        s = input('mysql> ')
    except EOFError:
        break
    if not s:
        continue
    parser.parse(s)
