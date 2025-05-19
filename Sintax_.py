# Sintax_.py
import ply.yacc as yacc
from Lexic_ import tokens, lexer
from ast_node import ASTNode
import Semantico

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

# ------------------------------------------------
# Producciones con AST + semántico usando expr.semantic
# ------------------------------------------------

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
        p[0] = ASTNode('decls', [ASTNode('Definir'), ASTNode('ids', value=ids), ASTNode('tipo', value=tipo)])
    else:
        prev = p[1]
        ids, tipo = p[3], p[4]
        prev.add_child(ASTNode('ids', value=ids))
        prev.add_child(ASTNode('tipo', value=tipo))
        p[0] = prev
    # Semántico: declarar variables
    Semantico.declarar_variables(ids, tipo)


def p_lista_ids(p):
    '''lista_ids : ID
                 | lista_ids COMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]


def p_tipo(p):
    'tipo : ENTERO'
    p[0] = 'Entero'


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
    var, expr_node = p[1], p[3]
    # Semántico: evalúa expresión y asigna
    Semantico.asignar_expresion(var, expr_node.semantic)
    node = ASTNode('asignacion', [ASTNode('id', value=var), expr_node])
    p[0] = node


def p_escritura(p):
    '''escritura : ESCRIBIR PARENTESIS_IZQUIERDO lista_expr PARENTESIS_DERECHO PUNTO_Y_COMA
                  | ESCRIBIR PARENTESIS_IZQUIERDO lista_expr PARENTESIS_DERECHO'''
    p[0] = ASTNode('escribir', [p[3]])


def p_lista_expr(p):
    '''lista_expr : expresion
                  | lista_expr COMA expresion'''
    if len(p) == 2:
        p[0] = ASTNode('exprs', [p[1]])
    else:
        p[1].add_child(p[3])
        p[0] = p[1]

# ------ Expresiones ------

def p_expresion_num(p):
    'expresion : NUMERO'
    node = ASTNode('numero', value=p[1])
    node.semantic = ('literal', str(p[1]))
    p[0] = node


def p_expresion_flota(p):
    'expresion : FLOTANTE'
    node = ASTNode('flotante', value=p[1])
    node.semantic = ('literal', str(p[1]))
    p[0] = node


def p_expresion_cadena(p):
    'expresion : CADENA'
    val = p[1].strip('"')
    node = ASTNode('cadena', value=val)
    node.semantic = ('literal', f'"{val}"')
    p[0] = node


def p_expresion_bool(p):
    '''expresion : VERDADERO
                 | FALSO'''
    node = ASTNode('booleano', value=p[1])
    node.semantic = ('literal', p[1])
    p[0] = node


def p_expresion_id(p):
    'expresion : ID'
    var = p[1]
    Semantico.usar_variable(var)
    node = ASTNode('id', value=var)
    node.semantic = ('var', var)
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
    # Semántico: evalúa binop cause errors internally
    node = ASTNode('op', [left, ASTNode(op), right])
    node.semantic = ('binop', op, left.semantic, right.semantic)
    Semantico.evaluar_expresion(node.semantic)
    p[0] = node


def p_expresion_neg(p):
    'expresion : NEG expresion'
    expr_node = p[2]
    node = ASTNode('neg', [expr_node])
    node.semantic = ('not', expr_node.semantic)
    Semantico.evaluar_expresion(node.semantic)
    p[0] = node


def p_expresion_paren(p):
    'expresion : PARENTESIS_IZQUIERDO expresion PARENTESIS_DERECHO'
    p[0] = p[2]

# ------ Control de flujo ------

def p_mientras(p):
    'mientras : MIENTRAS expresion instrucciones FIN MIENTRAS'
    # Semántico: condición debe ser booleano
    tipo_cond = Semantico.evaluar_expresion(p[2].semantic)
    if tipo_cond != 'Booleano':
        Semantico.evaluar_expresion(p[2].semantic)  # duplicates error
    p[0] = ASTNode('mientras', [p[2], p[3]])


def p_si(p):
    'si : SI expresion ENTONCES instrucciones sino_opcional'
    tipo_cond = Semantico.evaluar_expresion(p[2].semantic)
    if tipo_cond != 'Booleano':
        Semantico.evaluar_expresion(p[2].semantic)
    node = ASTNode('si', [p[2], p[4]])
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
# Análisis combinado
def analizar_codigo(codigo: str):
    """
    Parsea código, retorna errores_semanticos, AST y errores_sintacticos.
    """
    global errores_sintacticos
    Semantico.resetear_semantico()
    errores_sintacticos = []
    ast_root = parser.parse(codigo, lexer=lexer)
    errores_semanticos = Semantico.obtener_errores()
    # Devolver en orden: semánticos, AST, sintácticos
    return errores_semanticos, ast_root, errores_sintacticos
