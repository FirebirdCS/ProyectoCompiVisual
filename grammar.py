from Lexic_ import lexer
from Buffer import Buffer
from Sintax_ import analizar_codigo
from graphviz import Source
from codigo_intermedio import obtener_codigo
from optimizar_codigo import optimizar_codigo

def main():
    buf = Buffer()
    codigo_fuente = buf.load_buffer()

    # Léxico
    lexer.lineno = 1
    lexer.input(codigo_fuente)
    print("Tokens encontrados:\n")
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(f"{tok.type:20} {tok.value!r}   (línea {tok.lineno})")

    # Sintaxis y AST
    lexer.lineno = 1
    print("\nAnálisis sintáctico y generado AST:\n")
    errores_semanticos, ast_root, errores, codigo_intermedio = analizar_codigo(codigo_fuente)
    codigo_optimizado = optimizar_codigo(codigo_intermedio)

    if errores:
        for err in errores:
            print(err)
    else:
        dot_path = 'arbol_output.dot'
        pdf_path = 'Arbol.pdf'

        # 1) Genera el .dot
        with open(dot_path, 'w') as f:
            f.write(ast_root.to_dot())
        print("AST generado en arbol_output.dot")

        # 2) Renderiza directamente a PDF
        src = Source.from_file(dot_path)
        src.render(filename='Arbol', format='pdf', cleanup=True)
        print(f"PDF generado en {pdf_path}")

    # Semántico
    print("\nAnálisis semántico:\n")
    if errores_semanticos:
        print("Errores semánticos encontrados:")
        for err in errores_semanticos:
            print(err)
    else:
        print("Análisis semántico exitoso: sin errores")


    # Mostrar código intermedio
    print("\nCódigo Intermedio:\n")
    intermedio = codigo_intermedio
    if intermedio:
        for linea in intermedio:
            print(linea)
    else:
        print("No se generó código intermedio.")

    print("\nCódigo Intermedio Optimizado:\n")
    for linea in codigo_optimizado:
        print(linea)

    input("\nPresiona Enter para terminar...")

if __name__ == "__main__":
    main()
