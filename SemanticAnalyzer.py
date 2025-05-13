class SemanticAnalyzer:
    def __init__(self, tokens, lexemes):
        self.tokens = tokens          # Lista de tokens generados
        self.lexemes = lexemes        # Lista de lexemas (para mensajes de error)
        self.current = 0              # Índice del token actual
        self.symbol_table = {}        # Tabla de símbolos para variables

    def current_token(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def advance(self):
        self.current += 1

    def match(self, token_type):
        if self.current_token() == token_type:
            self.advance()
        else:
            raise SyntaxError(f"Se esperaba {token_type} pero se encontró {self.current_token()}.")

    def parse(self):
        self.program()
        print("Análisis semántico completado: El programa es semánticamente válido.")

    # program -> statement_list EOF
    def program(self):
        self.statement_list()
        self.match("EOF")

    # statement_list -> { NEWLINE } statement { statement } { NEWLINE }
    def statement_list(self):
        while self.current_token() != "EOF":
            if self.current_token() == "NEWLINE":
                self.advance()
            else:
                self.statement()

    # statement -> assignment | func_call
    def statement(self):
        if self.current_token() == "ID":
            # Según el siguiente token: asignación o llamada a función
            if self.tokens[self.current + 1] == "ASSIGN":
                self.assignment()
            elif self.tokens[self.current + 1] == "LPAREN":
                self.func_call()
            else:
                raise SyntaxError("Sentencia no reconocida después del identificador.")
        elif self.current_token() == "PRINT":
            self.func_call()
        else:
            raise SyntaxError("Se esperaba una sentencia.")

    # assignment -> ID ASSIGN expression NEWLINE
    def assignment(self):
        # Capturamos el nombre de la variable antes de consumir el token
        var_name = self.lexemes[self.current]
        self.match("ID")
        self.match("ASSIGN")
        expr_type = self.expression()
        self.match("NEWLINE")
        # Si la variable ya existe, el nuevo valor debe ser del mismo tipo
        if var_name in self.symbol_table:
            if self.symbol_table[var_name] != expr_type:
                raise Exception(
                    f"Error semántico: La variable '{var_name}' ya fue asignada como {self.symbol_table[var_name]} y se intenta asignar un valor de tipo {expr_type}."
                )
        else:
            self.symbol_table[var_name] = expr_type

    # func_call -> PRINT LPAREN expression RPAREN NEWLINE
    def func_call(self):
        # Solo se permite la función 'print'
        if self.current_token() == "PRINT":
            self.match("PRINT")
        else:
            raise Exception(f"Error semántico: Función desconocida: {self.lexemes[self.current]}")
        self.match("LPAREN")
        # Se evalúa el argumento, aunque para 'print' no se requiere un tipo específico
        self.expression()
        self.match("RPAREN")
        self.match("NEWLINE")

    # expression -> term { (PLUS | MINUS) term }
    def expression(self):
        left_type = self.term()
        while self.current_token() in ["PLUS", "MINUS"]:
            op = self.current_token()
            self.advance()
            right_type = self.term()
            # Se exige que ambos operandos sean del mismo tipo
            if left_type != right_type:
                raise Exception(
                    f"Error semántico: No se pueden combinar tipos diferentes con '{op}': {left_type} y {right_type}."
                )
            # El tipo resultante es el mismo (no se realizan conversiones)
            left_type = left_type
        return left_type

    # term -> factor { (MULT | DIV) factor }
    def term(self):
        left_type = self.factor()
        while self.current_token() in ["MULT", "DIV"]:
            op = self.current_token()
            self.advance()
            right_type = self.factor()
            if left_type != right_type:
                raise Exception(
                    f"Error semántico: No se pueden combinar tipos diferentes con '{op}': {left_type} y {right_type}."
                )
            left_type = left_type
        return left_type

    # factor -> INTEGER_CONST | FLOAT_CONST | ID | LPAREN expression RPAREN
    def factor(self):
        tok = self.current_token()
        if tok == "INTEGER_CONST":
            self.advance()
            return "int"
        elif tok == "FLOAT_CONST":
            self.advance()
            return "float"
        elif tok == "ID":
            var_name = self.lexemes[self.current]
            self.advance()
            # Si la variable no ha sido asignada previamente, se lanza un error
            if var_name not in self.symbol_table:
                raise Exception(f"Error semántico: La variable '{var_name}' no ha sido declarada.")
            return self.symbol_table[var_name]
        elif tok == "LPAREN":
            self.match("LPAREN")
            expr_type = self.expression()
            self.match("RPAREN")
            return expr_type
        else:
            raise Exception("Error semántico: Se esperaba un número, un identificador o '(' en la expresión.")
    