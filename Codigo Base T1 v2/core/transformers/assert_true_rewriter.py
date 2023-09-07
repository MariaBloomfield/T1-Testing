from ast import *
import ast
from core.rewriter import RewriterCommand


class AssertTrueCommand(RewriterCommand):
    
    class Transformer(NodeTransformer):
        def visit_Call(self, node):
            if (
                isinstance(node.func, Attribute) and
                isinstance(node.func.value, Name) and
                node.func.value.id == 'self' and
                node.func.attr == 'assertEquals' and
                len(node.args) == 2 and
                isinstance(node.args[1], Constant) and
                node.args[1].value is True
            ):
                return Call(
                    func=Attribute(
                        value=Name(id='self', ctx=Load()),
                        attr='assertTrue',
                        ctx=Load()
                    ),
                    args=[node.args[0]],
                    keywords=[]
                )
            return node
    
    def apply(self, node):
        transformer = self.Transformer()
        transformed = transformer.visit(node)
        return transformed