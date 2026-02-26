from nqcc.lexer import ConstantIntegerToken, SemicolonToken, KeywordToken
from nqcc.parser import SourceConstantIntNode, SourceExpressionNode, TokenTape, SourceStatementNode, SourceReturnNode


class TestSourceExpressionNode:
    def test_constant_integer(self):
        tokens = [
            ConstantIntegerToken(start_position=1, value="123"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = SourceExpressionNode.parse(token_tape)
        assert isinstance(node, SourceConstantIntNode)
        assert node.start_position == 1
        assert node.value == 123

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_return_statement(self):
        tokens = [
            KeywordToken(start_position=0, value="return"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = SourceStatementNode.parse(token_tape)

        assert isinstance(node, SourceReturnNode)
        assert node.start_position == 0
        assert isinstance(node.value, SourceConstantIntNode)
        sen : SourceConstantIntNode = node.value
        assert sen.start_position == 1
        assert sen.value == 321

        assert token_tape.tokens_remaining == 0