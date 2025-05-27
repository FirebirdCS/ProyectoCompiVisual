import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import io
import sys
import webbrowser
from Lexic_ import lexer
from Buffer import Buffer
from Sintax_ import analizar_codigo
from graphviz import Source

class LexicalGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador Léxico - Interfaz Gráfica")
        self.geometry("1200x600")
        self.errors = []
        self.syntax_errors = []
        self.semantic_errors = []
        self.create_widgets()

    def create_widgets(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Labelframe(paned, text="Archivo .Compi", width=300)
        paned.add(left_frame, weight=0)

        self.text_area = tk.Text(left_frame, wrap=tk.NONE, height=20)
        self.text_area.pack(fill=tk.X, expand=False, padx=5, pady=5)
        self.text_area.config(state=tk.DISABLED)

        right_frame = ttk.Labelframe(paned, text="Tabla de Símbolos")
        paned.add(right_frame, weight=1)

        columns = ("Tipo", "Valor", "Línea")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        self.tree.column("Tipo", width=100, anchor=tk.W)
        self.tree.column("Valor", width=150, anchor=tk.W)
        self.tree.column("Línea", width=50, anchor=tk.CENTER)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.X, expand=False, padx=5, pady=5)

        # Frame para botones de análisis léxico
        lex_btn_frame = tk.Frame(right_frame)
        lex_btn_frame.pack(fill=tk.X, pady=5)
        ver_err_btn = ttk.Button(lex_btn_frame, text="Ver Errores", command=self.show_errors)
        ver_err_btn.pack(side=tk.LEFT, padx=5)

        # Frame para análisis sintáctico
        syntax_frame = ttk.Labelframe(right_frame, text="Análisis sintáctico y árbol de derivación")
        syntax_frame.pack(fill=tk.X, pady=5)

        # Botones de análisis sintáctico
        syntax_btn_frame = tk.Frame(syntax_frame)
        syntax_btn_frame.pack(fill=tk.X, pady=5)
        
        ver_syntax_err_btn = ttk.Button(syntax_btn_frame, text="Ver Errores Sintácticos", 
                                      command=self.show_syntax_errors)
        ver_syntax_err_btn.pack(side=tk.LEFT, padx=5)
        
        ver_arbol_btn = ttk.Button(syntax_btn_frame, text="Ver Árbol de Derivación", 
                                 command=self.open_ast_pdf)
        ver_arbol_btn.pack(side=tk.LEFT, padx=5)

        # Frame para análisis semántico
        semantic_frame = ttk.Labelframe(right_frame, text="Análisis semántico")
        semantic_frame.pack(fill=tk.X, pady=5)
        semantic_btn_frame = tk.Frame(semantic_frame)
        semantic_btn_frame.pack(fill=tk.X, pady=5)
        ver_semantic_err_btn = ttk.Button(semantic_btn_frame, text="Ver Errores Semánticos", 
                                          command=self.show_semantic_errors)
        ver_semantic_err_btn.pack(side=tk.LEFT, padx=5)

        open_btn = ttk.Button(self, text="Abrir Archivo", command=self.open_file)
        open_btn.pack(side=tk.BOTTOM, pady=10)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona el archivo de código",
            filetypes=[("Archivos de texto", "*.txt *.compi *.py"), ("Todos los archivos", "*")]
        )
        if not file_path:
            return

        dir_path = os.path.dirname(file_path)
        os.chdir(dir_path)

        self.errors.clear()
        self.syntax_errors.clear()
        self.semantic_errors.clear()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, content)
            self.text_area.config(state=tk.DISABLED)

            # Reset tabla de símbolos
            for item in self.tree.get_children():
                self.tree.delete(item)

            buf = Buffer()
            # Capturar salida de errores de t_error
            stdout_backup = sys.stdout
            sys.stdout = io.StringIO()

            # Tokenización
            lexer.input(content)
            tok = lexer.token()
            while tok:
                self.tree.insert("", tk.END, values=(tok.type, tok.value, tok.lineno))
                tok = lexer.token()


            err_output = sys.stdout.getvalue()
            sys.stdout = stdout_backup

            # Procesar mensajes de error impresos
            for line in err_output.splitlines():
                if line.startswith("Error léxico"):
                    self.errors.append(line)

            # Análisis sintáctico
            errores_semanticos, ast_root, errores_sintacticos = analizar_codigo(content)
            self.syntax_errors = errores_sintacticos
            self.semantic_errors = errores_semanticos

            # Si no hay errores sintácticos y hay un AST, genera el .dot y el PDF
            if not self.syntax_errors and ast_root is not None:
                dot_path = 'arbol_output.dot'
                pdf_path = 'Arbol.pdf'
                with open(dot_path, 'w', encoding='utf-8') as f:
                    f.write(ast_root.to_dot())
                src = Source.from_file(dot_path)
                src.render(filename='Arbol', format='pdf', cleanup=True)

            # Si hay errores léxicos, limpiar tabla y avisar
            if self.errors:
                for item in self.tree.get_children():
                    self.tree.delete(item)
                messagebox.showwarning(
                    "Errores Léxicos",
                    "Se encontraron errores durante el análisis léxico. "
                    "Presiona 'Ver Errores' para más detalles."
                )
                return

            # Si hay errores sintácticos, avisar
            if self.syntax_errors:
                messagebox.showwarning(
                    "Errores Sintácticos",
                    "Se encontraron errores durante el análisis sintáctico. "
                    "Presiona 'Ver Errores Sintácticos' para más detalles."
                )

            # Mensaje de análisis semántico
            if self.semantic_errors:
                messagebox.showwarning(
                    "Errores Semánticos",
                    "Se encontraron errores durante el análisis semántico. "
                    "Presiona 'Ver Errores Semánticos' para más detalles."
                )
            else:
                messagebox.showinfo("Listo", "Análisis léxico, sintáctico y semántico completado sin errores.")

        except Exception as e:
            self.errors.append(str(e))
            messagebox.showerror("Error", f"Ha ocurrido un error: {e}")

    def show_errors(self):
        win = tk.Toplevel(self)
        win.title("Errores Léxicos")
        win.geometry("200x200")
        if not self.errors:
            lbl = ttk.Label(win, text="No se encontraron errores léxicos.")
            lbl.pack(padx=10, pady=10)
        else:
            listbox = tk.Listbox(win)
            for err in self.errors:
                listbox.insert(tk.END, err)
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_syntax_errors(self):
        win = tk.Toplevel(self)
        win.title("Errores Sintácticos")
        win.geometry("200x200")
        if not self.syntax_errors:
            lbl = ttk.Label(win, text="No se encontraron errores sintácticos.")
            lbl.pack(padx=10, pady=10)
        else:
            listbox = tk.Listbox(win)
            for err in self.syntax_errors:
                listbox.insert(tk.END, err)
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_semantic_errors(self):
        win = tk.Toplevel(self)
        win.title("Errores Semánticos")
        win.geometry("300x200")
        if not self.semantic_errors:
            lbl = ttk.Label(win, text="No se encontraron errores semánticos.")
            lbl.pack(padx=10, pady=10)
        else:
            listbox = tk.Listbox(win)
            for err in self.semantic_errors:
                listbox.insert(tk.END, err)
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def open_ast_pdf(self):
        pdf_path = 'Arbol.pdf'
        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showwarning(
                "Archivo no encontrado",
                "No se encontró el archivo del árbol de derivación."
            )

if __name__ == "__main__":
    app = LexicalGUI()
    app.mainloop()
