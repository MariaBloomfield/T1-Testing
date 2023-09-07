from _ast import AST
from ast import *
from core.rewriter import RewriterCommand

class InlineCommand(RewriterCommand):

    class InlineTransformer(NodeTransformer):
        def __init__(self):
            self.variables = {}

        def visit_Assign(self, node):
            if isinstance(node.targets[0], Name):
                var_name = node.targets[0].id
                var_value = self.visit(node.value)
                self.variables[var_name] = var_value
                return None
            return node
        
        def visit_Name(self, node):
            if isinstance(node, Name):
                if node.id in self.variables:
                    return self.variables[node.id]
            return node

    def apply(self, node):
        transformer = self.InlineTransformer()
        while True:
            transformed = transformer.visit(node)
            if transformed == node:
                break
            node = transformed
        return transformed