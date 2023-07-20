from anytree import Node, RenderTree

# Leer los elementos del archivo de texto y convertirlos en una lista
def values():
    mi_lista = []
    with open('datos.txt', 'r') as file:
        for linea in file:
            linea = linea.strip()
            mi_lista.append(linea)

    return mi_lista


def string_normalize(string, longinus=100):
    return string + (" "*(longinus-len(string)))

tokenValues = values().copy()
# Inicializamos arbol
def render_tree(node: Node) -> None:
    for pre, fill, node in RenderTree(node):
        print("%s%s" % (pre, node.name))



class Parser:
    def __init__(self, it):
        # define sync set
        self.sync_set = ["DEF","FOR","PRINT","IF","WHILE","$"]

        # set i/o
        self.input_tokens = it
        self.output_errors = []
        self.error_list = []

        # set process variables
        self.arbol = None
        self.current_node = None
        self.current_token = ""
        self.current_token_value = ""
        self.next_token()


    #Evaluamos el siguiente token
    def next_token(self):
        if len(self.input_tokens) > 0:
            self.current_token = self.input_tokens.pop(0)
        else:
            self.current_token = "$"  # Token de final de archivo

    #Añadimos los errores a una lista
    def add_error(self, error, symbol, at):
        self.output_errors.append(string_normalize(
            error, 19)+" "+string_normalize("\""+symbol+"\"", 16)+", at "+at)
        self.error_list.append((error, symbol, at))
        self.synchronize()

    def synchronize(self):
        while self.current_token not in self.sync_set and self.current_token != "$":
            self.next_token()


    def Program(self):
        #self.arbol = Node("STATEMENTLIST")
        #self.nodo_actual = self.arbol
        #if self.StatementList(self.nodo_actual):
        #    if self.current_token == "$":
        #        return True
        #return False
        
        #------
        self.arbol = Node("PROGRAM")
        self.nodo_actual = self.arbol
        while self.current_token != "$":
            self.StatementList(self.nodo_actual)
            self.synchronize()
        return len(self.output_errors) == 0
        
    def DefList(self):
        self.arbol  = Node("Def")

    def StatementList(self, node):
        #if self.Statement(node):
        #    if self.StatementList(node):
        #        return True
        #if self.current_token in ["$", "RKEY"]:
        #    return True
        #return False
        if not self.Statement(node):
            self.synchronize()
        if self.current_token not in ["$", "RKEY"]:
            self.StatementList(node)

    def Statement(self, node):
        if self.PrintStatement(node):
            return True
        elif self.DefStatement(node):
            return True
        elif self.AssignmentStatement(node):
            return True
        elif self.ForStatement(node):
            return True
        elif self.IfStatement(node):
            return True
        return False

    def PrintStatement(self, node):
        if self.current_token == "PRINT":
            print_node = Node("PRINTSTATEMENT", parent=node)
            self.next_token()
            if self.current_token == "LPAREN":
                aux_node = Node("LPAREN", parent=print_node)
                self.next_token()
                aux_node = Node("expression", parent=print_node)
                if self.Expression(aux_node):
                    if self.current_token == "RPAREN":
                        aux_node = Node("RPAREN", parent=print_node)
                        self.next_token()
                        return True
                    else:
                        self.add_error(
                            "Se esperaba un token", "RPAREN", "print statement"
                            
                        )
                else:
                    self.add_error(
                        "Se esperaba una expression", "any printable", "print statement"
                    )
            else:
                self.add_error(
                    "Se esperaba un token", "LPAREN", "print statement"
                )
        return False
    

    def DefStatement(self, node):
        if  self.current_token == "ID" and "DEF" in values():
            self.current_token = "DEF"

        if self.current_token == "DEF":
            def_node = Node("DEFSTATEMENT", parent=node)
            self.next_token()
            
            self.current_token = "ID"
            if self.current_token == "ID":
                id_node = Node("ID", parent=def_node)
                self.next_token()
                
                

                if self.Expression(def_node):
                    return True
                else:
                    self.add_error(
                    "Se esperaba una expresión",
                    "expression",
                    "def statement",
                        )

                self.current_token = "LPAREN"
                if self.current_token == "LPAREN":
                    self.next_token()

                    self.current_token = "RPAREN"
                    if self.current_token == "RPAREN" or self.ArgumentsList(id_node):
                        self.current_token = "RPAREN"
                        if self.current_token == "RPAREN":
                            self.next_token()

                            self.current_token = "COLON"
                            if self.current_token == "COLON":
                                self.next_token()
                                if self.Expression(def_node):
                                        return True
                                else:
                                    self.add_error(
                                        "Se esperaba una expresión",
                                        "expression",
                                        "def statement",
                                        )
                                
                                self.current_token = "NEWLINE"
                                if self.current_token == "NEWLINE":
                                    self.next_token()

                                    # Aquí puedes proporcionar una expresión válida para cumplir con el último if
                                    self.current_token = "EXPRESSION"
                                    if self.Expression(def_node):
                                        return True
                                    else:
                                        self.add_error(
                                            "Se esperaba una expresión",
                                            "expression",
                                            "def statement",
                                        )
                                else:
                                    self.add_error(
                                        "Se esperaba un token", "COLON", "def statement"
                                    )
                            else:
                                self.add_error(
                                    "Se esperaba un token", "RPAREN", "def statement"
                                )
                        else:
                            self.add_error(
                                "Se esperaba un token", "RPAREN", "def statement"
                            )
                    else:
                        self.add_error(
                            "Se esperaba una lista de argumentos o un paréntesis de cierre",
                            "arglist or RPAREN",
                            "def statement",
                        )
                else:
                    self.add_error(
                        "Se esperaba un token", "LPAREN", "def statement"
                    )
            else:
                self.add_error(
                    "Se esperaba un token", "ID", "def statement"
                )
        return False

    def AssignmentStatement(self, node):
        if self.current_token == "ID":
            assignment_node = Node("ASSIGNMENTSTATEMENT", parent=node)
            aux_node = Node("ID", parent=assignment_node)
            self.next_token()
            if self.current_token == "ASSIGN":
                aux_node = Node("expression", parent=assignment_node)
                self.next_token()
                if self.Expression(aux_node):
                    return True
                else:
                    self.add_error(
                        "Se esperaba una expression",
                        "any variable",
                        "assignment statement",
                    )
            else:
                self.add_error(
                    "Se esperaba un token", "ASSIGN", "assignment statement"
                )
        return False

    def ForStatement(self, node):
        if self.current_token == "FOR":
            for_node = Node("FORSTATEMENT", parent=node)
            self.next_token()
            if self.current_token == "ID":
                aux_node = Node("ID", parent=for_node)
                self.next_token()
                if self.current_token == "IN":
                    aux_node = Node("IN", parent=for_node)
                    self.next_token()
                    aux_node = Node("iterable", parent=for_node)
                    if self.Iterable(aux_node):
                        if self.current_token == "COLON":
                            aux_node = Node("COLON", parent=for_node)
                            self.next_token()
                            aux_node = Node("statements", parent=for_node)
                            self.nodo_actual = aux_node
                            if self.StatementList(self.nodo_actual):
                                return True
                            else:
                                self.add_error(
                                    "Se esperaba una lista",
                                    "any iterable",
                                    "for statement",
                                )
                        else:
                            self.add_error(
                                "Se esperaba un token",
                                "COLON",
                                "for statement",
                            )
                    else:
                        self.add_error(
                            "Se esperaba una lista",
                            "any iterable",
                            "for statement",
                        )
                else:
                    self.add_error("Se esperaba un token", "IN", "for statement")
            else:
                self.add_error(
                    "Se esperaba un IDENTIFIER", "any variable", "for statement"
                )
        return False

    def IfStatement(self, node):
        if self.current_token == "IF":
            if_node = Node("IFSTATEMENT", parent=node)
            self.next_token()
            aux_node = Node("expression", parent=if_node)
            if self.Expression(aux_node):
                if self.current_token == "COLON":
                    aux_node = Node("COLON", parent=if_node)
                    self.next_token()
                    aux_node = Node("statements", parent=if_node)
                    self.nodo_actual = aux_node
                    if self.StatementList(self.nodo_actual):
                        if self.ElifList(if_node):
                            return True
                        else:
                            self.add_error(
                                "Se esperaba un token",
                                "elif",
                                "if statement",
                            )
                else:
                    self.add_error(
                        "Se esperaba un token", "COLON", "if statement"
                    )
            else:
                self.add_error(
                    "Se esperaba una expression",
                    "any boolean",
                    "if statement",
                )
        return False

    def ElifList(self, node):
        if self.Elif(node):
            if self.ElifList(node):
                return True
            return True
        return False

    def Elif(self, node):
        if self.current_token == "ELIF":
            elif_node = Node("ELIF", parent=node)
            self.next_token()
            aux_node = Node("expression", parent=elif_node)
            if self.Expression(aux_node):
                if self.current_token == "COLON":
                    aux_node = Node("COLON", parent=elif_node)
                    self.next_token()
                    aux_node = Node("statements", parent=elif_node)
                    self.nodo_actual = aux_node
                    if self.StatementList(self.nodo_actual):
                        return True
                    else:
                        self.add_error(
                            "Se esperaba una lista de statements",
                            "elif",
                            "elif statement",
                        )
                else:
                    self.add_error(
                        "Se esperaba un token", "COLON", "elif statement"
                    )
            else:
                self.add_error(
                    "Se esperaba una expression",
                    "any boolean",
                    "elif statement",
                )
        return False

    def ElseStatement(self, node):
        if self.current_token == "ELSE":
            else_node = Node("ELSESTATEMENT", parent=node)
            self.next_token()
            if self.current_token == "COLON":
                aux_node = Node("COLON", parent=else_node)
                self.next_token()
                aux_node = Node("statements", parent=else_node)
                self.nodo_actual = aux_node
                if self.StatementList(self.nodo_actual):
                    return True
                else:
                    self.add_error(
                        "Se esperaba una lista de statements",
                        "else",
                        "else statement",
                    )
            else:
                self.add_error(
                    "Se esperaba un token", "COLON", "else statement"
                )
        if self.current_token in ["$", "PRINT", "ID", "FOR", "IF", "RKEY"]:
            return True
        return False

    def ComparisonOperator(self, node):
        if (
            self.current_token == "EQUAL"
            or self.current_token == "NOTEQUAL"
            or self.current_token == "LT"
            or self.current_token == "GT"
            or self.current_token == "LTE"
            or self.current_token == "GTE"
        ):
            aux_node = Node(self.current_token, parent=node)
            self.next_token()
            return True
        return False

    def BoolValue(self, node):
        if self.current_token == "FALSE" or self.current_token == "TRUE":
            aux_node = Node(self.current_token, parent=node)
            self.next_token()
            return True
        return False

    def List(self, node):
        if self.current_token == "LBRACKET":
            aux_node = Node("LBRACKET", parent=node)
            self.next_token()
            if self.ExpressionList(node):
                if self.current_token == "RBRACKET":
                    aux_node = Node("RBRACKET", parent=node)
                    self.next_token()
                    return True
                else:
                    self.add_error(
                        "Se esperaba un token", "RBRACKET", "list expression"
                    )
        return False

    def ExpressionList(self, node):
        if self.Expression(node):
            if self.ExpressionListTail(node):
                return True
        if self.current_token == "RBRACKET":
            return True
        return False

    def ExpressionListTail(self, node):
        if self.current_token == "COMMA":
            self.next_token()
            if self.Expression(node):
                if self.ExpressionListTail(node):
                    return True
        if self.current_token == "RBRACKET":
            return True
        return False

    def Expression(self, node):
        if self.OrExpression(node):
            if self.ExpressionPrima(node):
                return True
        return False

    def ExpressionPrima(self, node):
        if self.current_token == "IF":
            aux_node = Node("IF", parent=node)
            self.next_token()
            if self.AndExpression(node):
                if self.current_token == "ELSE":
                    aux_node = Node("ELSE", parent=node)
                    self.next_token()
                    if self.AndExpression(node):
                        if self.ExpressionPrima(node):
                            return True
                else:
                    self.add_error(
                        "Se esperaba un token", "ELSE", "expression"
                    )
        if (
            self.current_token in ["RBRACKET", "$", "PRINT", "ID", "FOR", "IF", "LBRACE", "COMMA"]
        ):
            return True
        return False

    def OrExpression(self, node):
        if self.AndExpression(node):
            if self.OrExpressionPrima(node):
                return True
        return False

    def OrExpressionPrima(self, node):
        if self.current_token == "OR":
            aux_node = Node("OR", parent=node)
            self.next_token()
            if self.AndExpression(node):
                if self.OrExpressionPrima(node):
                    return True
        if (
            self.current_token in ["RBRACKET", "$", "PRINT", "ID", "FOR", "IF", "LBRACE", "COMMA", "IF", "ELSE"]
        ):
            return True
        return False

    def AndExpression(self, node):
        if self.NotExpression(node):
            if self.AndExpressionPrima(node):
                return True
        return False

    def AndExpressionPrima(self, node):
        if self.current_token == "AND":
            aux_node = Node("AND", parent=node)
            self.next_token()
            if self.NotExpression(node):
                if self.AndExpressionPrima(node):
                    return True
        if (
            self.current_token in ["RBRACKET", "$", "PRINT", "ID", "FOR", "IF", "LBRACE", "COMMA", "IF", "ELSE", "OR"]
        ):
            return True
        return False

    def NotExpression(self, node):
        if self.current_token == "NOT":
            aux_node = Node("NOT", parent=node)
            self.next_token()
            if self.ComparisonExpression(node):
                return True
        if self.ComparisonExpression(node):
            return True
        return False

    def ComparisonExpression(self, node):
        if self.IntExpression(node):
            if self.ComparisonExpressionPrima(node):
                return True
        return False

    def ComparisonExpressionPrima(self, node):
        if self.ComparisonOperator(node):
            if self.IntExpression(node):
                return True
        if (
            self.current_token in [
                "RBRACKET",
                "$",
                "PRINT",
                "ID",
                "FOR",
                "IF",
                "LBRACE",
                "COMMA",
                "IF",
                "ELSE",
                "AND",
                "OR",
            ]
        ):
            return True
        return False

    def IntExpression(self, node):
        if self.Term(node):
            if self.IntExpressionPrima(node):
                return True
        return False

    def IntExpressionPrima(self, node):
        if self.current_token == "PLUS":
            aux_node = Node("PLUS", parent=node)
            self.next_token()
            if self.Term(node):
                if self.IntExpressionPrima(node):
                    return True
        if self.current_token == "MINUS":
            aux_node = Node("MINUS", parent=node)
            self.next_token()
            if self.Term(node):
                if self.IntExpressionPrima(node):
                    return True
        if (
            self.current_token
            in [
                "RBRACKET",
                "$",
                "PRINT",
                "ID",
                "FOR",
                "IF",
                "LBRACE",
                "COMMA",
                "IF",
                "ELSE",
                "AND",
                "OR",
                "EQUAL",
                "NOTEQUAL",
                "LT",
                "GT",
                "LTE",
                "GTE",
            ]
        ):
            return True
        return False

    def Term(self, node):
        if self.Factor(node):
            if self.TermPrima(node):
                return True
        return False

    def TermPrima(self, node):
        if self.current_token == "MULT":
            aux_node = Node("MULT", parent=node)
            self.next_token()
            if self.Factor(node):
                if self.TermPrima(node):
                    return True
        if self.current_token == "DIV":
            aux_node = Node("DIV", parent=node)
            self.next_token()
            if self.Factor(node):
                if self.TermPrima(node):
                    return True
        if (
            self.current_token
            in [
                "RBRACKET",
                "$",
                "PRINT",
                "ID",
                "FOR",
                "IF",
                "LBRACE",
                "COMMA",
                "IF",
                "ELSE",
                "AND",
                "OR",
                "EQUAL",
                "NOTEQUAL",
                "LT",
                "GT",
                "LTE",
                "GTE",
                "PLUS",
                "MINUS",
            ]
        ):
            return True
        return False
    
    def display_errors(self):
        print("Total errors:", len(self.error_list))
        for error in self.error_list:
            print("Error:", error[0])
            print("Symbol:", error[1])
            print("At:", error[2])
            print()

    def Factor(self, node):
        if self.current_token == "LPAREN":
            factor_node = Node("LPAREN", parent=node)
            self.next_token()
            if self.Expression(node):
                if self.current_token == "RPAREN":
                    factor_node = Node("RPAREN", parent=node)
                    return True
                else:
                    self.add_error(
                        "Se esperaba un token", "RPAREN", "factor expression"
                    )
        if self.current_token == "ID":
            aux_node = Node("ID", parent=node)
            self.next_token()
            return True
        if self.BoolValue(node):
            return True
        if self.List(node):
            return True
        if self.current_token == "INTEGER_CONST":
            aux_node = Node("INTEGER_CONST", parent=node)
            self.next_token()
            return True
        if (
            self.current_token
            in ["RPAREN", "$", "PRINT", "ID", "FOR", "IF", "LBRACE", "COMMA"]
        ):
            return True
        return False



    #Funcion que arma todo
    def parse(self):
        self.Program()
        if len(self.input_tokens) > 0:
            self.arbol = None
            while True:
                self.synchronize()
                if self.current_token == "$":
                    break
                self.Program()
            print("error(s): ", len(self.output_errors))
            for i in self.output_errors:
                print(i)
        else:
            print("abstract syntax tree: ")
            render_tree(self.arbol)

    def listaErroress(self):
        while self.current_token != "$":
            self.Program()
            self.synchronize()

        self.display_errors()

    def parse_all_tokens(self):
        while self.current_token != "$":
            self.next_token()
        print("Lista de errores:")
        for error in self.output_errors:
            print(error)
    def print_errors(self):
        if len(self.output_errors) > 0:
            print("Errors found during parsing:")
            for error in self.output_errors:
                print(error)
        else:
            print("No errors found during parsing.")



