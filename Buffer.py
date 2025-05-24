<<<<<<< HEAD
class Buffer:
    def load_buffer(self):
        arq = open('programaTest.py', 'r')
        text = arq.readline()

        buffer = []
        cont = 1

        while text != "":
            buffer.append(text)
            text = arq.readline()
            cont += 1

            if cont == 10 or text == '':
                # Retornamos el buffer
                buf = ''.join(buffer)
                cont = 1
                yield buf

                # Reseteamos el buffer
                buffer = []

=======
class Buffer:
    def load_buffer(self):
        arq = open('MiLenguaje.compi', 'r')
        text = arq.readline()

        buffer = []
        cont = 1

        while text != "":
            buffer.append(text)
            text = arq.readline()
            cont += 1

            if cont == 10 or text == '':
                # Retornamos el buffer
                buf = ''.join(buffer)
                cont = 1
                yield buf

                # Reseteamos el buffer
                buffer = []

>>>>>>> Alvaro-branch
        arq.close()