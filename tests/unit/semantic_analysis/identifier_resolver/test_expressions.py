import pytest

from nqcc.parser import (
    SourceAssignmentNode,
    SourceConstantIntNode,
    SourceTernaryExpressonNode,
    SourceVariableDeclarationNode,
    SourceVarNode,SourceFunctionCallNode,
    TokenTape,
    parse_expression,
)
from nqcc.semantic_analysis import (
    IdentifierResolver,
    SemanticAnalysisBadLValue,
    SemanticAnalysisUnknownVariable,
)


class TestExpressions:
    def test_assignment(self):
        target = IdentifierResolver()
        variable_map = {}

        # Make sure 'a' is declared
        decl_a = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_a, variable_map)

        # Our assignment
        c_str = "a=1;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert isinstance(assignment, SourceAssignmentNode)

        result = target.resolve_expression(assignment, variable_map)
        assert isinstance(result, SourceAssignmentNode)
        assert isinstance(result.left, SourceVarNode)
        assert result.left.identifier == "a.0"
        assert isinstance(result.right, SourceConstantIntNode)
        assert result.right.value == 1

    def test_assignment_undeclared(self):
        target = IdentifierResolver()
        variable_map = {}
        c_str = "a=1;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(assignment, SourceAssignmentNode)

        with pytest.raises(SemanticAnalysisUnknownVariable) as sauv:
            _ = target.resolve_expression(assignment, variable_map)
        assert sauv.value.message == "Unknown identifier 'a' at 0"

    def test_assignment_badlvalue(self):
        target = IdentifierResolver()
        variable_map = {}
        c_str = "1=1+2;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(assignment, SourceAssignmentNode)

        with pytest.raises(SemanticAnalysisBadLValue) as sablv:
            _ = target.resolve_expression(assignment, variable_map)
        assert sablv.value.message == "Not an lvalue at 0"

    def test_ternary(self):
        target = IdentifierResolver()
        variable_map = {}
        c_str = "a?b:c;"
        token_tape = TokenTape.from_c_source(c_str)
        ternary_expr = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(ternary_expr, SourceTernaryExpressonNode)

        for decl_var in ["a", "b", "c"]:
            decl = SourceVariableDeclarationNode(
                start_position=ord(decl_var),
                identifier=SourceVarNode(start_position=ord(decl_var) + 32, identifier=decl_var),
                initial=None,
            )
            _ = target.resolve_declaration(decl, variable_map)

        result = target.resolve_expression(ternary_expr, variable_map)
        assert isinstance(result, SourceTernaryExpressonNode)
        assert result.condition == SourceVarNode(start_position=0, identifier="a.0")
        assert result.then == SourceVarNode(start_position=2, identifier="b.1")
        assert result.otherwise == SourceVarNode(start_position=4, identifier="c.2")

class TestFunctionCalls:
    def test_simple(self):
        target = IdentifierResolver()
        variable_map = {}
        c_str = "some_func();"
        token_tape = TokenTape.from_c_source(c_str)
        func_call_expr = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(func_call_expr, SourceFunctionCallNode)
        assert func_call_expr.identifier =="some_func"
        assert len(func_call_expr.args) == 0

        result = target.resolve_expression(func_call_expr, variable_map)
        assert isinstance(result, SourceFunctionCallNode)
        assert result.identifier == func_call_expr.identifier
        assert len(result.args) == 0