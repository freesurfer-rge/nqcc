from typing import Sequence

from nqcc.lexer import (
    TokenItem,
)

from ._exceptions import SourceASTError


class TokenTape:
    def __init__(self, token_list: Sequence[TokenItem]):
        self._tokens = token_list
        self._idx = 0

    @property
    def tokens_remaining(self) -> int:
        return len(self._tokens) - self._idx

    def take(self) -> TokenItem:
        nxt = self._tokens[self._idx]
        self._idx += 1
        return nxt

    def expect(self, expected_token_type: type) -> TokenItem:
        head = self.take()
        if not isinstance(head, expected_token_type):
            raise SourceASTError(
                expected_type=expected_token_type,
                actual_token=head,
                message="Received token of unexpected type",
            )
        return head
