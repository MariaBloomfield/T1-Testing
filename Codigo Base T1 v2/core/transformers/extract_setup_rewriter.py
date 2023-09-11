from _ast import AST, ClassDef, FunctionDef, Module
from ast import *
import ast
from typing import Any
from core.rewriter import RewriterCommand
import copy


class ExtractSetupVisitor(NodeVisitor):

    def __init__(self):
            super().__init__()
            self.lista_funciones = []
            self.lista_variables = []
            self.variables_duplicadas = []

    # Reviso las funciones de una clase
    def visit_ClassDef(self, node: ClassDef):
        contador = 0
        self.generic_visit(node)
        cant_funciones = len(self.lista_funciones)
        hacer_break = False
        # Recorro la lista de funciones, y veo si hay duplicados
        for i in range(cant_funciones):
            for j in range(i+1, cant_funciones):
                largo = len(self.lista_funciones[i])
                for k in range(largo):
                    print(self.lista_funciones[i][k], self.lista_funciones[j][k])
                    if self.lista_funciones[i][k] == self.lista_funciones[j][k]:
                        contador += 1
                        print("Duplicado en linea:", contador)
                    else:
                        print("No hay duplicados en la linea:", contador)
                        hacer_break = True
                        break
                if hacer_break:
                    break
            if hacer_break:
                break

        print("CONTADOR:", contador)
        print("LISTA FUNCIONES:", self.lista_funciones)
        # Agrego a las variables duplicadas las primers n lineas de las funciones
        if contador > 0:
            for i in range(contador):
                self.variables_duplicadas.append(self.lista_funciones[0][i])
        
        # Elimino las variables duplicadas de cada función
        print("VARIABLES DUPLICADAS:", self.variables_duplicadas)
        return self.variables_duplicadas

    # Reviso las lineas de la funcion de una clase, y las agrego a una lista de listas
    def visit_FunctionDef(self, node: FunctionDef):
        lista_funcion = []
        for n in node.body:
            if isinstance(n, ast.Assign):
                for target in n.targets:
                    print("Estoy en assign imprimiendo el target", target)
                    print("Estoy en assign imprimiendo el target", target.id)
                    lista_funcion.append(target.id)
            elif isinstance(n, ast.Expr):
                if isinstance(n.value, ast.Call):
                    print(n.value.func)
                    if isinstance(n.value.func, ast.Attribute):
                        if isinstance(n.value.args[0], ast.Name):
                            variable = n.value.args[0].id
                            print("variable", variable)
                            print(n.value.func.attr)
                            lista_funcion.append((n.value.func.attr, variable))
                        elif isinstance(n.value.args[0], ast.Call):
                            print("ENTRE")
                            variable = n.value.func.value
                            print("var", variable)
                            print("otro", n.value.func.attr)
                            lista_funcion.append((n.value.func.attr, variable))
            else:
                print("ESTOY EN ELSE")
        self.lista_funciones.append(lista_funcion)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                # Reviso si la asignación de la variable contiene a otra variable:
                print("variable", target.id)
                print(node.value.value)
                # Encuentro la variable target.id en la lista de funciones, y la reemplazo por el valor de la variable
                for i in range(len(self.lista_funciones)):
                    for j in range(len(self.lista_funciones[i])):
                        if self.lista_funciones[i][j] == target.id:
                            self.lista_funciones[i][j] = (target.id, node.value.value)
        self.generic_visit(node)


class ExtractSetupTransformer(NodeTransformer):
    def __init__(self, variables_duplicadas):
        super().__init__()
        self.variables_duplicadas = variables_duplicadas
        self.cambiar_self = False
        print("VARIABLES DUPLICADAS:", self.variables_duplicadas)

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        setup_statements = []
        if len(self.variables_duplicadas) > 0:
            for item in self.variables_duplicadas:
                if isinstance(item, tuple):
                    print("ITEM:", item)
                    assign_stmt = Assign(
                        targets=[Attribute(value=Name(id='self', ctx=Load()), attr=item[0], ctx=Store())],
                        value=Constant(value=item[1]),
                    )
                    setup_statements.append(assign_stmt)
        print("SETUP STATEMENTS:", setup_statements)
        if len(setup_statements) == 0:
            return node
        else: 
            self.cambiar_self = True
            nueva_funcion = FunctionDef(
                name="setUp",
                args=arguments(posonlyargs=[], args=[arg(arg='self')], kwonlyargs=[], kw_defaults=[], defaults=[]),
                body=setup_statements,
                decorator_list=[],
            )

        # Crea una nueva lista de elementos para node.body sin las líneas a eliminar
        new_body = [nueva_funcion] + [self.visit(n) for n in node.body]
        
        # Reemplaza node.body con la nueva lista
        node.body = new_body
        print("BODY:", node.body)
        return node

    def visit_FunctionDef(self, node):
        node = copy.deepcopy(node)

        # Itera sobre las declaraciones en el cuerpo de la función
        new_body = []
        for statement in node.body:
            print("statement", statement)
            # Comprueba si la declaración debe eliminarse
            if not self.should_remove_node(statement):
                # Reemplaza las variables en la asignación con self.variable
                if self.cambiar_self:
                    if isinstance(statement, ast.Assign):
                        new_targets = []
                        for target in statement.targets:
                            if isinstance(target, ast.Name):
                                print("TARGET ID:", target.id)
                                for item in self.variables_duplicadas:
                                    if isinstance(item, tuple):
                                        if target.id == item[0]:
                                            new_targets.append(Attribute(value=Name(id='self', ctx=Load()), attr=target.id, ctx=Store()))
                                            break
                                    else:
                                        if target.id == item:
                                            new_targets.append(Attribute(value=Name(id='self', ctx=Load()), attr=target.id, ctx=Store()))
                                            break
                                # and target.id in self.variables_duplicadas:
                                # new_targets.append(Attribute(value=Name(id='self', ctx=Load()), attr=target.id, ctx=Store()))
                            else:
                                new_targets.append(target)
                        statement.targets = new_targets
                # Reemplaza las variables en las llamadas con self.variable
                if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                    print("Imprimiendo", statement.value)
                    self.replace_variables_in_call(statement.value)

                new_body.append(statement)

        # Actualiza el cuerpo de la función con las declaraciones restantes
        node.body = new_body

        self.generic_visit(node)
        return node

    def replace_variables_in_call(self, call_node):
        if isinstance(call_node, ast.Call):
            new_args = []
            for arg in call_node.args:
                if isinstance(arg, ast.Name):
                    if self.cambiar_self:
                        # Si el argumento es un nombre de variable, verifica si está en la lista de duplicados
                        for item in self.variables_duplicadas:
                            if isinstance(item, tuple):
                                if arg.id == item[0]:
                                    # Reemplaza el nombre de la variable con self.nombre
                                    new_args.append(Attribute(value=Name(id='self', ctx=Load()), attr=arg.id, ctx=Load()))
                                    break
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
            call_node.args = new_args
            # Recursivamente, procesa cualquier atributo en la función
            if isinstance(call_node.func, ast.Attribute):
                self.replace_variables_in_call(call_node.func)
            # Procesa cualquier otro argumento recursivamente
            for arg in call_node.args:
                self.replace_variables_in_call(arg)

    def should_remove_node(self, node):
        print(self.variables_duplicadas)
        # Verifica si una declaración debe eliminarse
        if isinstance(node, ast.Assign):
            print("es una signación")
            for target in node.targets:
                if isinstance(target, ast.Name):
                    for item in self.variables_duplicadas:
                        if isinstance(item, tuple):
                            if target.id == item[0]:
                                print("Esta en variables duplicadas")
                                return True
        return False


class ExtractSetupCommand(RewriterCommand):
    def apply(self, node):
        visitor = ExtractSetupVisitor()
        visitor.visit(node)
        extractor = ExtractSetupTransformer(visitor.variables_duplicadas)
        new_tree = fix_missing_locations(extractor.visit(node))
        return new_tree

    @classmethod
    def name(cls):
        return 'extract-setup'
