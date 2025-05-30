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
from codigo_intermedio import obtener_codigo
from optimizar_codigo import optimizar_codigo

class LexicalGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compilador Grupo#3 - Interfaz Gráfica")
        self.geometry("1400x700")
        self.errors = []
        self.syntax_errors = []
        self.semantic_errors = []
        self.create_widgets()

    def create_widgets(self):
        # Main container with three panes
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame for source code
        left_frame = ttk.Labelframe(main_paned, text="Archivo .Compi", width=300)
        main_paned.add(left_frame, weight=0)

        self.text_area = tk.Text(left_frame, wrap=tk.NONE, height=20)
        self.text_area.pack(fill=tk.X, expand=False, padx=5, pady=5)
        self.text_area.config(state=tk.DISABLED)

        # Middle frame for symbol table and analysis
        middle_frame = ttk.Labelframe(main_paned, text="Tabla de Símbolos", width=800)
        main_paned.add(middle_frame, weight=1)

        columns = ("Tipo", "Valor", "Línea")
        self.tree = ttk.Treeview(middle_frame, columns=columns, show="headings", height=15)
        self.tree.column("Tipo", width=100, anchor=tk.W)
        self.tree.column("Valor", width=150, anchor=tk.W)
        self.tree.column("Línea", width=50, anchor=tk.CENTER)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.X, expand=False, padx=5, pady=5)

        # Right frame for intermediate code
        right_frame = ttk.Labelframe(main_paned, text="Código Intermedio")
        main_paned.add(right_frame, weight=1)

        # Create notebook for intermediate code tabs
        self.code_notebook = ttk.Notebook(right_frame)
        self.code_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Original intermediate code tab
        original_frame = ttk.Frame(self.code_notebook)
        self.code_notebook.add(original_frame, text="Original")
        self.original_code = tk.Text(original_frame, wrap=tk.NONE, height=20)
        self.original_code.pack(fill=tk.BOTH, expand=True)
        self.original_code.config(state=tk.DISABLED)

        # Optimized intermediate code tab
        optimized_frame = ttk.Frame(self.code_notebook)
        self.code_notebook.add(optimized_frame, text="Optimizado")
        self.optimized_code = tk.Text(optimized_frame, wrap=tk.NONE, height=20)
        self.optimized_code.pack(fill=tk.BOTH, expand=True)
        self.optimized_code.config(state=tk.DISABLED)

        # Frame para botones de análisis léxico
        lex_btn_frame = tk.Frame(middle_frame)
        lex_btn_frame.pack(fill=tk.X, pady=5)
        ver_err_btn = ttk.Button(lex_btn_frame, text="Ver Errores", command=self.show_errors)
        ver_err_btn.pack(side=tk.LEFT, padx=5)

        # Frame para análisis sintáctico
        syntax_frame = ttk.Labelframe(middle_frame, text="Análisis sintáctico y árbol de derivación")
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
        semantic_frame = ttk.Labelframe(middle_frame, text="Análisis semántico")
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

            # Reset código intermedio
            self.original_code.config(state=tk.NORMAL)
            self.original_code.delete('1.0', tk.END)
            self.original_code.config(state=tk.DISABLED)
            self.optimized_code.config(state=tk.NORMAL)
            self.optimized_code.delete('1.0', tk.END)
            self.optimized_code.config(state=tk.DISABLED)

            buf = Buffer()
            # Capturar salida de errores de t_error
            stdout_backup = sys.stdout
            sys.stdout = io.StringIO()

            # 1. Análisis Léxico
            lexer.input(content)
            tok = lexer.token()
            while tok:
                self.tree.insert("", tk.END, values=(tok.type, tok.value, tok.lineno))
                tok = lexer.token()

            err_output = sys.stdout.getvalue()
            sys.stdout = stdout_backup

            # Procesar mensajes de error léxico
            for line in err_output.splitlines():
                if line.startswith("Error léxico"):
                    self.errors.append(line)

            # Si hay errores léxicos, detener aquí
            if self.errors:
                messagebox.showwarning(
                    "Errores Léxicos",
                    "Se encontraron errores durante el análisis léxico. "
                    "Presiona 'Ver Errores' para más detalles."
                )
                return

            # 2. Análisis Sintáctico y Semántico
            errores_semanticos, ast_root, errores_sintacticos, codigo_intermedio = analizar_codigo(content)
            self.syntax_errors = errores_sintacticos
            self.semantic_errors = errores_semanticos

            # Si hay errores sintácticos, detener aquí
            if self.syntax_errors:
                messagebox.showwarning(
                    "Errores Sintácticos",
                    "Se encontraron errores durante el análisis sintáctico. "
                    "Presiona 'Ver Errores Sintácticos' para más detalles."
                )
                return

            # Si hay errores semánticos, detener aquí
            if self.semantic_errors:
                messagebox.showwarning(
                    "Errores Semánticos",
                    "Se encontraron errores durante el análisis semántico. "
                    "Presiona 'Ver Errores Semánticos' para más detalles."
                )
                return

            # 3. Si no hay errores, continuar con AST y código intermedio
            if ast_root is not None:
                # Generar AST
                dot_path = 'arbol_output.dot'
                pdf_path = 'Arbol.pdf'
                with open(dot_path, 'w', encoding='utf-8') as f:
                    f.write(ast_root.to_dot())
                src = Source.from_file(dot_path)
                src.render(filename='Arbol', format='pdf', cleanup=True)

                # Actualizar código intermedio
                self.original_code.config(state=tk.NORMAL)
                self.original_code.delete('1.0', tk.END)
                if codigo_intermedio:
                    self.original_code.insert(tk.END, '\n'.join(codigo_intermedio))
                self.original_code.config(state=tk.DISABLED)

                # Actualizar código optimizado
                codigo_optimizado = optimizar_codigo(codigo_intermedio)
                self.optimized_code.config(state=tk.NORMAL)
                self.optimized_code.delete('1.0', tk.END)
                if codigo_optimizado:
                    self.optimized_code.insert(tk.END, '\n'.join(codigo_optimizado))
                self.optimized_code.config(state=tk.DISABLED)

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
