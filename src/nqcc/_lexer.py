import abc
import string

from pydantic import BaseModel, Field


class Token(BaseModel, abc.ABC):
    start_position: int = Field(default=-1)
    value: str = Field(default="")

    def append(self, char: str, position: int) -> bool:
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


class IdentifierToken(Token):
    _FIRST_CHARS = {*string.ascii_letters, "_"}
    _SUBSEQUENT_CHARS = {*string.ascii_letters, *string.digits, "_"}

    def _allowed_first(self, char: str) -> bool:
        return char in self._FIRST_CHARS

    def _allowed_subsequent(self, char: str) -> bool:
        return char in self._SUBSEQUENT_CHARS


class ConstantIntegerToken(Token):
    def _allowed_first(self, char: str) -> bool:
        return char in string.digits

    def _allowed_subsequent(self, char: str) -> bool:
        return char in string.digits
