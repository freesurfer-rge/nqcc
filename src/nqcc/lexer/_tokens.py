import abc
import string
from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field


class AppendResult(Enum):
    ACCEPTED = 0
    CAN_FOLLOW = 1
    REJECTED = 2


_NONWORD_CHARS = {c for c in string.printable if (c != "_" and not c.isalnum())}


class Token(BaseModel, abc.ABC):
    type: str
    start_position: int = Field(default=-1)
    value: str = Field(default="")

    @abc.abstractmethod
    def try_append(self, char: str, position: int) -> AppendResult:
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
    def try_append(self, char: str, position: int) -> AppendResult:
        assert len(char) == 1, f"Got '{char}' and not single character"

        if not self.value:
            if self._allowed_first(char):
                self.start_position = position
                self.value = char
                return AppendResult.ACCEPTED
        else:
            assert position == self.start_position + len(self.value)
            if self._allowed_subsequent(char):
                self.value += char
                return AppendResult.ACCEPTED
            elif self._can_follow(char):
                return AppendResult.CAN_FOLLOW

        return AppendResult.REJECTED

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

    @abc.abstractmethod
    def _can_follow(self, char: str) -> bool:
        pass


class IdentifierToken(FirstSubsequentToken):
    type: Literal["IdentifierToken"] = "IdentifierToken"

    _FIRST_CHARS = {*string.ascii_letters, "_"}
    _SUBSEQUENT_CHARS = {*string.ascii_letters, *string.digits, "_"}

    def _allowed_first(self, char: str) -> bool:
        return char in self._FIRST_CHARS

    def _allowed_subsequent(self, char: str) -> bool:
        return char in self._SUBSEQUENT_CHARS

    def _can_follow(self, char):
        return char in _NONWORD_CHARS

    @property
    def precedence(self) -> int:
        return 5


class ConstantIntegerToken(FirstSubsequentToken):
    type: Literal["ConstantIntegerToken"] = "ConstantIntegerToken"

    def _allowed_first(self, char: str) -> bool:
        return char in string.digits

    def _allowed_subsequent(self, char: str) -> bool:
        return char in string.digits

    def _can_follow(self, char):
        return char in _NONWORD_CHARS

    @property
    def precedence(self) -> int:
        return 5


class WhitespaceToken(FirstSubsequentToken):
    type: Literal["WhitespaceToken"] = "WhitespaceToken"

    def _allowed_first(self, char: str) -> bool:
        return char in string.whitespace

    def _allowed_subsequent(self, char: str) -> bool:
        return char in string.whitespace

    def _can_follow(self, _: str):
        return True

    @property
    def precedence(self) -> int:
        return -5


class KeywordToken(Token):
    type: Literal["KeywordToken"] = "KeywordToken"

    _KEYWORDS = {"int", "void", "return"}

    def try_append(self, char: str, position: int) -> AppendResult:
        assert len(char) == 1, f"Got '{char}' and not single character"
        if self.value:
            assert position == self.start_position + len(self.value)

        tst_value = self.value + char

        valid_prefix = [s.startswith(tst_value) for s in self._KEYWORDS]

        if any(valid_prefix):
            if not self.value:
                self.start_position = position
            self.value = tst_value
            return AppendResult.ACCEPTED
        else:
            if char in _NONWORD_CHARS:
                return AppendResult.CAN_FOLLOW
            else:
                return AppendResult.REJECTED

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

    def try_append(self, char: str, position: int) -> AppendResult:
        assert len(char) == 1, f"Got '{char}' and not single character"

        if self.value:
            return AppendResult.CAN_FOLLOW

        if char != self.allowed_character:
            return AppendResult.REJECTED

        self.value = char
        self.start_position = position
        return AppendResult.ACCEPTED

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
    type: Literal["OpenParenToken"] = "OpenParenToken"

    @property
    def allowed_character(self) -> str:
        return "("


class CloseParenToken(SingleCharacterToken):
    type: Literal["CloseParenToken"] = "CloseParenToken"

    @property
    def allowed_character(self) -> str:
        return ")"


class OpenBraceToken(SingleCharacterToken):
    type: Literal["OpenBraceToken"] = "OpenBraceToken"

    @property
    def allowed_character(self) -> str:
        return "{"


class CloseBraceToken(SingleCharacterToken):
    type: Literal["CloseBraceToken"] = "CloseBraceToken"

    @property
    def allowed_character(self) -> str:
        return "}"


class SemicolonToken(SingleCharacterToken):
    type: Literal["SemicolonToken"] = "SemicolonToken"

    @property
    def allowed_character(self) -> str:
        return ";"


TokenItem = Union[
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
]

ExpressionTokenItem = Union[ConstantIntegerToken]