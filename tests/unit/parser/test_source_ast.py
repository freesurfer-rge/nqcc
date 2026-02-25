from nqcc.lexer import *
from nqcc.parser import *


class TestSourceExpressionNode:
    def test_constant_integer(self):
        tokens = [
            ConstantIntegerToken(start_position=1, value="123"),
            SemicolonToken(start_position=5, value=";"),
        ]

        node = SourceExpressionNode.parse(tokens)
        assert isinstance(node, SourceConstantIntNode)
        assert node.start_position == 1
        assert node.value == 123

        assert len(tokens) == 1
        assert tokens[0] == SemicolonToken(start_position=5, value=";")
