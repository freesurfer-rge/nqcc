import abc
import string

from pydantic import BaseModel


class Token(BaseModel, abc.ABC):
    start_position: int
    value: str

    @abc.abstractmethod
    def append(self, char: str, position: int) -> bool:
        pass


class IdentifierToken(Token):
    def append(self, char: str, position: int) -> bool:
        assert len(char) == 1, f"Got {char} not single character"

        if not self.value:
            if char == "_" or char in string.ascii_letters:
                self.start_position = position
                self.value = char
                return True
        else:
            if char == "_" or char in string.ascii_letters or char in string.digits:
                self.value += char
                return True
        return False
