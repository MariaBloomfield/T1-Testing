from _ast import Call
from typing import Any
from ..rule import *
import ast


class AssertionTrueVisitor(WarningNodeVisitor):
    #  Implementar Clase
    def __init__(self):
        super().__init__()
        self.true_variables = set()

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant) and node.value.value is True:
                self.true_variables.add(target.id)
        NodeVisitor.generic_visit(self, node)

    def visit_Call(self, node: Call):
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                if node.func.attr == 'assertTrue':
                    if isinstance(node.args[0], ast.Constant) and node.args[0].value is True:
                        self.addWarning('AssertTrueWarning', node.lineno, 'useless assert true detected')
                    elif isinstance(node.args[0], ast.Name) and node.args[0].id in self.true_variables:
                        self.addWarning('AssertTrueWarning', node.lineno, 'useless assert true detected')
        NodeVisitor.generic_visit(self, node)


class AssertionTrueTestRule(Rule):
    #  Implementar Clase
    def analyze(self, node):
        visitor = AssertionTrueVisitor()
        visitor.visit(node)
        return visitor.warningsList()

    @classmethod
    def name(cls):
        return 'assertion-true'
