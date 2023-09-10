from _ast import AST
from ast import *
from core.rewriter import RewriterCommand


class InlineCommand(RewriterCommand):

    class InlineTransformer(NodeTransformer):
        def __init__(self):
            self.variables = {}
            self.usage_count = {}

        def visit_Assign(self, node):
            if isinstance(node.targets[0], Name):
                var_name = node.targets[0].id
                var_value = self.visit(node.value)
                # Cuento la cantidad de veces que se ocupa la variable
                self.usage_count[var_name] = len([stmt for stmt in walk(self.parent) if isinstance(stmt, Name) and stmt.id == var_name and stmt != node.targets[0]])
                if self.usage_count[var_name] == 1:
                    self.variables[var_name] = var_value
                else:
                    return node
                return None
            return node

        def visit_Name(self, node):
            if isinstance(node, Name):
                if node.id in self.variables:
                    return self.variables[node.id]
            return node

        def visit_BinOp(self, node):
            if isinstance(node.left, Name) and node.left.id in self.variables:
                node.left = self.variables[node.left.id]
            if isinstance(node.right, Name) and node.right.id in self.variables:
                node.right = self.variables[node.right.id]
            return node

    def apply(self, node):
        transformer = self.InlineTransformer()
        transformer.parent = node
        transformed = transformer.visit(node)
        new_tree = fix_missing_locations(transformed)
        return new_tree
