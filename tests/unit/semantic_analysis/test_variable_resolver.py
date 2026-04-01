import pytest

from nqcc.parser import SourceDeclarationNode, SourceVarNode
from nqcc.semantic_analysis import VariableResolver, SemanticAnalysisDuplicateDeclaration


class TestDeclarations:
    def test_smoke_no_init(self):
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

    def test_two_decl(self):
        target = VariableResolver()

        decl0 = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )

        updated0 = target.resolve_declaration(decl0)
        assert isinstance(updated0, SourceDeclarationNode)
        assert updated0.start_position == 10
        assert updated0.identifier == SourceVarNode(start_position=11, identifier="a.0")
        assert updated0.initial is None

        decl1 = SourceDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="b"),
            initial=None,
        )

        updated1 = target.resolve_declaration(decl1)
        assert isinstance(updated1, SourceDeclarationNode)
        assert updated1.start_position == 12
        assert updated1.identifier == SourceVarNode(start_position=13, identifier="b.1")
        assert updated1.initial is None

    def test_duplicate_name(self):
        target = VariableResolver()

        decl0 = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl0)

        decl1 = SourceDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="a"),
            initial=None,
        )

        with pytest.raises(SemanticAnalysisDuplicateDeclaration) as saduperr:
            _ = target.resolve_declaration(decl1)
        assert saduperr.value.decl == decl1
        assert saduperr.value.message == "Duplicate declaration of 'a' at 12"
