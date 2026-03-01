import pytest

from nqcc.lexer import ConstantIntegerToken, SemicolonToken
from nqcc.parser import SourceASTBadTypeError, TokenTape


class TestTokenTape:
    def test_take(self):
        a = ConstantIntegerToken(start_position=0, value="2")
        b = SemicolonToken(start_position=3, value=";")

        target = TokenTape([a, b])
        assert target.tokens_remaining == 2

        first = target.take()
        assert target.tokens_remaining == 1
        assert first == a

        second = target.take()
        assert target.tokens_remaining == 0
        assert second == b

    def test_take_too_many(self):
        target = TokenTape([])
        with pytest.raises(IndexError, match="No tokens remaining in TokenTape"):
            _ = target.take()

    def test_expect_correct(self):
        a = ConstantIntegerToken(start_position=0, value="2")
        b = SemicolonToken(start_position=3, value=";")

        target = TokenTape([a, b])
        assert target.tokens_remaining == 2

        first = target.expect(ConstantIntegerToken)
        assert target.tokens_remaining == 1
        assert first == a

        second = target.expect(SemicolonToken)
        assert target.tokens_remaining == 0
        assert second == b

    def test_expect_incorrect(self):
        a = ConstantIntegerToken(start_position=0, value="2")
        b = SemicolonToken(start_position=3, value=";")

        target = TokenTape([a, b])
        assert target.tokens_remaining == 2

        with pytest.raises(SourceASTBadTypeError) as sae:
            _ = target.expect(SemicolonToken)
        assert sae.value.actual_token == a
        assert sae.value.expected_type == SemicolonToken
        assert sae.value.message == "Received token of unexpected type"
