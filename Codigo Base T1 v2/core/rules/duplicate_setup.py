import ast
from ..rule import *


class DuplicatedSetupVisitor(WarningNodeVisitor):
    #  Implementar Clase
    def __init__(self):
        super().__init__()
        self.lista_funciones = []
        self.lista_variables = []

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
        

        print(contador)
        if contador > 0:
            print('DuplicatedSetup ' + str(contador) + ' there are ' + str(contador) + ' duplicated setup statements')
            self.addWarning('DuplicatedSetup', str(contador), 'there are ' + str(contador) + ' duplicated setup statements')
        self.generic_visit(node)
    
    # Reviso las lineas de la funcion de una clase, y las agrego a una lista de listas
    def visit_FunctionDef(self, node: FunctionDef):
        lista_funcion = []
        for n in node.body:
            if isinstance(n, ast.Assign):
                for target in n.targets:
                    print(target.id)
                    lista_funcion.append(target.id)
            elif isinstance(n, ast.Expr):
                if isinstance(n.value, ast.Call):
                    if isinstance(n.value.func, ast.Attribute) and isinstance(n.value.args[0], ast.Name):
                        variable = n.value.args[0].id
                        print(n.value.func.attr)
                        lista_funcion.append((n.value.func.attr, variable))
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


class DuplicatedSetupRule(Rule):
    #  Implementar Clase
    def analyze(self, node):
        visitor = DuplicatedSetupVisitor()
        visitor.visit(node)
        return visitor.warningsList()

    @classmethod
    def name(cls):
        return 'duplicate-setup'
