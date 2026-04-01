from nqcc.parser import SourceDeclarationNode


class SemanticAnalysisDuplicateDeclaration:
    def __init__(self, *, decl: SourceDeclarationNode):
        self.decl = decl
        message = f"Duplicate declaration of '{decl.identifier}' at {decl.start_position}"
        self.message = message
        super().__init__(self.message)
