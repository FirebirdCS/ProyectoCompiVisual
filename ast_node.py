class ASTNode:
    """
    Nodo genérico para el árbol de sintaxis abstracta (AST).

    Atributos:
        name (str): etiqueta o tipo del nodo (p.ej. 'asignacion', 'numero').
        children (list[ASTNode]): lista de nodos hijos.
        value (any): valor literal o identificador (opcional).
    """
    def __init__(self, name: str, children=None, value=None):
        self.name = name
        self.children = children if children is not None else []
        self.value = value

    def add_child(self, node: "ASTNode"):
        """Agrega un hijo al nodo actual."""
        if node is not None:
            self.children.append(node)

    def __repr__(self):
        val = f": {self.value}" if self.value is not None else ""
        return f"ASTNode({self.name}{val})"

    def to_dot(self) -> str:
        """
        Genera la representación DOT de este nodo y sus hijos,
        escapando comillas dobles en los valores.
        """
        lines = ["digraph AST {", "  node [shape=box];"]
        _counter = {"n": 0}

        def _visit(n):
            nid = f"n{_counter['n']}"
            _counter['n'] += 1
            # Prepara etiqueta, escapando comillas dobles
            raw_label = n.name + (f": {n.value}" if n.value is not None else "")
            label = raw_label.replace('"', '\\"')
            lines.append(f"  {nid} [label=\"{label}\"];" )
            for child in n.children:
                cid = _visit(child)
                lines.append(f"  {nid} -> {cid};")
            return nid

        _visit(self)
        lines.append("}")
        return "\n".join(lines)
