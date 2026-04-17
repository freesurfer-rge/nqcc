import pytest

from nqcc.parser import (
    SourceAdd,
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceBreakNode,
    SourceCompoundNode,
    SourceConstantIntNode,
    SourceContinueNode,
    SourceDeclarationNode,
    SourceExpressionStatementNode,
    SourceIfStatementNode,
    SourceNullStatementNode,
    SourceReturnNode,
    SourceTernaryExpressonNode,
    SourceVarNode,
    SourceWhileNode,
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
    VariableInfo,
    VariableResolver,
    make_inner_variable_map,
    resolve_function,
    resolve_program,
)


class TestInnerMap:
    def test_smoke(self):
        inner = {
            "a": VariableInfo(name="a.0", defined_in_block=True),
            "b": VariableInfo(name="b.1", defined_in_block=False),
        }

        result = make_inner_variable_map(inner)
        assert len(result) == 2
        assert result["a"] == VariableInfo(name="a.0", defined_in_block=False)
        assert result["b"] == VariableInfo(name="b.1", defined_in_block=False)


class TestDeclarations:
    def test_smoke_no_init(self):
        target = VariableResolver()
        variable_map = {}

        decl = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )

        updated = target.resolve_declaration(decl, variable_map)
        assert isinstance(updated, SourceDeclarationNode)
        assert updated.start_position == 10
        assert updated.identifier == SourceVarNode(start_position=11, identifier="a.0")
        assert updated.initial is None
        assert len(variable_map) == 1

    def test_decl_with_init(self):
        target = VariableResolver()
        variable_map = {}

        program_str = "int a = 1;"

        token_tape = TokenTape.from_c_source(program_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceDeclarationNode)

        result = target.resolve_declaration(decl, variable_map)
        assert isinstance(result, SourceDeclarationNode)
        assert result.start_position == 0
        assert result.identifier == SourceVarNode(start_position=4, identifier="a.0")
        assert isinstance(result.initial, SourceConstantIntNode)
        assert result.initial.value == 1
        assert len(variable_map) == 1

    def test_two_decl(self):
        target = VariableResolver()

        decl0 = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )

        variable_map = {}
        updated0 = target.resolve_declaration(decl0, variable_map)
        assert isinstance(updated0, SourceDeclarationNode)
        assert updated0.start_position == 10
        assert updated0.identifier == SourceVarNode(start_position=11, identifier="a.0")
        assert updated0.initial is None

        decl1 = SourceDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="b"),
            initial=None,
        )

        updated1 = target.resolve_declaration(decl1, variable_map)
        assert isinstance(updated1, SourceDeclarationNode)
        assert updated1.start_position == 12
        assert updated1.identifier == SourceVarNode(start_position=13, identifier="b.1")
        assert updated1.initial is None

    def test_duplicate_name(self):
        target = VariableResolver()
        variable_map = {}

        decl0 = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl0, variable_map)

        decl1 = SourceDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="a"),
            initial=None,
        )

        with pytest.raises(SemanticAnalysisDuplicateDeclaration) as saduperr:
            _ = target.resolve_declaration(decl1, variable_map)
        assert saduperr.value.decl == decl1
        assert saduperr.value.message == "Duplicate declaration of 'a' at 12"


class TestExpressions:
    def test_assignment(self):
        target = VariableResolver()
        variable_map = {}

        # Make sure 'a' is declared
        decl_a = SourceDeclarationNode(
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
        target = VariableResolver()
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
        target = VariableResolver()
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
        target = VariableResolver()
        variable_map = {}
        c_str = "a?b:c;"
        token_tape = TokenTape.from_c_source(c_str)
        ternary_expr = parse_expression(token_tape, min_precedence=0)
        assert token_tape.tokens_remaining == 1
        assert isinstance(ternary_expr, SourceTernaryExpressonNode)

        for decl_var in ["a", "b", "c"]:
            decl = SourceDeclarationNode(
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


class TestStatements:
    @pytest.mark.parametrize(
        ("c_stmt", "node_type"),
        [
            (";", SourceNullStatementNode),
            ("break;", SourceBreakNode),
            ("continue;", SourceContinueNode),
        ],
    )
    def test_null_statement(self, c_stmt: str, node_type: type):
        target = VariableResolver()
        variable_map: dict[str, VariableInfo] = {}
        token_tape = TokenTape.from_c_source(c_stmt)
        stmt = parse_statement(token_tape)
        assert isinstance(stmt, node_type)

        result = target.resolve_statement(stmt, variable_map)
        assert isinstance(result, node_type)
        assert result == stmt
        assert len(variable_map) == 0

    def test_expression_statement(self):
        target = VariableResolver()
        variable_map = {}
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
        _ = target.resolve_declaration(decl_a, variable_map)

        result = target.resolve_statement(stmt, variable_map)
        assert isinstance(result, SourceExpressionStatementNode)
        assert isinstance(result.value, SourceAssignmentNode)
        assert isinstance(result.value.left, SourceVarNode)
        assert result.value.left.identifier == "a.0"
        assert isinstance(result.value.right, SourceConstantIntNode)
        assert result.value.right.value == 22

    def test_return_statement(self):
        target = VariableResolver()
        variable_map = {}
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
        _ = target.resolve_declaration(decl_a, variable_map)

        result = target.resolve_statement(stmt, variable_map)
        assert isinstance(result, SourceReturnNode)
        assert isinstance(result.value, SourceBinaryExpressionNode)
        assert isinstance(result.value.operator, SourceAdd)
        assert isinstance(result.value.left, SourceVarNode)
        assert result.value.left.identifier == "a.0"
        assert isinstance(result.value.right, SourceConstantIntNode)
        assert result.value.right.value == 44

    def test_if_statement(self):
        target = VariableResolver()
        variable_map = {}
        c_str = """
        if( a )
           return a;
        else
           return b;
"""
        token_tape = TokenTape.from_c_source(c_str)
        stmt = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 0
        assert isinstance(stmt, SourceIfStatementNode)
        assert stmt.otherwise is not None

        # Make sure 'a' and 'b' are declared
        decl_a = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_a, variable_map)
        decl_b = SourceDeclarationNode(
            start_position=11,
            identifier=SourceVarNode(start_position=12, identifier="b"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_b, variable_map)

        result = target.resolve_statement(stmt, variable_map)
        assert isinstance(result, SourceIfStatementNode)
        assert isinstance(result.condition, SourceVarNode)
        assert result.condition.identifier == "a.0"

        assert isinstance(result.then, SourceReturnNode)
        assert isinstance(result.then.value, SourceVarNode)
        assert result.then.value.identifier == "a.0"

        assert isinstance(result.otherwise, SourceReturnNode)
        assert isinstance(result.otherwise.value, SourceVarNode)
        assert result.otherwise.value.identifier == "b.1"

    def test_while_statement(self):
        target = VariableResolver()
        variable_map = {}
        c_str = """
        while( a < 10) a=a+1;
        """
        token_tape = TokenTape.from_c_source(c_str)
        stmt = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 0

        # Make sure that 'a' is declared
        decl_a = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_a, variable_map)

        result = target.resolve_statement(stmt, variable_map)
        assert len(variable_map) == 1
        assert isinstance(result, SourceWhileNode)
        assert isinstance(result.condition, SourceBinaryExpressionNode)
        assert isinstance(result.condition.left, SourceVarNode)
        assert result.condition.left.identifier == "a.0"

        assert isinstance(result.body, SourceExpressionStatementNode)
        assert isinstance(result.body.value, SourceAssignmentNode)
        assert isinstance(result.body.value.left, SourceVarNode)
        assert result.body.value.left.identifier == "a.0"
        assert isinstance(result.body.value.right, SourceBinaryExpressionNode)
        assert isinstance(result.body.value.right.left, SourceVarNode)
        assert result.body.value.right.left.identifier == "a.0"


class TestFunction:
    def test_simple(self):
        c_str = "int main(void) { int a = 1; return a;}"
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_function(func)
        assert updated.identifier == "main"
        assert len(updated.body.items) == 2
        decl = updated.body.items[0]
        assert isinstance(decl, SourceDeclarationNode)
        assert isinstance(decl.identifier, SourceVarNode)
        assert decl.identifier.identifier == "a.0"
        ret = updated.body.items[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "a.0"

    def test_with_nested(self):
        c_str = """int main( void ) {
            int x=1;
            {
                int y = x+1;
                int x = 2;
            }
            return x;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_function(func)
        assert updated.identifier == "main"
        assert len(updated.body.items) == 3

        decl0 = updated.body.items[0]
        assert isinstance(decl0, SourceDeclarationNode)
        assert isinstance(decl0.identifier, SourceVarNode)
        assert decl0.identifier.identifier == "x.0"

        compound0 = updated.body.items[1]
        assert isinstance(compound0, SourceCompoundNode)
        assert len(compound0.block.items) == 2

        decl1 = compound0.block.items[0]
        assert isinstance(decl1, SourceDeclarationNode)
        assert isinstance(decl1.identifier, SourceVarNode)
        assert decl1.identifier.identifier == "y.1"
        assert isinstance(decl1.initial, SourceBinaryExpressionNode)
        assert isinstance(decl1.initial.left, SourceVarNode)
        assert decl1.initial.left.identifier == "x.0"

        decl2 = compound0.block.items[1]
        assert isinstance(decl2, SourceDeclarationNode)
        assert isinstance(decl2.identifier, SourceVarNode)
        assert decl2.identifier.identifier == "x.2"

        ret = updated.body.items[2]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "x.0"


class TestProgram:
    def test_simple(self):
        c_str = "int main(void) { int a = 1; return a;}"
        token_tape = TokenTape.from_c_source(c_str)
        prog = parse_program(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_program(prog)

        updated_func = updated.value
        assert updated_func.identifier == "main"
        assert len(updated_func.body.items) == 2
        decl = updated_func.body.items[0]
        assert isinstance(decl, SourceDeclarationNode)
        assert isinstance(decl.identifier, SourceVarNode)
        assert decl.identifier.identifier == "a.0"
        ret = updated_func.body.items[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "a.0"
