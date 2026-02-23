from ._tokens import (
    AppendResult,
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    IdentifierToken,
    KeywordToken,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
    TokenItem,
    WhitespaceToken,
)

MAX_EXCEPTION_TOKENS = 5


class LexerError(Exception):
    def __init__(
        self, *, bad_character: str, position: int, previous_tokens: list[TokenItem], message: str
    ):
        self.bad_character = bad_character
        self.position = position
        self.previous_tokens = previous_tokens
        self.message = message
        super().__init__(self.message)


class Lexer:
    def __init__(self):
        self._position = 0
        self._completed_token_list: list[TokenItem] = []
        self._current_candidates = self._get_fresh_candidate_tokens()

    @property
    def position(self) -> int:
        return self._position

    @property
    def completed_token_list(self) -> list[TokenItem]:
        return [item for item in self._completed_token_list if item.precedence >= 0]

    def push_character(self, ch: str):
        assert len(ch) == 1, "Must only pass single characters!"

        tokens_accept: list[TokenItem] = []
        tokens_can_follow: list[TokenItem] = []
        tokens_reject: list[TokenItem] = []

        # Try to append the token
        for tok in self._current_candidates:
            match tok.try_append(ch, self.position):
                case AppendResult.ACCEPTED:
                    tokens_accept.append(tok)
                case AppendResult.CAN_FOLLOW:
                    tokens_can_follow.append(tok)
                case AppendResult.REJECTED:
                    tokens_reject.append(tok)
                case unrecognised:
                    raise ValueError(f"Unrecognised try_append result: {unrecognised}")

        if len(tokens_accept) > 0:
            # At least one token accepted the character, so we
            # can go to the next character
            self._current_candidates = tokens_accept
        else:
            # No token accepted the character, so see if
            # any tokens said that the character could follow
            if len(tokens_can_follow) > 0:
                valid_tokens = [t for t in tokens_can_follow if t.is_valid]
                if len(valid_tokens) == 0:
                    raise LexerError(
                        bad_character=ch,
                        position=self.position,
                        previous_tokens=self._completed_token_list[-MAX_EXCEPTION_TOKENS:],
                        message="No valid token for character",
                    )

                valid_tokens.sort(key=lambda t: t.precedence, reverse=True)
                self._completed_token_list.append(valid_tokens[0])

                all_candidates = self._get_fresh_candidate_tokens()
                next_candidates: list[TokenItem] = []
                for nc in all_candidates:
                    if nc.try_append(ch, self.position) == AppendResult.ACCEPTED:
                        next_candidates.append(nc)

                if len(next_candidates) == 0:
                    raise LexerError(
                        bad_character=ch,
                        position=self.position,
                        previous_tokens=self._completed_token_list[-MAX_EXCEPTION_TOKENS:],
                        message="No token will accept character",
                    )
            else:
                raise LexerError(
                    bad_character=ch,
                    position=self.position,
                    previous_tokens=self._completed_token_list[-MAX_EXCEPTION_TOKENS:],
                    message="No valid action for character",
                )
            self._current_candidates = next_candidates

        self._position += 1

    def character_stream_done(self):
        # Final tidy up, for when we are done pushing characters
        valid_tokens = [t for t in self._current_candidates if t.is_valid]
        if len(valid_tokens) == 0:
            raise LexerError(
                bad_character="",
                position=self.position,
                previous_tokens=self._completed_token_list[-MAX_EXCEPTION_TOKENS:],
                message="No token currently valid at end",
            )

        valid_tokens.sort(key=lambda t: t.precedence, reverse=True)
        self._completed_token_list.append(valid_tokens[0])

    def _get_fresh_candidate_tokens(self) -> list[TokenItem]:
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
