import abc
import string

from pydantic import BaseModel, Field


class Token(BaseModel, abc.ABC):
    start_position: int = Field(default=-1)
    value: str = Field(default="")

    @abc.abstractmethod
    def try_append(self, char: str, position: int) -> bool:
        pass

    @property
    @abc.abstractmethod
    def is_valid(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def is_appendable(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def precedence(self) -> int:
        pass


class FirstSubsequentToken(Token):
    def try_append(self, char: str, position: int) -> bool:
        assert len(char) == 1, f"Got '{char}' and not single character"

        if not self.value:
            if self._allowed_first(char):
                self.start_position = position
                self.value = char
                return True
        else:
            assert position == self.start_position + len(self.value)
            if self._allowed_subsequent(char):
                self.value += char
                return True
        return False

    @property
    def is_valid(self) -> bool:
        return len(self.value) > 0

    @property
    def is_appendable(self) -> bool:
        return True

    @abc.abstractmethod
    def _allowed_first(self, char: str) -> bool:
        pass

    @abc.abstractmethod
    def _allowed_subsequent(self, char: str) -> bool:
        pass


class IdentifierToken(FirstSubsequentToken):
    _FIRST_CHARS = {*string.ascii_letters, "_"}
    _SUBSEQUENT_CHARS = {*string.ascii_letters, *string.digits, "_"}

    def _allowed_first(self, char: str) -> bool:
        return char in self._FIRST_CHARS

    def _allowed_subsequent(self, char: str) -> bool:
        return char in self._SUBSEQUENT_CHARS

    @property
    def precedence(self) -> int:
        return 5


class ConstantIntegerToken(FirstSubsequentToken):
    def _allowed_first(self, char: str) -> bool:
        return char in string.digits

    def _allowed_subsequent(self, char: str) -> bool:
        return char in string.digits

    @property
    def precedence(self) -> int:
        return 5


class WhitespaceToken(FirstSubsequentToken):
    def _allowed_first(self, char: str) -> bool:
        return char in string.whitespace

    def _allowed_subsequent(self, char: str) -> bool:
        return char in string.whitespace

    @property
    def precedence(self) -> int:
        return -5


class KeywordToken(Token):
    _KEYWORDS = {"int", "void", "return"}

    def try_append(self, char: str, position: int) -> bool:
        assert len(char) == 1, f"Got '{char}' and not single character"
        if self.value:
            assert position == self.start_position + len(self.value)

        tst_value = self.value + char

        valid_prefix = [s.startswith(tst_value) for s in self._KEYWORDS]

        if any(valid_prefix):
            if not self.value:
                self.start_position = position
            self.value = tst_value
            return True
        return False

    @property
    def is_valid(self) -> bool:
        return self.value in self._KEYWORDS

    @property
    def is_appendable(self) -> bool:
        return not self.is_valid

    @property
    def precedence(self) -> int:
        return 10


class SingleCharacterToken(Token):
    @property
    @abc.abstractmethod
    def allowed_character(self) -> str:
        pass

    def try_append(self, char: str, position: int) -> bool:
        assert len(char) == 1, f"Got '{char}' and not single character"

        if self.value:
            return False

        if char != self.allowed_character:
            return False

        self.value = char
        self.start_position = position
        return True

    @property
    def is_valid(self) -> bool:
        return self.value == self.allowed_character

    @property
    def is_appendable(self) -> bool:
        return not self.is_valid

    @property
    def precedence(self) -> int:
        return 5


class OpenParenToken(SingleCharacterToken):
    @property
    def allowed_character(self) -> str:
        return "("


class CloseParenToken(SingleCharacterToken):
    @property
    def allowed_character(self) -> str:
        return ")"


class OpenBraceToken(SingleCharacterToken):
    @property
    def allowed_character(self) -> str:
        return "{"


class CloseBraceToken(SingleCharacterToken):
    @property
    def allowed_character(self) -> str:
        return "}"


class SemicolonToken(SingleCharacterToken):
    @property
    def allowed_character(self) -> str:
        return ";"


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
        assert len(ch)==1,"Must only pass single characters!"

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
            
            valid_tokens.sort(key = lambda t: t.precedence, reverse=True)
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
        if len(valid_tokens)==0:
            candidate_strings = [t.model_jump_json() for t in self._current_candidates]
            all_candidate_str = ", ".join(candidate_strings)
            msg = "No token currently valid: " + all_candidate_str
            raise ValueError(msg)
        
        valid_tokens.sort(key = lambda t: t.precedence, reverse=True)
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
