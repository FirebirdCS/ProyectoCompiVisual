class Buffer:
    def load_buffer(self):
        try:
            with open('MiLenguaje.compi', 'r', encoding='utf-8') as arq:
                return arq.read()
        except FileNotFoundError:
            print("Error: No se encontró el archivo 'MiLenguaje.compi'.")
            return ""
