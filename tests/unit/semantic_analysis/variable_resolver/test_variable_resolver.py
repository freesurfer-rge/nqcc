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
    SourceDoWhileNode,
    SourceExpressionStatementNode,
    SourceForNode,
    SourceIfStatementNode,
    SourceInitDeclNode,
    SourceInitExpressionNode,
    SourceNullStatementNode,
    SourceReturnNode,
    SourceVarNode,
    SourceWhileNode,
    TokenTape,
    parse_function,
    parse_program,
    parse_statement,
)
from nqcc.semantic_analysis import (
    VariableInfo,
    VariableResolver,
    resolve_function,
    resolve_program,
)


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

    def test_dowhile_statement(self):
        target = VariableResolver()
        variable_map = {}
        c_str = """
        do a=2+a; while( a < 3 );
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
        assert isinstance(result, SourceDoWhileNode)
        assert isinstance(result.condition, SourceBinaryExpressionNode)
        assert isinstance(result.condition.left, SourceVarNode)
        assert result.condition.left.identifier == "a.0"

        assert isinstance(result.body, SourceExpressionStatementNode)
        assert isinstance(result.body.value, SourceAssignmentNode)
        assert isinstance(result.body.value.left, SourceVarNode)
        assert result.body.value.left.identifier == "a.0"
        assert isinstance(result.body.value.right, SourceBinaryExpressionNode)
        assert isinstance(result.body.value.right.right, SourceVarNode)
        assert result.body.value.right.right.identifier == "a.0"

    def test_for_initexpr(self):
        target = VariableResolver()
        variable_map = {}
        c_str = """
        for( a=0; a<10; a=a+1) b=b+1;
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

        # And also 'b'
        decl_b = SourceDeclarationNode(
            start_position=13,
            identifier=SourceVarNode(start_position=14, identifier="b"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_b, variable_map)

        result = target.resolve_statement(stmt, variable_map)
        assert len(variable_map) == 2
        assert isinstance(result, SourceForNode)
        assert isinstance(result.init, SourceInitExpressionNode)
        assert isinstance(result.init.expression, SourceAssignmentNode)
        assert isinstance(result.init.expression.left, SourceVarNode)
        assert result.init.expression.left.identifier == "a.0"

        assert isinstance(result.condition, SourceBinaryExpressionNode)
        assert isinstance(result.condition.left, SourceVarNode)
        assert result.condition.left.identifier == "a.0"

        assert isinstance(result.post, SourceAssignmentNode)
        assert isinstance(result.post.left, SourceVarNode)
        assert result.post.left.identifier == "a.0"
        assert isinstance(result.post.right, SourceBinaryExpressionNode)
        assert isinstance(result.post.right.left, SourceVarNode)
        assert result.post.right.left.identifier == "a.0"

        assert isinstance(result.body, SourceExpressionStatementNode)
        assert isinstance(result.body.value, SourceAssignmentNode)
        assert isinstance(result.body.value.left, SourceVarNode)
        assert result.body.value.left.identifier == "b.1"
        assert isinstance(result.body.value.right, SourceBinaryExpressionNode)
        assert isinstance(result.body.value.right.left, SourceVarNode)
        assert result.body.value.right.left.identifier == "b.1"

    def test_for_initdecl(self):
        target = VariableResolver()
        variable_map = {}
        c_str = """
        for( int a=0; a<10; a=a+1) b=b+1;
        """
        token_tape = TokenTape.from_c_source(c_str)
        stmt = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 0

        # Make sure that 'a' is declared outside the loop
        decl_a = SourceDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_a, variable_map)

        # And also 'b'
        decl_b = SourceDeclarationNode(
            start_position=13,
            identifier=SourceVarNode(start_position=14, identifier="b"),
            initial=None,
        )
        _ = target.resolve_declaration(decl_b, variable_map)

        result = target.resolve_statement(stmt, variable_map)
        # Original variable map unaffected by inner 'a' decl
        assert len(variable_map) == 2
        assert isinstance(result, SourceForNode)
        assert isinstance(result.init, SourceInitDeclNode)
        assert isinstance(result.init.decl, SourceDeclarationNode)
        assert isinstance(result.init.decl.identifier, SourceVarNode)
        assert result.init.decl.identifier.identifier == "a.2"

        assert isinstance(result.condition, SourceBinaryExpressionNode)
        assert isinstance(result.condition.left, SourceVarNode)
        assert result.condition.left.identifier == "a.2"

        assert isinstance(result.post, SourceAssignmentNode)
        assert isinstance(result.post.left, SourceVarNode)
        assert result.post.left.identifier == "a.2"
        assert isinstance(result.post.right, SourceBinaryExpressionNode)
        assert isinstance(result.post.right.left, SourceVarNode)
        assert result.post.right.left.identifier == "a.2"

        assert isinstance(result.body, SourceExpressionStatementNode)
        assert isinstance(result.body.value, SourceAssignmentNode)
        assert isinstance(result.body.value.left, SourceVarNode)
        assert result.body.value.left.identifier == "b.1"
        assert isinstance(result.body.value.right, SourceBinaryExpressionNode)
        assert isinstance(result.body.value.right.left, SourceVarNode)
        assert result.body.value.right.left.identifier == "b.1"


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
