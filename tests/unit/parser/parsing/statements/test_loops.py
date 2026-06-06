import pytest

from nqcc.parser import (
    SourceAdd,
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceCompoundNode,
    SourceConstantIntNode,
    SourceDivide,
    SourceDoWhileNode,
    SourceExpressionStatementNode,
    SourceForNode,
    SourceGreaterThan,
    SourceInitDeclNode,
    SourceInitExpressionNode,
    SourceLessThan,
    SourceVariableDeclarationNode,
    SourceVarNode,
    SourceWhileNode,
    TokenTape,
    parse_statement,
)


class TestSourceWhileNode:
    def test_simple(self):
        c_str = """
        while( a > 0 )
            a = a / 2;
        a = a + 1;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 6

        assert isinstance(node, SourceWhileNode)
        cond = node.condition
        assert isinstance(cond, SourceBinaryExpressionNode)
        assert isinstance(cond.operator, SourceGreaterThan)
        assert cond.left == SourceVarNode(start_position=16, identifier="a")
        assert cond.right == SourceConstantIntNode(start_position=20, value=0)

        assert isinstance(node.body, SourceExpressionStatementNode)
        assert isinstance(node.body.value, SourceAssignmentNode)
        body = node.body.value
        assert body.left == SourceVarNode(start_position=36, identifier="a")
        isinstance(body.right, SourceBinaryExpressionNode)
        assert isinstance(body.right.operator, SourceDivide)
        assert body.right.left == SourceVarNode(start_position=40, identifier="a")
        assert body.right.right == SourceConstantIntNode(start_position=44, value=2)

    def test_simple_braces(self):
        c_str = """
        while( a > 0 ) {
            a = a / 2;
        }
        a = a + 1;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 6

        assert isinstance(node, SourceWhileNode)
        cond = node.condition
        assert isinstance(cond, SourceBinaryExpressionNode)
        assert isinstance(cond.operator, SourceGreaterThan)
        assert cond.left == SourceVarNode(start_position=16, identifier="a")
        assert cond.right == SourceConstantIntNode(start_position=20, value=0)

        assert isinstance(node.body, SourceCompoundNode)
        assert len(node.body.block.items) == 1
        stmt = node.body.block.items[0]
        assert isinstance(stmt, SourceExpressionStatementNode)
        assert isinstance(stmt.value, SourceAssignmentNode)
        assert stmt.value.left == SourceVarNode(start_position=38, identifier="a")
        isinstance(stmt.value.right, SourceBinaryExpressionNode)
        assert isinstance(stmt.value.right.operator, SourceDivide)
        assert stmt.value.right.left == SourceVarNode(start_position=42, identifier="a")
        assert stmt.value.right.right == SourceConstantIntNode(start_position=46, value=2)


class TestSourceDoWhileNode:
    def test_simple(self):
        c_str = """
        do
            a = 10 + a;
        while( 100 > a );
        a = a + 1;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 6

        assert isinstance(node, SourceDoWhileNode)
        assert isinstance(node.body, SourceExpressionStatementNode)
        assert isinstance(node.body.value, SourceAssignmentNode)
        assert node.body.value.left == SourceVarNode(start_position=24, identifier="a")
        assert isinstance(node.body.value.right, SourceBinaryExpressionNode)
        assign_expr = node.body.value.right
        assert isinstance(assign_expr.operator, SourceAdd)
        assert assign_expr.left == SourceConstantIntNode(start_position=28, value=10)
        assert assign_expr.right == SourceVarNode(start_position=33, identifier="a")

        assert isinstance(node.condition, SourceBinaryExpressionNode)
        assert isinstance(node.condition.operator, SourceGreaterThan)
        assert node.condition.left == SourceConstantIntNode(start_position=51, value=100)
        assert node.condition.right == SourceVarNode(start_position=57, identifier="a")

    def test_simple_braces(self):
        c_str = """
        do {
            a = 10 + a;
        } while( 100 > a );
        a = a + 1;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 6

        assert isinstance(node, SourceDoWhileNode)
        assert isinstance(node.body, SourceCompoundNode)
        assert len(node.body.block.items) == 1
        stmt = node.body.block.items[0]
        assert isinstance(stmt, SourceExpressionStatementNode)
        assert isinstance(stmt.value, SourceAssignmentNode)
        assert stmt.value.left == SourceVarNode(start_position=26, identifier="a")
        assert isinstance(stmt.value.right, SourceBinaryExpressionNode)
        assign_expr = stmt.value.right
        assert isinstance(assign_expr.operator, SourceAdd)
        assert assign_expr.left == SourceConstantIntNode(start_position=30, value=10)
        assert assign_expr.right == SourceVarNode(start_position=35, identifier="a")

        assert isinstance(node.condition, SourceBinaryExpressionNode)
        assert isinstance(node.condition.operator, SourceGreaterThan)
        assert node.condition.left == SourceConstantIntNode(start_position=55, value=100)
        assert node.condition.right == SourceVarNode(start_position=61, identifier="a")


class TestSourceForNode:
    def test_simple(self):
        c_str = """
        for( i=0; i<10; i=i+1)
            a = 10 + a;
        a = a + 1;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 6

        assert isinstance(node, SourceForNode)

        assert isinstance(node.init, SourceInitExpressionNode)
        assert isinstance(node.init.expression, SourceAssignmentNode)
        init_expr = node.init.expression
        assert init_expr.left == SourceVarNode(start_position=14, identifier="i")
        assert init_expr.right == SourceConstantIntNode(start_position=16, value=0)

        assert isinstance(node.condition, SourceBinaryExpressionNode)
        assert isinstance(node.condition.operator, SourceLessThan)
        assert node.condition.left == SourceVarNode(start_position=19, identifier="i")
        assert node.condition.right == SourceConstantIntNode(start_position=21, value=10)

        assert isinstance(node.post, SourceAssignmentNode)
        assert node.post.left == SourceVarNode(start_position=25, identifier="i")
        assert isinstance(node.post.right, SourceBinaryExpressionNode)
        pe = node.post.right
        assert isinstance(pe.operator, SourceAdd)
        assert pe.left == SourceVarNode(start_position=27, identifier="i")
        assert pe.right == SourceConstantIntNode(start_position=29, value=1)

        assert isinstance(node.body, SourceExpressionStatementNode)
        stmt = node.body
        assert isinstance(stmt.value, SourceAssignmentNode)
        assert stmt.value.left == SourceVarNode(start_position=44, identifier="a")
        assert isinstance(stmt.value.right, SourceBinaryExpressionNode)
        assign_expr = stmt.value.right
        assert isinstance(assign_expr.operator, SourceAdd)
        assert assign_expr.left == SourceConstantIntNode(start_position=48, value=10)
        assert assign_expr.right == SourceVarNode(start_position=53, identifier="a")

    def test_simple_with_init(self):
        c_str = """
        for( int i=0; i<10; i=i+1) {
            a = 12 + a;
        }
        a = a + 1;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 6

        assert isinstance(node, SourceForNode)

        assert isinstance(node.init, SourceInitDeclNode)
        assert isinstance(node.init.decl, SourceVariableDeclarationNode)
        decl = node.init.decl
        assert decl.identifier == SourceVarNode(start_position=18, identifier="i")
        assert decl.initial == SourceConstantIntNode(start_position=20, value=0)

        assert isinstance(node.condition, SourceBinaryExpressionNode)
        assert isinstance(node.condition.operator, SourceLessThan)
        assert node.condition.left == SourceVarNode(start_position=23, identifier="i")
        assert node.condition.right == SourceConstantIntNode(start_position=25, value=10)

        assert isinstance(node.post, SourceAssignmentNode)
        assert node.post.left == SourceVarNode(start_position=29, identifier="i")
        assert isinstance(node.post.right, SourceBinaryExpressionNode)
        pe = node.post.right
        assert isinstance(pe.operator, SourceAdd)
        assert pe.left == SourceVarNode(start_position=31, identifier="i")
        assert pe.right == SourceConstantIntNode(start_position=33, value=1)

        assert isinstance(node.body, SourceCompoundNode)
        assert len(node.body.block.items) == 1
        stmt = node.body.block.items[0]
        assert isinstance(stmt.value, SourceAssignmentNode)
        assert stmt.value.left == SourceVarNode(start_position=50, identifier="a")
        assert isinstance(stmt.value.right, SourceBinaryExpressionNode)
        assign_expr = stmt.value.right
        assert isinstance(assign_expr.operator, SourceAdd)
        assert assign_expr.left == SourceConstantIntNode(start_position=54, value=12)
        assert assign_expr.right == SourceVarNode(start_position=59, identifier="a")

    def test_empty_expressions(self):
        c_str = """
        for( ; ; )
            a = 17 + a;
        a = a + 1;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 6

        assert isinstance(node, SourceForNode)
        assert node.init == SourceInitExpressionNode(start_position=9, expression=None)
        assert node.condition is None
        assert node.post is None

        assert isinstance(node.body, SourceExpressionStatementNode)
        stmt = node.body
        assert isinstance(stmt.value, SourceAssignmentNode)
        assert stmt.value.left == SourceVarNode(start_position=32, identifier="a")
        assert isinstance(stmt.value.right, SourceBinaryExpressionNode)
        assign_expr = stmt.value.right
        assert isinstance(assign_expr.operator, SourceAdd)
        assert assign_expr.left == SourceConstantIntNode(start_position=36, value=17)
        assert assign_expr.right == SourceVarNode(start_position=41, identifier="a")

    def test_bad_storage_class(self):
        c_str = """
        for( static int i=0; i<10; i=i+1) a = a + i;
        """
        token_tape = TokenTape.from_c_source(c_str)

        with pytest.raises(ValueError, match="Storage not allowed in for loop initialiser"):
            _ = parse_statement(token_tape)
