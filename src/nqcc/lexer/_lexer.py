from ._tokens import (
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    IdentifierToken,
    KeywordToken,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
    Token,
    WhitespaceToken,
)


class Lexer:
    def __init__(self):
        self._position = 0
        self._completed_token_list: list[Token] = []
        self._current_candidates = self._get_fresh_candidate_tokens()

    @property
    def position(self) -> int:
        return self._position

    @property
    def completed_token_list(self) -> list[Token]:
        return [item for item in self._completed_token_list if item.precedence >= 0]

    def push_character(self, ch: str):
        assert len(ch) == 1, "Must only pass single characters!"

        tokens_accept: list[Token] = []
        tokens_reject: list[Token] = []

        # Try to append the token
        for tok in self._current_candidates:
            if tok.try_append(ch, self.position):
                tokens_accept.append(tok)
            else:
                tokens_reject.append(tok)

        if len(tokens_accept) > 0:
            # At least one token accepted the character, so we
            # can go to the next character
            self._current_candidates = tokens_accept
        else:
            # No token accepted the character, so look through
            # those which rejected it to see if any are
            # currently valid
            valid_tokens = [t for t in tokens_reject if t.is_valid]
            if len(valid_tokens) == 0:
                msg = f"No valid token on arriving at '{ch}' at position {self.position}"
                raise ValueError(msg)

            valid_tokens.sort(key=lambda t: t.precedence, reverse=True)
            self._completed_token_list.append(valid_tokens[0])

            all_candidates = self._get_fresh_candidate_tokens()
            next_candidates: list[Token] = []
            for nc in all_candidates:
                if nc.try_append(ch, self.position):
                    next_candidates.append(nc)

            if len(next_candidates) == 0:
                raise ValueError(f"No token will accept '{ch}' at position {self.position}")

            self._current_candidates = next_candidates

        self._position += 1

    def character_stream_done(self):
        # Final tidy up, for when we are done pushing characters
        valid_tokens = [t for t in self._current_candidates if t.is_valid]
        if len(valid_tokens) == 0:
            candidate_strings = [t.model_jump_json() for t in self._current_candidates]
            all_candidate_str = ", ".join(candidate_strings)
            msg = "No token currently valid: " + all_candidate_str
            raise ValueError(msg)

        valid_tokens.sort(key=lambda t: t.precedence, reverse=True)
        self._completed_token_list.append(valid_tokens[0])

    def _get_fresh_candidate_tokens(self) -> list[Token]:
        starting_tokens = [
            CloseBraceToken(),
            CloseParenToken(),
            ConstantIntegerToken(),
            IdentifierToken(),
            KeywordToken(),
            OpenBraceToken(),
            OpenParenToken(),
            SemicolonToken(),
            WhitespaceToken(),
        ]
        return starting_tokens
