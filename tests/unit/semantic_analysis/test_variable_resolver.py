import pytest

from nqcc.parser import (
    SourceAdd,
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceConstantIntNode,
    SourceDeclarationNode,
    SourceExpressionStatementNode,
    SourceNullStatementNode,
    SourceReturnNode,
    SourceVarNode,
    TokenTape,
    parse_declaration,
    parse_expression,
    parse_function,
    parse_program,
    parse_statement,
)
from nqcc.semantic_analysis import (
    SemanticAnalysisBadLValue,
    SemanticAnalysisDuplicateDeclaration,
    SemanticAnalysisUnknownVariable,
    VariableResolver,
    resolve_function,
    resolve_program,
)


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
        target = VariableResolver()
        c_str = "a=1;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(assignment, SourceAssignmentNode)

        with pytest.raises(SemanticAnalysisUnknownVariable) as sauv:
            _ = target.resolve_expression(assignment)
        assert sauv.value.message == "Unknown identifier 'a' at 0"

    def test_assignment_badlvalue(self):
        target = VariableResolver()
        c_str = "1=1+2;"
        token_tape = TokenTape.from_c_source(c_str)
        assignment = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(assignment, SourceAssignmentNode)

        with pytest.raises(SemanticAnalysisBadLValue) as sablv:
            _ = target.resolve_expression(assignment)
        assert sablv.value.message == "Not an lvalue at 0"


class TestStatements:
    def test_null_statement(self):
        target = VariableResolver()
        c_str = ";"
        token_tape = TokenTape.from_c_source(c_str)
        stmt = parse_statement(token_tape)
        assert isinstance(stmt, SourceNullStatementNode)

        result = target.resolve_statement(stmt)
        assert isinstance(result, SourceNullStatementNode)

    def test_expression_statement(self):
        target = VariableResolver()
        c_str = "a=22;"
        token_tape = TokenTape.from_c_source(c_str)
        stmt = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 0

        # Make sure 'a' is declared
        decl_a = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_a)

        result = target.resolve_statement(stmt)
        assert isinstance(result, SourceExpressionStatementNode)
        assert isinstance(result.value, SourceAssignmentNode)
        assert isinstance(result.value.left, SourceVarNode)
        assert result.value.left.identifier == "a.0"
        assert isinstance(result.value.right, SourceConstantIntNode)
        assert result.value.right.value == 22

    def test_return_statement(self):
        target = VariableResolver()
        c_str = "return a+44;"
        token_tape = TokenTape.from_c_source(c_str)
        stmt = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 0

        # Make sure 'a' is declared
        decl_a = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_a)

        result = target.resolve_statement(stmt)
        assert isinstance(result, SourceReturnNode)
        assert isinstance(result.value, SourceBinaryExpressionNode)
        assert isinstance(result.value.operator, SourceAdd)
        assert isinstance(result.value.left, SourceVarNode)
        assert result.value.left.identifier == "a.0"
        assert isinstance(result.value.right, SourceConstantIntNode)
        assert result.value.right.value == 44


class TestFunction:
    def test_simple(self):
        c_str = "int main(void) { int a = 1; return a;}"
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_function(func)
        assert updated.identifier == "main"
        assert len(updated.body) == 2
        decl = updated.body[0]
        assert isinstance(decl, SourceDeclarationNode)
        assert isinstance(decl.identifier, SourceVarNode)
        assert decl.identifier.identifier == "a.0"
        ret = updated.body[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "a.0"


class TestProgram:
    def test_simple(self):
        c_str = "int main(void) { int a = 1; return a;}"
        token_tape = TokenTape.from_c_source(c_str)
        prog = parse_program(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_program(prog)

        updated_func = updated.value
        assert updated_func.identifier == "main"
        assert len(updated_func.body) == 2
        decl = updated_func.body[0]
        assert isinstance(decl, SourceDeclarationNode)
        assert isinstance(decl.identifier, SourceVarNode)
        assert decl.identifier.identifier == "a.0"
        ret = updated_func.body[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "a.0"
