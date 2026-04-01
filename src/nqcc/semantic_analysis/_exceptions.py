from nqcc.parser import SourceDeclarationNode, SourceExpressionNode, SourceVarNode


class SemanticAnalysisDuplicateDeclaration(ValueError):
    def __init__(self, *, decl: SourceDeclarationNode):
        self.decl = decl
        message = (
            f"Duplicate declaration of '{decl.identifier.identifier}' at {decl.start_position}"
        )
        self.message = message
        super().__init__(self.message)


class SemanticAnalysisBadLValue(ValueError):
    def __init__(self, *, expr: SourceExpressionNode):
        self.expression = expr
        message = f"Not an lvalue at {self.expression.start_position}"
        self.message = message
        super().__init__(self.message)


class SemanticAnalysisUnknownVariable(ValueError):
    def __init__(self, *, var: SourceVarNode):
        self.var = var
        message = f"Unknown identifier '{var.identifier}' at {var.start_position}"
        self.message = message
        super().__init__(self.message)
