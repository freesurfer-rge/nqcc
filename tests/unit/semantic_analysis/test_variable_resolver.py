import pytest

from nqcc.parser import (
    SourceConstantIntNode,
    SourceDeclarationNode,
    SourceVarNode,SourceAssignmentNode,
    TokenTape,
    parse_declaration, parse_expression
)
from nqcc.semantic_analysis import SemanticAnalysisDuplicateDeclaration, VariableResolver, SemanticAnalysisUnknownVariable


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

    def test_decl_with_init(self):
        target = VariableResolver()
        program_str = "int a = 1;"

        token_tape = TokenTape.from_c_source(program_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceDeclarationNode)

        result = target.resolve_declaration(decl)
        assert isinstance(result, SourceDeclarationNode)
        assert result.start_position == 0
        assert result.identifier == SourceVarNode(start_position=4, identifier="a.0")
        assert isinstance(result.initial, SourceConstantIntNode)
        assert result.initial.value == 1

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

class TestExpressions:
    def test_assignment(self):
        target = VariableResolver()

        # Make sure 'a' is declared
        decl_a = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_a)

        # Our assignment
        c_str = "a=1;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert isinstance(assignment, SourceAssignmentNode)

        result = target.resolve_expression(assignment)
        assert isinstance(result, SourceAssignmentNode)
        assert isinstance(result.left, SourceVarNode)
        assert result.left.identifier == "a.0"
        assert isinstance(result.right, SourceConstantIntNode)
        assert result.right.value == 1

    def test_assignment_undeclared(self):
        target = VariableResolver()# Our assignment
        c_str = "a=1;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert isinstance(assignment, SourceAssignmentNode)

        with pytest.raises(SemanticAnalysisUnknownVariable) as sauv:
            _ = target.resolve_expression(assignment)
        assert sauv.value.message == "Unknown identifier 'a' at 0"
