from nqcc.parser import SourceDeclarationNode, SourceFunctionNode, SourceVarNode

from ._exceptions import SemanticAnalysisDuplicateDeclaration


class VariableResolver:
    def __init__(self):
        self._variable_map: dict[str, str] = {}
        self._counter = 0

    def resolve_declaration(self, decl: SourceDeclarationNode):
        assert isinstance(decl, SourceDeclarationNode)

        orig_name = decl.identifier.identifier
        if orig_name in self._variable_map:
            raise SemanticAnalysisDuplicateDeclaration(decl=decl)
        unique_name = f"{orig_name}.{self._counter}"
        self._counter += 1
        self._variable_map[orig_name] = unique_name
        if decl.initial is not None:
            raise NotImplementedError("TBD")

        nxt_var = SourceVarNode(
            start_position=decl.identifier.start_position, identifier=unique_name
        )
        return SourceDeclarationNode(
            start_position=decl.start_position, identifier=nxt_var, initial=None
        )
