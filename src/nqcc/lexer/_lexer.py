import re

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
    Token,
    TokenItem,
    TokenTypes,
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


class LexerMatchError(Exception):
    def __init__(self, *, position: int):
        self.position = position
        self.message = "Lexer Failed to match"
        super().__init__(f"{self.message} at position {self.position}")


class Lexer:
    """
    Convert C source into tokens

    To use, iterate over the C source, calling push_character()
    repeatedly. When complete, call character_stream_done() to
    finalise the token list. The list itself can be accessed via
    the completed_token_list property (this will exclude whitespace)
    """

    def __init__(self) -> None:
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
        """
        Process the next character

        Internally, an object of this class maintains a list of candidate tokens.
        This method presents the character to each candidate, and can get three
        possible responses:

        - The token accepts the character
        - The token rejects the character
        - The token rejects the character, but can be followed by it

        The third case is required to distinguish between valid strings like "123;foo"
        and "123foo" which is not.

        If any of the candidate tokens accepted the character, then they become
        the new candidate tokens. If all the candidates reject the character then
        the lexing has failed and an LexerError raised. If there are candidate tokens
        which rejected the character but can be followed by it (and there are no
        tokens which accepted the character), then:

        - The reject-but-follow token is added to the list of completed tokens
        - A fresh list of candidate tokens is created
        - The character is offered to each of the new candidates
        - Those which accept the character become the new list of candidate tokens

        Each token type also has a precedence, which is used to (for example)
        determine that 'main' is an identifier but 'int' is a keyword.
        """

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
                next_candidates = self._handle_can_follow_tokens(ch, tokens_can_follow)
            else:
                raise LexerError(
                    bad_character=ch,
                    position=self.position,
                    previous_tokens=self.completed_token_list[-MAX_EXCEPTION_TOKENS:],
                    message="No valid action for character",
                )
            self._current_candidates = next_candidates

        self._position += 1

    def _handle_can_follow_tokens(self, ch: str, tokens_can_follow: list[TokenItem]):
        """
        Handle character which has finished a token

        This is the trickier case. We have to look through the current list of candidate
        tokens which can be followed by the character, and find which are valid. If there
        are none, then we have a bad lexing. If multiple candidates would be valid, we
        take the one with the highest precedence.

        This done, we create a fresh list of candidate tokens, and offer the rejected
        character to each. Those tokens which accept it become the new list of candidate
        tokens.
        """
        valid_tokens = [t for t in tokens_can_follow if t.is_valid]
        if len(valid_tokens) == 0:
            raise LexerError(
                bad_character=ch,
                position=self.position,
                previous_tokens=self.completed_token_list[-MAX_EXCEPTION_TOKENS:],
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
                previous_tokens=self.completed_token_list[-MAX_EXCEPTION_TOKENS:],
                message="No token will accept character",
            )

        return next_candidates

    def character_stream_done(self):
        """
        Indicate that the C source file is complete

        This looks at the list of tokens which are currently valid in the
        source, and appends the one with the highest precedence to the
        list of completed tokens. If none are currently valid, it raises
        an LexerError.
        """
        # Final tidy up, for when we are done pushing characters
        valid_tokens = [t for t in self._current_candidates if t.is_valid]
        if len(valid_tokens) == 0:
            raise LexerError(
                bad_character="",
                position=self.position,
                previous_tokens=self.completed_token_list[-MAX_EXCEPTION_TOKENS:],
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


def extract_tokens(s: str, idx: int) -> list[TokenItem]:
    assert not s[0].isspace()

    candidates = []
    for tt in TokenTypes:
        assert issubclass(tt, Token)
        m = re.match(tt.re(), s)
        if m and len(m.group(0)) > 0:
            candidate_token = tt(start_position=idx, value=m.group(0))
            candidates.append(candidate_token)
    if len(candidates) == 0:
        raise LexerMatchError(position=idx)

    return candidates


def pick_token(tokens: list[TokenItem]) -> TokenItem:
    pass


def lex_string(c_program_str: str) -> list[TokenItem]:
    # We won't want to change the supplied string
    s = str(c_program_str)
    idx = 0

    while s:
        old_len = len(s)
        s = s.lstrip()
        idx += old_len - len(s)

        candidates = extract_tokens(s, idx)
