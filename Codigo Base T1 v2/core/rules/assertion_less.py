from ..rule import *
from _ast import Call
import ast


class AssertionLessVisitor(WarningNodeVisitor):
    # Implementar Clase
    def __init__(self):
        super().__init__()
        self.lista_funciones = []

    def visit_FunctionDef(self, node: FunctionDef):
        if node.name.startswith("test_"):
            self.lista_funciones.append(True) 
        self.generic_visit(node)
        if self.lista_funciones:
            # Agrego un warning si la fucnion no tiene assert
            if not any(isinstance(n, ast.Assert) for n in node.body):
                self.addWarning('AssertionLessWarning', node.lineno, 'it is an assertion less test')
        if self.lista_funciones:
            self.lista_funciones.pop()

    def visit_Call(self, node: Call):
        if self.lista_funciones:
            if isinstance(node.func, ast.Attribute) and node.func.attr.startswith("assert"):
                self.lista_funciones.pop()
        self.generic_visit(node)


class AssertionLessTestRule(Rule):
    #  Implementar Clase
    def analyze(self, node):
        visitor = AssertionLessVisitor()
        visitor.visit(node)
        return visitor.warningsList()

    @classmethod
    def name(cls):
        return 'assertion-less'
