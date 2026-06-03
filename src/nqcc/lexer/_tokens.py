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


_KEYWORDS = {
    "break",
    "continue",
    "do",
    "else",
    "extern",
    "for",
    "if",
    "int",
    "return",
    "static",
    "void",
    "while",
}


class KeywordToken(Token):
    token_type: Literal["KeywordToken"] = "KeywordToken"

    @property
    def precedence(self) -> int:
        return 10

    @classmethod
    def re(cls) -> str:
        keyword_alternatives = "|".join(_KEYWORDS)
        return f"({keyword_alternatives})\\b"


class AssignmentToken(Token):
    token_type: Literal["AssignmentToken"] = "AssignmentToken"
    value: Literal["="] = "="

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "="


class TildeToken(Token):
    token_type: Literal["TildeToken"] = "TildeToken"
    value: Literal["~"] = "~"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "~"


class NegationToken(Token):
    token_type: Literal["NegationToken"] = "NegationToken"
    value: Literal["-"] = "-"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "-"


class AdditionToken(Token):
    token_type: Literal["AdditionToken"] = "AdditionToken"
    value: Literal["+"] = "+"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[+]"


class DecrementToken(Token):
    token_type: Literal["DecrementToken"] = "DecrementToken"
    value: Literal["--"] = "--"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "--"


class IncrementToken(Token):
    token_type: Literal["IncrementToken"] = "IncrementToken"
    value: Literal["++"] = "++"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[+][+]"


class MultiplyToken(Token):
    token_type: Literal["MultiplyToken"] = "MultiplyToken"
    value: Literal["*"] = "*"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[*]"


class DivideToken(Token):
    token_type: Literal["DivideToken"] = "DivideToken"
    value: Literal["/"] = "/"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "/"


class ModuloToken(Token):
    token_type: Literal["ModuloToken"] = "ModuloToken"
    value: Literal["%"] = "%"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "%"


class BitwiseAnd(Token):
    token_type: Literal["BitwiseAnd"] = "BitwiseAnd"
    value: Literal["&"] = "&"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "&"


class BitwiseOr(Token):
    token_type: Literal["BitwiseOr"] = "BitwiseOr"
    value: Literal["|"] = "|"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[|]"


class BitwiseXor(Token):
    token_type: Literal["BitwiseXor"] = "BitwiseXor"
    value: Literal["^"] = "^"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "\\^"


class LeftShift(Token):
    token_type: Literal["LeftShift"] = "LeftShift"
    value: Literal["<<"] = "<<"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "<<"


class RightShift(Token):
    token_type: Literal["RightShift"] = "RightShift"
    value: Literal[">>"] = ">>"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return ">>"


class LogicalNot(Token):
    token_type: Literal["LogicalNot"] = "LogicalNot"
    value: Literal["!"] = "!"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "!"


class LogicalAnd(Token):
    token_type: Literal["LogicalAnd"] = "LogicalAnd"
    value: Literal["&&"] = "&&"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "&&"


class LogicalOr(Token):
    token_type: Literal["LogicalOr"] = "LogicalOr"
    value: Literal["||"] = "||"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[|][|]"


class EqualTo(Token):
    token_type: Literal["EqualTo"] = "EqualTo"
    value: Literal["=="] = "=="

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "=="


class NotEqualTo(Token):
    token_type: Literal["NotEqualTo"] = "NotEqualTo"
    value: Literal["!="] = "!="

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "!="


class LessThan(Token):
    token_type: Literal["LessThan"] = "LessThan"
    value: Literal["<"] = "<"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "<"


class LessThanOrEqual(Token):
    token_type: Literal["LessThanOrEqual"] = "LessThanOrEqual"
    value: Literal["<="] = "<="

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "<="


class GreaterThan(Token):
    token_type: Literal["GreaterThan"] = "GreaterThan"
    value: Literal[">"] = ">"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return ">"


class GreaterThanOrEqual(Token):
    token_type: Literal["GreaterThanOrEqual"] = "GreaterThanOrEqual"
    value: Literal[">="] = ">="

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return ">="


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


class QuestionMarkToken(Token):
    token_type: Literal["QuestionMarkToken"] = "QuestionMarkToken"
    value: Literal["?"] = "?"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[?]"


class ColonToken(Token):
    token_type: Literal["ColonToken"] = "ColonToken"
    value: Literal[":"] = ":"

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return "[:]"


class CommaToken(Token):
    token_type: Literal["CommaToken"] = "CommaToken"
    value: Literal[","] = ","

    @property
    def precedence(self) -> int:
        return 5

    @classmethod
    def re(cls) -> str:
        return ","


TokenTypes: list[type] = [
    AdditionToken,
    AssignmentToken,
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    CloseBraceToken,
    CloseParenToken,
    ColonToken,
    CommaToken,
    ConstantIntegerToken,
    DecrementToken,
    DivideToken,
    EqualTo,
    GreaterThan,
    GreaterThanOrEqual,
    IdentifierToken,
    IncrementToken,
    KeywordToken,
    LeftShift,
    LessThan,
    LessThanOrEqual,
    LogicalAnd,
    LogicalNot,
    LogicalOr,
    ModuloToken,
    MultiplyToken,
    NegationToken,
    NotEqualTo,
    OpenBraceToken,
    OpenParenToken,
    QuestionMarkToken,
    RightShift,
    SemicolonToken,
    TildeToken,
]

UnaryOperatorToken = Union[DecrementToken, IncrementToken, LogicalNot, NegationToken, TildeToken]
BinaryOperatorToken = Union[
    AdditionToken,
    AssignmentToken,
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    DivideToken,
    EqualTo,
    GreaterThan,
    GreaterThanOrEqual,
    LeftShift,
    LessThan,
    LessThanOrEqual,
    LogicalAnd,
    LogicalOr,
    ModuloToken,
    MultiplyToken,
    NegationToken,
    NotEqualTo,
    QuestionMarkToken,
    RightShift,
]
