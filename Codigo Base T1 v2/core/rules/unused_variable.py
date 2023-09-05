from _ast import Assign, BinOp, Call
from typing import Any
from ..rule import *
import ast


class UnusedVariableVisitor(WarningNodeVisitor):
    #  Implementar Clase
    def __init__(self):
        super().__init__()
        self.lista_funciones = []
        self.lista_variables = []

    def visit_FunctionDef(self, node: FunctionDef):
        if node.name.startswith("test_"):
            self.lista_funciones.append(True)
        self.generic_visit(node)
        if self.lista_funciones:
            # Agrego las variable definidas en la funcion
            for n in node.body:
                if isinstance(n, ast.Assign):
                    for target in n.targets:
                        print("Variable Encontrada:", target.id, "en linea:", n.lineno)
                        self.lista_variables.append((target.id, n.lineno))

                # Encuentro las variables usadas en metodos de la funcion y las elimino de la lista
                elif isinstance(n, ast.Expr):
                    if isinstance(n.value, ast.Call):
                        if isinstance(n.value.args[0], ast.Name):  # Verifica si es un nodo Name
                            variable_name = n.value.args[0].id
                            if variable_name in [var[0] for var in self.lista_variables]:
                                print("Variable Usada:", variable_name)
                                self.lista_variables = [(var_name, var_line) for var_name, var_line in self.lista_variables if var_name != variable_name]
        self.generic_visit(node)

        for variable in self.lista_variables:
            self.addWarning('UnusedVariable', variable[1], 'variable ' + variable[0] + ' has not been used')
            # Se elimina la variable de la lista para que no se repita el warning
            self.lista_variables = [(var_name, var_line) for var_name, var_line in self.lista_variables if var_name != variable[0]]

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                # Reviso si la asignación de la variable contiene a otra variable:
                print("variable", target.id)
                print(node.value.value)
                if node.value.value in [var[0] for var in self.lista_variables]:
                    print("Variable Usada:", node.value.value)
                    self.lista_variables = [(var_name, var_line) for var_name, var_line in self.lista_variables if var_name != node.value.value]
        self.generic_visit(node)

    def visit_BinOp(self, node: BinOp):
        print("linea de binop", node.lineno)
        left_operand = node.left
        right_operand = node.right
        if isinstance(left_operand, ast.Name):
            print("left", left_operand.id)
            if left_operand.id in [var[0] for var in self.lista_variables]:
                print("Variable Usada:", left_operand.id)
                self.lista_variables = [(var_name, var_line) for var_name, var_line in self.lista_variables if var_name != left_operand.id]
        if isinstance(right_operand, ast.Name):
            if right_operand.id in [var[0] for var in self.lista_variables]:
                print("Variable Usada:", right_operand.id)
                self.lista_variables = [(var_name, var_line) for var_name, var_line in self.lista_variables if var_name != right_operand.id]
        self.generic_visit(node)


class UnusedVariableTestRule(Rule):
    #  Implementar Clase
    def analyze(self, node):
        visitor = UnusedVariableVisitor()
        visitor.visit(node)
        return visitor.warningsList()

    @classmethod
    def name(cls):
        return 'not-used-variable'
