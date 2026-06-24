import pytest
from nqcc.frontend.parser import (
    SourceAssignmentNode,
    SourceConstantIntNode,
    SourceFunctionCallNode,
    SourceFunctionDeclarationNode,
    SourceTernaryExpressonNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    TokenTape,
    parse_declaration,
    parse_expression,
)
from nqcc.frontend.semantic_analysis import (
    IdentifierResolver,
    SemanticAnalysisBadLValue,
    SemanticAnalysisUnknownIdentifier,
)


class TestExpressions:
    def test_assignment(self):
        target = IdentifierResolver()
        identifier_map = {}

        # Make sure 'a' is declared
        decl_a = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
            storage_class=None,
        )
        _ = target.resolve_declaration(decl_a, identifier_map, at_file_scope=False)

        # Our assignment
        c_str = "a=1;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert isinstance(assignment, SourceAssignmentNode)

        result = target.resolve_expression(assignment, identifier_map)
        assert isinstance(result, SourceAssignmentNode)
        assert isinstance(result.left, SourceVarNode)
        assert result.left.identifier == "a.0"
        assert isinstance(result.right, SourceConstantIntNode)
        assert result.right.value == 1

    def test_assignment_undeclared(self):
        target = IdentifierResolver()
        identifier_map = {}
        c_str = "a=1;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(assignment, SourceAssignmentNode)

        with pytest.raises(SemanticAnalysisUnknownIdentifier) as sauv:
            _ = target.resolve_expression(assignment, identifier_map)
        assert sauv.value.message == "Unknown identifier 'a' at 0"

    def test_assignment_badlvalue(self):
        target = IdentifierResolver()
        identifier_map = {}
        c_str = "1=1+2;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(assignment, SourceAssignmentNode)

        with pytest.raises(SemanticAnalysisBadLValue) as sablv:
            _ = target.resolve_expression(assignment, identifier_map)
        assert sablv.value.message == "Not an lvalue at 0"

    def test_ternary(self):
        target = IdentifierResolver()
        identifier_map = {}
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
                storage_class=None,
            )
            _ = target.resolve_declaration(decl, identifier_map, at_file_scope=False)

        result = target.resolve_expression(ternary_expr, identifier_map)
        assert isinstance(result, SourceTernaryExpressonNode)
        assert result.condition == SourceVarNode(start_position=0, identifier="a.0")
        assert result.then == SourceVarNode(start_position=2, identifier="b.1")
        assert result.otherwise == SourceVarNode(start_position=4, identifier="c.2")


class TestFunctionCalls:
    def test_simple(self):
        target = IdentifierResolver()
        identifier_map = {}
        c_str = "some_func();"
        token_tape = TokenTape.from_c_source(c_str)
        func_call_expr = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(func_call_expr, SourceFunctionCallNode)
        assert func_call_expr.identifier == "some_func"
        assert len(func_call_expr.args) == 0

        # Ensure function is defined
        decl = SourceFunctionDeclarationNode(
            start_position=123,
            identifier="some_func",
            params=[],
            body=None,
            storage_class=None,
        )

        _ = target.resolve_declaration(decl, identifier_map, at_file_scope=False)
        assert "some_func" in identifier_map

        result = target.resolve_expression(func_call_expr, identifier_map)
        assert isinstance(result, SourceFunctionCallNode)
        assert result.identifier == func_call_expr.identifier
        assert len(result.args) == 0

    def test_onearg_constant(self):
        target = IdentifierResolver()
        identifier_map = {}

        decl_str = "int some_func(int a);"
        token_tape = TokenTape.from_c_source(decl_str)
        decl = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0
        assert isinstance(decl, SourceFunctionDeclarationNode)

        _ = target.resolve_function_declaration(decl, identifier_map)

        call_str = "some_func(2);"
        token_tape = TokenTape.from_c_source(call_str)
        call_expr = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(call_expr, SourceFunctionCallNode)

        result = target.resolve_expression(call_expr, identifier_map)
        assert result.identifier == call_expr.identifier
        assert len(result.args) == 1
        arg0 = result.args[0]
        assert isinstance(arg0, SourceConstantIntNode)
        assert arg0.value == 2

    def test_onearg_variable(self):
        target = IdentifierResolver()
        identifier_map = {}

        func_decl_str = "int some_func(int a);"
        token_tape = TokenTape.from_c_source(func_decl_str)
        decl = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0
        assert isinstance(decl, SourceFunctionDeclarationNode)
        _ = target.resolve_function_declaration(decl, identifier_map)

        var_decl_str = "int a = 2;"
        token_tape = TokenTape.from_c_source(var_decl_str)
        var_decl = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0
        assert isinstance(var_decl, SourceVariableDeclarationNode)
        var_resolved = target.resolve_declaration(var_decl, identifier_map, at_file_scope=False)
        assert var_resolved.identifier.identifier == "a.1"

        call_str = "some_func(a);"
        token_tape = TokenTape.from_c_source(call_str)
        call_expr = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(call_expr, SourceFunctionCallNode)

        result = target.resolve_expression(call_expr, identifier_map)
        assert result.identifier == call_expr.identifier
        assert len(result.args) == 1
        arg0 = result.args[0]
        assert isinstance(arg0, SourceVarNode)
        assert arg0.identifier == "a.1"
