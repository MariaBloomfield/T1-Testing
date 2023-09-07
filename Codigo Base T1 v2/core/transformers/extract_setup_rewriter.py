from _ast import AST, FunctionDef, Module
from ast import *
import ast
from typing import Any
from core.rewriter import RewriterCommand



class ExtractSetupCommand(RewriterCommand):

    class ExtractSetupTransformer(NodeTransformer):
        def visit_Module(self, node):
            setup_body = []
            for child in node.body:
                if isinstance(child, FunctionDef) and child.name != 'setUp':
                    duplicates = self.find_duplicates(child.body)
                    if duplicates:
                        setup_body.extend(duplicates)
                        child.body = [stmt for stmt in child.body if stmt not in duplicates]
            if setup_body:
                setup = FunctionDef(name='setUp', args=arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=setup_body, decorator_list=[])
                new_body = node.body[:]
                new_body.insert(0, setup)
                return copy_location(node, Module(body=new_body))
            return node
        
        def find_duplicates(self, body):
            duplicates = []
            statements = {}
            for node in body:
                if isinstance(node, Assign) and isinstance(node.targets[0], Name):
                    key = self.generate_key(node)
                    if key in statements:
                        duplicates.append(node)
                    else:
                        statements[key] = node
            return duplicates
        
        def generate_key(self, node):
            if isinstance(node.value, Num):
                return node.__repr__()
            
        def generic_visit(self, node):
            return NodeTransformer.generic_visit(self, node)
            

    def apply(self, node):
        extractor = self.ExtractSetupTransformer()
        return extractor.visit(node)

    @classmethod
    def name(cls):
        return 'extract-setup'
