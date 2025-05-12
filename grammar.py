from Lexic_ import lexer
from Buffer import Buffer

def main():
    buf = Buffer()

    print("Tokens encontrados:\n")
    # Recorremos cada "chunk" de hasta 10 líneas
    for chunk in buf.load_buffer():
        # Alimentamos el lexer con el bloque de texto
        lexer.input(chunk)

        # Recorremos y mostramos todos los tokens de este bloque
        for tok in lexer:
            print(f"{tok.type:20} {tok.value!r}   (línea {tok.lineno})")

    input("\nPresiona Enter para terminar...")

if __name__ == "__main__":
    main()
