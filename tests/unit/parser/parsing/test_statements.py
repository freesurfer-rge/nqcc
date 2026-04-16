import pytest

from nqcc.lexer import ConstantIntegerToken, KeywordToken, SemicolonToken
from nqcc.parser import (
    SourceAdd,
    SourceAssignmentNode,
    SourceASTBadValueError,
    SourceBinaryExpressionNode,
    SourceBlockNode,
    SourceBreakNode,
    SourceCompoundNode,
    SourceConstantIntNode,
    SourceContinueNode,
    SourceDeclarationNode,
    SourceDivide,
    SourceDoWhileNode,
    SourceExpressionStatementNode,
    SourceGreaterThan,
    SourceIfStatementNode,
    SourceMultiply,
    SourceNullStatementNode,
    SourceReturnNode,
    SourceVarNode,
    SourceWhileNode,SourceForNode, SourceInitDeclNode, SourceInitExpressionNode, SourceLessThan,
    TokenTape,
    parse_statement,
)


class TestSourceStatementNode:
    def test_return_statement(self):
        tokens = [
            KeywordToken(start_position=0, value="return"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = parse_statement(token_tape)

        assert isinstance(node, SourceReturnNode)
        assert node.start_position == 0
        assert isinstance(node.value, SourceConstantIntNode)
        assert node.value.start_position == 1
        assert node.value.value == 321

        assert token_tape.tokens_remaining == 0

    def test_return_mispelled(self):
        tokens = [
            KeywordToken(start_position=0, value="returns"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        with pytest.raises(SourceASTBadValueError) as sabve:
            _ = parse_statement(token_tape)
        assert sabve.value.message == "Unexpected keyword"
        assert sabve.value.actual_token == tokens[0]

    def test_return_has_space(self):
        tokens = [
            KeywordToken(start_position=0, value="retur n"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        with pytest.raises(SourceASTBadValueError) as sabve:
            _ = parse_statement(token_tape)
        assert sabve.value.message == "Unexpected keyword"
        assert sabve.value.actual_token == tokens[0]

    def test_null_statement(self):
        c_str = ";"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 1

        node = parse_statement(token_tape)
        assert isinstance(node, SourceNullStatementNode)
        assert node.start_position == 0
        assert token_tape.tokens_remaining == 0

    def test_complex_statement(self):
        c_str = "a = 3 * (b = a);"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 10

        node = parse_statement(token_tape)
        assert isinstance(node, SourceExpressionStatementNode)
        assert token_tape.tokens_remaining == 0
        assert isinstance(node.value, SourceAssignmentNode)
        assert node.value.left == SourceVarNode(start_position=0, identifier="a")
        assert isinstance(node.value.right, SourceBinaryExpressionNode)
        mul_exp = node.value.right
        assert mul_exp.operator == SourceMultiply(start_position=6)
        assert mul_exp.left == SourceConstantIntNode(start_position=4, value=3)
        assert isinstance(mul_exp.right, SourceAssignmentNode)
        mul_assign = mul_exp.right
        assert mul_assign.left == SourceVarNode(start_position=9, identifier="b")
        assert mul_assign.right == SourceVarNode(start_position=13, identifier="a")
        assert token_tape.tokens_remaining == 0

    def test_return_addition(self):
        c_str = "return a + b;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 5

        node = parse_statement(token_tape)
        assert isinstance(node, SourceReturnNode)
        assert isinstance(node.value, SourceBinaryExpressionNode)
        assert node.value.operator == SourceAdd(start_position=9)
        assert node.value.left == SourceVarNode(start_position=7, identifier="a")
        assert node.value.right == SourceVarNode(start_position=11, identifier="b")
        assert token_tape.tokens_remaining == 0


class TestSourceIfStatementNode:
    def test_simple(self):
        # Have extra semicolon to ensure we don't run out of tokens
        c_str = "if( a ) b=1; ;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 9

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceExpressionStatementNode)
        assert isinstance(node.then.value, SourceAssignmentNode)
        assert isinstance(node.then.value.left, SourceVarNode)
        assert node.then.value.left.identifier == "b"
        assert isinstance(node.then.value.right, SourceConstantIntNode)
        assert node.then.value.right.value == 1

        assert node.otherwise is None

        # Should not have touched the extra semicolon
        assert token_tape.tokens_remaining == 1

    def test_with_else(self):
        c_str = "if( a ) b=1; else c=2;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 13

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceExpressionStatementNode)
        assert isinstance(node.then.value, SourceAssignmentNode)
        assert isinstance(node.then.value.left, SourceVarNode)
        assert node.then.value.left.identifier == "b"
        assert isinstance(node.then.value.right, SourceConstantIntNode)
        assert node.then.value.right.value == 1

        assert isinstance(node.otherwise, SourceExpressionStatementNode)
        assert isinstance(node.otherwise.value, SourceAssignmentNode)
        assert isinstance(node.otherwise.value.left, SourceVarNode)
        assert node.otherwise.value.left.identifier == "c"
        assert isinstance(node.otherwise.value.right, SourceConstantIntNode)
        assert node.otherwise.value.right.value == 2

        # Should have consumed everything
        assert token_tape.tokens_remaining == 0

    def test_nested(self):
        # Again, tag an extra semicolon onto the end
        c_str = """if (a)
        if( a>10 )
           return a;
        else
           return b;

        ;
"""
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 18

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceIfStatementNode)
        assert node.otherwise is None
        inner = node.then
        assert isinstance(inner.condition, SourceBinaryExpressionNode)
        assert isinstance(inner.condition.operator, SourceGreaterThan)
        assert isinstance(inner.condition.left, SourceVarNode)
        assert inner.condition.left.identifier == "a"
        assert isinstance(inner.condition.right, SourceConstantIntNode)
        assert inner.condition.right.value == 10

        assert isinstance(inner.then, SourceReturnNode)
        assert isinstance(inner.then.value, SourceVarNode)
        assert inner.then.value.identifier == "a"
        assert isinstance(inner.otherwise, SourceReturnNode)
        assert isinstance(inner.otherwise.value, SourceVarNode)
        assert inner.otherwise.value.identifier == "b"

    def test_braced(self):
        # Again, tag an extra semicolon onto the end
        c_str = """if (a) {
            return a;
        } else {
            return b;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 15

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceCompoundNode)
        assert isinstance(node.then.block, SourceBlockNode)
        assert len(node.then.block.items) == 1
        assert node.then.block.items[0] == SourceReturnNode(
            start_position=21, value=SourceVarNode(start_position=28, identifier="a")
        )

        assert isinstance(node.otherwise, SourceCompoundNode)
        assert isinstance(node.otherwise.block, SourceBlockNode)
        assert len(node.otherwise.block.items) == 1
        assert node.otherwise.block.items[0] == SourceReturnNode(
            start_position=60, value=SourceVarNode(start_position=67, identifier="b")
        )


class TestSourceCompoundNode:
    def test_simple(self):
        c_str = """
        {
            int a;
            a = a + 1;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 11

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 0
        assert isinstance(node, SourceCompoundNode)
        assert isinstance(node.block, SourceBlockNode)
        assert len(node.block.items) == 2

        item0 = node.block.items[0]
        assert isinstance(item0, SourceDeclarationNode)
        assert item0.identifier.identifier == "a"
        assert item0.initial is None

        item1 = node.block.items[1]
        assert isinstance(item1, SourceExpressionStatementNode)
        assert isinstance(item1.value, SourceAssignmentNode)
        assert item1.value.left == SourceVarNode(start_position=42, identifier="a")

        add_op = item1.value.right
        assert isinstance(add_op, SourceBinaryExpressionNode)
        assert isinstance(add_op.operator, SourceAdd)
        assert add_op.left == SourceVarNode(start_position=46, identifier="a")
        assert add_op.right == SourceConstantIntNode(start_position=50, value=1)


class TestSourceBreakNode:
    def test_simple(self):
        c_str = """
        break;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 0

        assert node == SourceBreakNode(start_position=9, label="")


class TestSourceContinueNode:
    def test_simple(self):
        c_str = """
        continue;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 0

        assert node == SourceContinueNode(start_position=9, label="")


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
        for( int i=0; i<10; i=i+1)
            a = 10 + a;
        a = a + 1;
        """
        token_tape = TokenTape.from_c_source(c_str)

        node = parse_statement(token_tape)
        assert token_tape.tokens_remaining == 6

        assert isinstance(node, SourceForNode)

        assert isinstance(node.init, SourceInitDeclNode)
        assert isinstance(node.init.decl, SourceDeclarationNode)
        decl = node.init.decl
        assert decl.identifier == SourceVarNode(start_position=14, identifier="i")
        assert decl.initial == SourceConstantIntNode(start_position=16, value=0)

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