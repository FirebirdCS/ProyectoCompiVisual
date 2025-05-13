# lexic.py

import ply.lex as lex

# Lista de tokens básicos
tokens = (
    'ID', 'NUMERO', 'FLOTANTE', 'CADENA',
    'MAS', 'MENOS', 'POR', 'DIVIDIDO', 'MODULO',
    'IGUAL', 'DIFERENTE', 'MENOR', 'MENOR_IGUAL', 'MAYOR', 'MAYOR_IGUAL',
    'Y', 'O', 'NEG',
    'ASIGNAR',
    'PARENTESIS_IZQUIERDO', 'PARENTESIS_DERECHO',
    'PUNTO_Y_COMA', 'COMA'
)

# Palabras reservadas de tu lenguaje
reserved = {
    'Algoritmo': 'ALGORITMO',
    'Fin':       'FIN',
    'Definir':   'DEFINIR',
    'Entero':    'ENTERO',
    'Inicio':    'INICIO',
    'Escribir':  'ESCRIBIR',
    'Mientras':  'MIENTRAS',
    'Si':        'SI',
    'Entonces':  'ENTONCES',
    'Verdadero': 'VERDADERO',
    'Falso':     'FALSO',
    'No':        'SINO'
}


# Añadimos los valores de reserved al listado de tokens
tokens += tuple(reserved.values())

# Reglas de los símbolos
t_ignore = ' \t'
t_MAS    = r'\+'
t_MENOS  = r'-'
t_POR    = r'\*'
t_DIVIDIDO = r'/'
t_MODULO = r'%'
t_IGUAL  = r'=='
t_DIFERENTE = r'!='
t_MENOR  = r'<'
t_MENOR_IGUAL = r'<='
t_MAYOR  = r'>'
t_MAYOR_IGUAL = r'>='
t_Y      = r'&&'
t_O      = r'\|\|'
t_NEG     = r'!'
t_ASIGNAR = r'='
t_PARENTESIS_IZQUIERDO  = r'\('
t_PARENTESIS_DERECHO    = r'\)'
t_PUNTO_Y_COMA  = r';'
t_COMA          = r','

# Literales
t_CADENA   = r'\".*?\"'
t_FLOTANTE = r'\d+\.\d+'
t_NUMERO   = r'\d+'

# Identificador y palabras reservadas
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    # Si coincide con un reservado, le cambiamos el tipo
    t.type = reserved.get(t.value, 'ID')
    return t

# Para llevar línea exacta (opcional)
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Comentarios: ignora desde // hasta fin de línea
def t_COMMENT(t):
    r'//.*'
    pass

# Captura errores
def t_error(t):
    print(f"Error léxico: caracter inesperado '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
