import pytest

from nqcc.parser import (
    SourceConstantIntNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    TokenTape,
    parse_declaration,
)
from nqcc.semantic_analysis import (
    SemanticAnalysisDuplicateDeclaration,
    IdentifierResolver,
)


class TestDeclarations:
    def test_smoke_no_init(self):
        target = IdentifierResolver()
        variable_map = {}

        decl = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )

        updated = target.resolve_declaration(decl, variable_map)
        assert isinstance(updated, SourceVariableDeclarationNode)
        assert updated.start_position == 10
        assert updated.identifier == SourceVarNode(start_position=11, identifier="a.0")
        assert updated.initial is None
        assert len(variable_map) == 1

    def test_decl_with_init(self):
        target = IdentifierResolver()
        variable_map = {}

        program_str = "int a = 1;"

        token_tape = TokenTape.from_c_source(program_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceVariableDeclarationNode)

        result = target.resolve_declaration(decl, variable_map)
        assert isinstance(result, SourceVariableDeclarationNode)
        assert result.start_position == 0
        assert result.identifier == SourceVarNode(start_position=4, identifier="a.0")
        assert isinstance(result.initial, SourceConstantIntNode)
        assert result.initial.value == 1
        assert len(variable_map) == 1

    def test_two_decl(self):
        target = IdentifierResolver()

        decl0 = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )

        variable_map = {}
        updated0 = target.resolve_declaration(decl0, variable_map)
        assert isinstance(updated0, SourceVariableDeclarationNode)
        assert updated0.start_position == 10
        assert updated0.identifier == SourceVarNode(start_position=11, identifier="a.0")
        assert updated0.initial is None

        decl1 = SourceVariableDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="b"),
            initial=None,
        )

        updated1 = target.resolve_declaration(decl1, variable_map)
        assert isinstance(updated1, SourceVariableDeclarationNode)
        assert updated1.start_position == 12
        assert updated1.identifier == SourceVarNode(start_position=13, identifier="b.1")
        assert updated1.initial is None

    def test_duplicate_name(self):
        target = IdentifierResolver()
        variable_map = {}

        decl0 = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl0, variable_map)

        decl1 = SourceVariableDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="a"),
            initial=None,
        )

        with pytest.raises(SemanticAnalysisDuplicateDeclaration) as saduperr:
            _ = target.resolve_declaration(decl1, variable_map)
        assert saduperr.value.decl == decl1
        assert saduperr.value.message == "Duplicate declaration of 'a' at 12"
