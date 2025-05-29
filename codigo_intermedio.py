# codigo_intermedio.py

codigo_intermedio = []
contador_temp = 0

def nueva_temp():
    global contador_temp
    contador_temp += 1
    return f"t{contador_temp}"

def agregar_linea(linea):
    codigo_intermedio.append(linea)

def reiniciar():
    global codigo_intermedio, contador_temp
    codigo_intermedio = []
    contador_temp = 0

def obtener_codigo():
    return codigo_intermedio

def limpiar_codigo(lines: list[str]) -> list[str]:
    """
    Elimina patrones redundantes como:
      ifFalse tX goto LY
      goto LZ
      LY:
      LZ:
    cuando no hay nada entre LY: y LZ:.
    """
    cleaned = []
    i = 0
    n = len(lines)
    while i < n:
        # Busca el patrón redundante de 4 ó 5 líneas
        if (
            i + 3 < n
            and lines[i].startswith("ifFalse")
            and lines[i+1].startswith("goto")
            and lines[i+2].endswith(":")
            and lines[i+3].endswith(":")
        ):
            # Nos saltamos estas 4 líneas
            i += 4
            # Si hay línea 'goto L…' extra justo después, también la saltamos
            if i < n and lines[i].startswith("goto"):
                i += 1
        else:
            cleaned.append(lines[i])
            i += 1
    return cleaned


