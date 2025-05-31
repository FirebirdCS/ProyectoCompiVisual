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
        # Check if it's a decimal number
        if '.' in valor:
            try:
                float(valor)
                return 'Decimal'
            except:
                return None
        # Check if it's an integer
        try:
            int(valor)
            return 'Entero'
        except:
            return None
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
        # If type is provided in the semantic tuple, use it
        if len(expr) > 2:
            return expr[2]
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
            # For arithmetic operations, both types must be the same
            if tipo_izq != tipo_der:
                errores_semanticos.append(f"Error: Operación '{op}' no válida entre tipos diferentes '{tipo_izq}' y '{tipo_der}'.")
                return None
            return tipo_izq  # Return the type of either operand since they're the same
        elif op in ['==', '!=', '<', '>', '<=', '>=']:
            # For comparisons, both types must be the same
            if tipo_izq != tipo_der:
                errores_semanticos.append(f"Error: Comparación no válida entre tipos diferentes '{tipo_izq}' y '{tipo_der}'.")
                return None
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
    if tipo_var == 'Decimal' and tipo_valor in ['Entero', 'Decimal']:
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
