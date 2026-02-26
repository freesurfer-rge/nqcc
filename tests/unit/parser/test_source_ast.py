from nqcc.lexer import ConstantIntegerToken, SemicolonToken
from nqcc.parser import SourceConstantIntNode, SourceExpressionNode, TokenTape


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

        assert token_tape.tokens_remaining == 1
