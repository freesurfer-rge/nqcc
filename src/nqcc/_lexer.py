import abc
import string

from pydantic import BaseModel, Field


class Token(BaseModel, abc.ABC):
    start_position: int = Field(default=-1)
    value: str = Field(default="")

    @abc.abstractmethod
    def try_append(self, char: str, position: int) -> bool:
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


class ConstantIntegerToken(FirstSubsequentToken):
    def _allowed_first(self, char: str) -> bool:
        return char in string.digits

    def _allowed_subsequent(self, char: str) -> bool:
        return char in string.digits


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


class SingleCharacterToken(Token):
    @abc.abstractproperty
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
