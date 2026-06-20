import re

from ._tokens import DecrementToken, Token, TokenTypes


class LexerMatchError(Exception):
    def __init__(self, *, position: int):
        self.position = position
        self.message = "Lexer failed to match"
        super().__init__(f"{self.message} at position {self.position}")


def extract_tokens(s: str, idx: int) -> list[Token]:
    assert not s[0].isspace()

    candidates = []
    for tt in TokenTypes:
        assert issubclass(tt, Token)
        m = re.match(tt.re(), s)
        if m and len(m.group(0)) > 0:
            # Following has a suppression because the subclasses enforce
            # a token_type argument but this isn't being picked up
            candidate_token = tt(start_position=idx, value=m.group(0))  # type: ignore[call-arg]
            candidates.append(candidate_token)
    if len(candidates) == 0:
        raise LexerMatchError(position=idx)

    return candidates


def pick_token(tokens: list[Token]) -> Token:
    assert len(tokens) > 0, "Must have at least one token!"
    if len(tokens) == 1:
        return tokens[0]

    # First filter is for the longest match
    max_length = max(len(x.value) for x in tokens)
    remaining = [t for t in tokens if len(t.value) == max_length]
    if len(remaining) == 1:
        return remaining[0]

    # If multiple matches, take the highest
    # precedence
    result = remaining[0]
    for t in remaining:
        if t.precedence > result.precedence:
            result = t
    return result


def lex_string(c_program_str: str) -> list[Token]:
    # We won't want to change the supplied string
    s = str(c_program_str)

    idx = 0
    lex_tokens = []
    while s:
        # Consume the string

        # Remove the whitespace at the front
        old_len = len(s)
        s = s.lstrip()
        if not s:
            break
        idx += old_len - len(s)

        # Get the next token
        candidates = extract_tokens(s, idx)
        selection = pick_token(candidates)
        assert not isinstance(selection, DecrementToken), "Not currently supported"

        # Update position and remove the token
        idx += len(selection.value)
        s = s[len(selection.value) :]

        # Add to the result
        lex_tokens.append(selection)
    return lex_tokens
