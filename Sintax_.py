# Sintax_.py
import ply.yacc as yacc
from Lexic_ import tokens, lexer
from ast_node import ASTNode
import Semantico
from codigo_intermedio import limpiar_codigo, nueva_temp, agregar_linea, reiniciar, obtener_codigo

# Listas de errores
errores_sintacticos = []

# Precedencia operadores
precedence = (
    ('left', 'O'),
    ('left', 'Y'),
    ('right', 'NEG'),
    ('left', 'IGUAL', 'DIFERENTE'),
    ('left', 'MENOR', 'MENOR_IGUAL', 'MAYOR', 'MAYOR_IGUAL'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'POR', 'DIVIDIDO', 'MODULO'),
)

# --------------------------
# Producciones combinadas: AST, semántico y código intermedio
# --------------------------

def p_programa(p):
    'programa : ALGORITMO ID bloque FIN ALGORITMO'
    p[0] = ASTNode('programa', [ASTNode('Algoritmo', value=p[2]), p[3]])


def p_bloque(p):
    'bloque : declaraciones INICIO instrucciones FIN'
    p[0] = ASTNode('bloque', [p[1], ASTNode('Inicio'), p[3]])


def p_declaraciones(p):
    '''declaraciones : DEFINIR lista_ids tipo
                     | declaraciones DEFINIR lista_ids tipo'''
    if len(p) == 4:
        ids, tipo = p[2], p[3]
        node = ASTNode('decls', [ASTNode('Definir'), ASTNode('ids', value=ids), ASTNode('tipo', value=tipo)])
    else:
        node = p[1]
        ids, tipo = p[3], p[4]
        node.add_child(ASTNode('ids', value=ids))
        node.add_child(ASTNode('tipo', value=tipo))
    # Semántico: declarar variables
    Semantico.declarar_variables(ids, tipo)
    p[0] = node


def p_lista_ids(p):
    '''lista_ids : ID
                 | lista_ids COMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]


def p_tipo(p):
    '''tipo : ENTERO
            | DECIMAL
            | CADENA_TIPO'''
    if p[1] == 'Entero':
        p[0] = 'Entero'
    elif p[1] == 'Decimal':
        p[0] = 'Decimal'
    elif p[1] == 'Cadena':
        p[0] = 'Cadena'


def p_instrucciones(p):
    '''instrucciones : instruccion
                     | instrucciones instruccion'''
    if len(p) == 2:
        p[0] = ASTNode('instrs', [p[1]])
    else:
        p[1].add_child(p[2])
        p[0] = p[1]


def p_instruccion(p):
    '''instruccion : escritura
                   | asignacion
                   | mientras
                   | si'''
    p[0] = p[1]


def p_asignacion(p):
    '''asignacion : ID ASIGNAR expresion PUNTO_Y_COMA
                  | ID ASIGNAR expresion'''
    var = p[1]
    expr_node = p[3]
    # Semántico: evalúa expresión y asigna
    Semantico.asignar_expresion(var, expr_node.semantic)
    # Código intermedio
    agregar_linea(f"{var} = {expr_node.code}")
    node = ASTNode('asignacion', [ASTNode('id', value=var), expr_node])
    p[0] = node


def p_escritura(p):
    '''escritura : ESCRIBIR PARENTESIS_IZQUIERDO lista_expr PARENTESIS_DERECHO PUNTO_Y_COMA
                  | ESCRIBIR PARENTESIS_IZQUIERDO lista_expr PARENTESIS_DERECHO'''
    # Código intermedio: imprimir cada expr
    for expr in p[3].children:
        agregar_linea(f"print {expr.code}")
    p[0] = ASTNode('escribir', [p[3]])


def p_lista_expr(p):
    '''lista_expr : expresion
                  | lista_expr COMA expresion'''
    if len(p) == 2:
        node = ASTNode('exprs', [p[1]])
    else:
        node = p[1]
        node.add_child(p[3])
    p[0] = node

# ------ Expresiones ------

def p_expresion_num(p):
    'expresion : NUMERO'
    node = ASTNode('numero', value=p[1])
    node.semantic = ('literal', str(p[1]))
    node.code = str(p[1])
    p[0] = node


def p_expresion_flota(p):
    'expresion : FLOTANTE'
    node = ASTNode('flotante', value=p[1])
    node.semantic = ('literal', str(p[1]))
    node.code = str(p[1])
    p[0] = node


def p_expresion_cadena(p):
    'expresion : CADENA'
    val = p[1].strip('"')
    node = ASTNode('cadena', value=val)
    node.semantic = ('literal', f'"{val}"')
    node.code = f'"{val}"'
    p[0] = node


def p_expresion_bool(p):
    '''expresion : VERDADERO
                 | FALSO'''
    node = ASTNode('booleano', value=p[1])
    node.semantic = ('literal', p[1])
    node.code = p[1]
    p[0] = node


def p_expresion_id(p):
    'expresion : ID'
    var = p[1]
    Semantico.usar_variable(var)
    node = ASTNode('id', value=var)
    node.semantic = ('var', var)
    node.code = var
    p[0] = node


def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                  | expresion MENOS expresion
                  | expresion POR expresion
                  | expresion DIVIDIDO expresion
                  | expresion MODULO expresion
                  | expresion IGUAL expresion
                  | expresion DIFERENTE expresion
                  | expresion MENOR expresion
                  | expresion MAYOR expresion
                  | expresion MENOR_IGUAL expresion
                  | expresion MAYOR_IGUAL expresion
                  | expresion Y expresion
                  | expresion O expresion'''
    op = p[2]
    left, right = p[1], p[3]
    # Semántico
    semantic = ('binop', op, left.semantic, right.semantic)
    Semantico.evaluar_expresion(semantic)
    # Código intermedio
    temp = nueva_temp()
    agregar_linea(f"{temp} = {left.code} {op} {right.code}")
    node = ASTNode('op', [left, ASTNode(op), right])
    node.semantic = semantic
    node.code = temp
    p[0] = node


def p_expresion_neg(p):
    'expresion : NEG expresion'
    expr_node = p[2]
    semantic = ('not', expr_node.semantic)
    Semantico.evaluar_expresion(semantic)
    temp = nueva_temp()
    agregar_linea(f"{temp} = !{expr_node.code}")
    node = ASTNode('neg', [expr_node])
    node.semantic = semantic
    node.code = temp
    p[0] = node


def p_expresion_paren(p):
    'expresion : PARENTESIS_IZQUIERDO expresion PARENTESIS_DERECHO'
    p[0] = p[2]

# ------ Control de flujo ------

def p_mientras(p):
    'mientras : MIENTRAS expresion instrucciones FIN MIENTRAS'
    cond = p[2]
    tipo_cond = Semantico.evaluar_expresion(cond.semantic)
    if tipo_cond != 'Booleano':
        Semantico.evaluar_expresion(cond.semantic)
    # Generación simplificada: etiquetas y goto
    start = nueva_temp()
    end = nueva_temp()
    agregar_linea(f"L{start}:")
    agregar_linea(f"ifFalse {cond.code} goto L{end}")
    for instr in p[3].children:
        # Asumimos que cada instr tiene code gen líneas ya agregadas
        pass
    agregar_linea(f"goto L{start}")
    agregar_linea(f"L{end}:")
    p[0] = ASTNode('mientras', [cond, p[3]])


def p_si(p):
    'si : SI expresion ENTONCES instrucciones sino_opcional'
    cond = p[2]
    tipo_cond = Semantico.evaluar_expresion(cond.semantic)
    if tipo_cond != 'Booleano':
        Semantico.evaluar_expresion(cond.semantic)
    # Código intermedio simple
    else_label = nueva_temp()
    end = nueva_temp()
    agregar_linea(f"ifFalse {cond.code} goto L{else_label}")
    # then block lines generated
    for instr in p[4].children:
        pass
    agregar_linea(f"goto L{end}")
    agregar_linea(f"L{else_label}:")
    if p[5]:
        for instr in p[5].children:
            pass
    agregar_linea(f"L{end}:")
    node = ASTNode('si', [cond, p[4]])
    if p[5]: node.add_child(p[5])
    p[0] = node


def p_sino_opcional(p):
    '''sino_opcional : SINO si
                     | SINO instrucciones
                     | empty'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None


def p_empty(p):
    'empty :'
    p[0] = None

# ------ Errores ------

def p_error(p):
    if p:
        errores_sintacticos.append(f"Error de sintaxis en '{p.value}' línea {p.lineno}")
        parser.errok()
    else:
        errores_sintacticos.append("Error de sintaxis en EOF")

# Construcción parser
parser = yacc.yacc()

# Análisis combinado
def analizar_codigo(codigo: str):
    """
    Parsea código, retorna errores_semanticos, AST, errores_sintacticos y código intermedio.
    """
    global errores_sintacticos
    Semantico.resetear_semantico()
    reiniciar()  # limpia código intermedio
    errores_sintacticos = []
    ast_root = parser.parse(codigo, lexer=lexer)
    errores_semanticos = Semantico.obtener_errores()
    codigo_int = obtener_codigo()
    codigo_int = limpiar_codigo(codigo_int)
    return errores_semanticos, ast_root, errores_sintacticos, codigo_int
