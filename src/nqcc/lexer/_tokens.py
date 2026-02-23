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
