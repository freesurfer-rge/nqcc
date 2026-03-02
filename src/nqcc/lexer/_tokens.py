import abc
from typing import Literal, Union

from pydantic import BaseModel, Field


class Token(BaseModel, abc.ABC):
    token_type: str
    start_position: int = Field(default=-1)
    value: str = Field(default="")

    @property
    @abc.abstractmethod
    def precedence(self) -> int:
        pass

    @classmethod
    @abc.abstractmethod
    def re(cls) -> str:
        pass


class IdentifierToken(Token):
    token_type: Literal["IdentifierToken"] = "IdentifierToken"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[a-zA-Z_]\\w*\\b"


class ConstantIntegerToken(Token):
    token_type: Literal["ConstantIntegerToken"] = "ConstantIntegerToken"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[0-9]+\\b"


_KEYWORDS = {"int", "return", "void"}


class KeywordToken(Token):
    token_type: Literal["KeywordToken"] = "KeywordToken"

    @property
    def precedence(self) -> int:
        return 10

    @classmethod
    def re(cls) -> str:
        keyword_alternatives = "|".join(_KEYWORDS)
        return f"({keyword_alternatives})\\b"


class OpenParenToken(Token):
    token_type: Literal["OpenParenToken"] = "OpenParenToken"
    value: Literal["("] = "("

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[(]"


class CloseParenToken(Token):
    token_type: Literal["CloseParenToken"] = "CloseParenToken"
    value: Literal[")"] = ")"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[)]"


class OpenBraceToken(Token):
    token_type: Literal["OpenBraceToken"] = "OpenBraceToken"
    value: Literal["{"] = "{"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[{]"


class CloseBraceToken(Token):
    token_type: Literal["CloseBraceToken"] = "CloseBraceToken"
    value: Literal["}"] = "}"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[}]"


class SemicolonToken(Token):
    token_type: Literal["SemicolonToken"] = "SemicolonToken"
    value: Literal[";"] = ";"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[;]"


TokenTypes = [
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    IdentifierToken,
    KeywordToken,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
]

TokenItem = Union[
    Token,
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    IdentifierToken,
    KeywordToken,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
]

ExpressionTokenItem = Union[ConstantIntegerToken]
