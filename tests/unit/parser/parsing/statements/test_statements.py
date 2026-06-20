import pytest

from nqcc.frontend.lexer import ConstantIntegerToken, KeywordToken, SemicolonToken
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
    SourceExpressionStatementNode,
    SourceMultiply,
    SourceNullStatementNode,
    SourceReturnNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
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
        assert isinstance(item0, SourceVariableDeclarationNode)
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
