from ast import *
import ast
from typing import Any
from core.rewriter import RewriterCommand

class ExtractSetupCommand(RewriterCommand):

    class CommonLinesVisitor(NodeVisitor):

        def __init__(self):
            super().__init__()
            self.common_lines = None
            self.method_lines = set()

        def visit_ClassDef(self, node: ClassDef):
            self.common_lines = None
            self.generic_visit(node)
            if self.common_lines is not None:
                print("Lineas comunes:", self.common_lines)
        
        def visit_FunctionDef(self, node: FunctionDef):
            self.method_lines.clear()
            self.generic_visit(node)
            if self.common_lines is None:
                self.common_lines = self.method_lines.copy()
            else:
                self.common_lines.intersection_update(self.method_lines)

        def visit_Assign(self, node: Assign):
            for target in node.targets:
                if isinstance(target, Name):
                    self.method_lines.add(target.lineno)
            self.generic_visit(node)

        def visit_Expr(self, node: Expr):
            if isinstance(node.value, Call):
                if isinstance(node.value.func, Attribute) and isinstance(node.value.args[0], Name):
                    self.method_lines.add(node.lineno)
            self.generic_visit(node)

    def apply(self, node):
        visitor = self.CommonLinesVisitor()
        visitor.visit(node)
        if visitor.common_lines:
            print("Lineas comunes:", visitor.common_lines)

    @classmethod
    def name(cls):
        return 'extract-setup'

