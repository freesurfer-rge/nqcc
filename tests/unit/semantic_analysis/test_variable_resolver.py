from nqcc.parser import SourceDeclarationNode, SourceVarNode
from nqcc.semantic_analysis import VariableResolver, SemanticAnalysisDuplicateDeclaration


class TestDeclarations:
    def test_smoke(self):
        target = VariableResolver()

        decl = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )

        updated = target.resolve_declaration(decl)
        assert isinstance(updated, SourceDeclarationNode)
        assert updated.start_position == 10
        assert updated.identifier == SourceVarNode(start_position=11, identifier="a.0")
        assert updated.initial is None
