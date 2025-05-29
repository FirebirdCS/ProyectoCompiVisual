# optimizador.py
import re

def optimizar_codigo(lines: list[str]) -> list[str]:
    """
    Realiza optimizaciones simples de código intermedio:
      - Elimina sumas con 0:   x = y + 0  → x = y
      - Elimina sumas con 0 inversas: x = 0 + y  → x = y
      - Elimina multiplicaciones por 1: x = y * 1  → x = y
      - Elimina multiplicaciones por 1 inversas: x = 1 * y  → x = y

    @param lines: lista de líneas de código intermedio originales
    @return: lista optimizada
    """
    optimized = []
    for line in lines:
        # x = y + 0
        m = re.match(r'^(\w+)\s*=\s*(\w+)\s*\+\s*0$', line)
        if m:
            dest, src = m.group(1), m.group(2)
            optimized.append(f"{dest} = {src}")
            continue
        # x = 0 + y
        m = re.match(r'^(\w+)\s*=\s*0\s*\+\s*(\w+)$', line)
        if m:
            dest, src = m.group(1), m.group(2)
            optimized.append(f"{dest} = {src}")
            continue
        # x = y * 1
        m = re.match(r'^(\w+)\s*=\s*(\w+)\s*\*\s*1$', line)
        if m:
            dest, src = m.group(1), m.group(2)
            optimized.append(f"{dest} = {src}")
            continue
        # x = 1 * y
        m = re.match(r'^(\w+)\s*=\s*1\s*\*\s*(\w+)$', line)
        if m:
            dest, src = m.group(1), m.group(2)
            optimized.append(f"{dest} = {src}")
            continue
        # Por defecto, mantenemos la línea original
        optimized.append(line)
    return optimized
