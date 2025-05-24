
# Semantico.py

tabla_simbolos = {}  # var_name -> tipo
errores_semanticos = []

def declarar_variables(ids, tipo):
    for var in ids:
        if var in tabla_simbolos:
            errores_semanticos.append(f"Error: Variable '{var}' ya fue declarada.")
        else:
            tabla_simbolos[var] = tipo

def tipo_literal(valor):
    if isinstance(valor, str):
        if valor.startswith('"') and valor.endswith('"'):
            return 'Cadena'
        elif valor in ['Verdadero', 'Falso']:
            return 'Booleano'
    try:
        int(valor)
        return 'Entero'
    except:
        try:
            float(valor)
            return 'Real'
        except:
            return None

def asignar_variable(var, valor):
    if var not in tabla_simbolos:
        errores_semanticos.append(f"Error: Variable '{var}' no ha sido declarada antes de su uso.")
    else:
        tipo_var = tabla_simbolos[var]
        tipo_valor = tipo_literal(valor) if isinstance(valor, str) else None
        if tipo_valor and not tipo_compatible(tipo_var, tipo_valor):
            errores_semanticos.append(f"Error: No se puede asignar un valor de tipo '{tipo_valor}' a la variable '{var}' de tipo '{tipo_var}'.")
def asignar_expresion(var, expr):
    if var not in tabla_simbolos:
        errores_semanticos.append(f"Error: Variable '{var}' no ha sido declarada antes de su uso.")
        return
    
    tipo_var = tabla_simbolos[var]
    tipo_expr = evaluar_expresion(expr)

    if tipo_expr is None:
        return  # Ya se reportó error

    if not tipo_compatible(tipo_var, tipo_expr):
        errores_semanticos.append(f"Error: No se puede asignar un valor de tipo '{tipo_expr}' a la variable '{var}' de tipo '{tipo_var}'.")

def evaluar_expresion(expr):
    if expr[0] == 'literal':
        return tipo_literal(expr[1])
    elif expr[0] == 'var':
        var = expr[1]
        if var not in tabla_simbolos:
            errores_semanticos.append(f"Error: Variable '{var}' no ha sido declarada.")
            return None
        return tabla_simbolos[var]
    elif expr[0] == 'binop':
        op, left, right = expr[1], expr[2], expr[3]
        tipo_izq = evaluar_expresion(left)
        tipo_der = evaluar_expresion(right)
        if tipo_izq is None or tipo_der is None:
            return None

        if op in ['+', '-', '*', '/', '%']:
            if tipo_izq in ['Entero', 'Real'] and tipo_der in ['Entero', 'Real']:
                return 'Real' if 'Real' in [tipo_izq, tipo_der] else 'Entero'
            errores_semanticos.append(f"Error: Operación '{op}' no válida entre '{tipo_izq}' y '{tipo_der}'.")
            return None
        elif op in ['==', '!=', '<', '>', '<=', '>=']:
            return 'Booleano'
        elif op in ['&&', '||']:
            if tipo_izq == tipo_der == 'Booleano':
                return 'Booleano'
            errores_semanticos.append(f"Error: Operación lógica '{op}' requiere booleanos.")
            return None
    elif expr[0] == 'not':
        tipo = evaluar_expresion(expr[1])
        if tipo != 'Booleano':
            errores_semanticos.append(f"Error: Negación lógica requiere tipo 'Booleano', no '{tipo}'.")
            return None
        return 'Booleano'
    return None

def tipo_compatible(tipo_var, tipo_valor):
    if tipo_var == 'Entero' and tipo_valor == 'Entero':
        return True
    if tipo_var == 'Real' and tipo_valor in ['Entero', 'Real']:
        return True
    if tipo_var == 'Cadena' and tipo_valor == 'Cadena':
        return True
    if tipo_var == 'Booleano' and tipo_valor == 'Booleano':
        return True
    return False

def usar_variable(var):
    if var not in tabla_simbolos:
        errores_semanticos.append(f"Error: Variable '{var}' no ha sido declarada.")

def resetear_semantico():
    global tabla_simbolos, errores_semanticos
    tabla_simbolos = {}
    errores_semanticos = []

def obtener_errores():
    return errores_semanticos
