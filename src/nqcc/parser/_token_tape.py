from typing import Sequence

from nqcc.lexer import lex_string, TokenItem

from ._exceptions import SourceASTBadTypeError


class TokenTape:
    def __init__(self, token_list: Sequence[TokenItem]) -> None:
        self._tokens = token_list
        self._idx = 0

    @property
    def tokens_remaining(self) -> int:
        return len(self._tokens) - self._idx

    def take(self) -> TokenItem:
        if self._idx >= len(self._tokens):
            raise IndexError("No tokens remaining in TokenTape")
        nxt = self._tokens[self._idx]
        self._idx += 1
        return nxt

    def expect(self, expected_token_type: type) -> TokenItem:
        head = self.take()
        if not isinstance(head, expected_token_type):
            raise SourceASTBadTypeError(
                expected_type=expected_token_type,
                actual_token=head,
                message="Received token of unexpected type",
            )
        return head

    @classmethod
    def from_c_source(cls, c_source: str) -> TokenTape:
        return TokenTape(lex_string(c_source))
