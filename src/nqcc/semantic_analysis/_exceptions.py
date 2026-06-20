from nqcc.frontend.parser import (
    SourceBreakNode,
    SourceContinueNode,
    SourceDeclarationNode,
    SourceExpressionNode,
    SourceFunctionCallNode,
    SourceFunctionDeclarationNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
)


class SemanticAnalysisDuplicateDeclaration(ValueError):
    def __init__(self, *, decl: SourceDeclarationNode):
        self.decl = decl

        identifier = "Unknown Decl!"
        match decl:
            case SourceVariableDeclarationNode():
                identifier = decl.identifier.identifier
            case SourceFunctionDeclarationNode():
                identifier = decl.identifier

        message = f"Duplicate declaration of '{identifier}' at {decl.start_position}"

        self.message = message
        super().__init__(self.message)


class SemanticAnalysisBadLValue(ValueError):
    def __init__(self, *, expr: SourceExpressionNode):
        self.expression = expr
        message = f"Not an lvalue at {self.expression.start_position}"
        self.message = message
        super().__init__(self.message)


class SemanticAnalysisUnknownIdentifier(ValueError):
    def __init__(self, *, var: SourceVarNode | SourceFunctionCallNode):
        self.var = var
        message = f"Unknown identifier '{var.identifier}' at {var.start_position}"
        self.message = message
        super().__init__(self.message)


class SemanticAnalysisOutsideLoop(ValueError):
    def __init__(self, *, stmt: SourceBreakNode | SourceContinueNode):
        self.stmt = stmt
        message = f"Outside loop: {stmt.node_type} {stmt.start_position}"
        self.message = message
        super().__init__(self.message)
