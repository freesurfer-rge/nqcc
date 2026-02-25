import abc
from typing import Literal, MutableSequence

from pydantic import BaseModel

from nqcc.lexer import (
    ConstantIntegerToken,
    ExpressionTokenItem,
    TokenItem,
)


class SourceASTError(ValueError):
    def __init__(self, *, expected_type: type, actual_token: TokenItem, message: str):
        self.expected_type = expected_type
        self.actual_token = actual_token
        self.message = message
        super().__init__(self.message)


class SourceASTNode(BaseModel, abc.ABC):
    type: str
    start_position: int

    @classmethod
    def expect(cls, expected_token_type: type, tokens: MutableSequence[TokenItem]) -> TokenItem:
        # By default, pop takes the _last_ element
        head = tokens.pop(0)
        if not isinstance(head, expected_token_type):
            raise SourceASTError(
                expected_type=expected_token_type,
                actual_token=head,
                message="Received token of unexpected type",
            )
        return head

    @classmethod
    @abc.abstractmethod
    def parse(cls, tokens: MutableSequence[TokenItem]) -> SourceASTNode:
        pass


class SourceExpressionNode(SourceASTNode):
    @classmethod
    def parse(cls, tokens: MutableSequence[TokenItem]) -> SourceASTNode:
        token = cls.expect(ExpressionTokenItem, tokens)

        match token:
            case ConstantIntegerToken():
                result = SourceConstantIntNode(
                    start_position=token.start_position, value=int(token.value)
                )

            case _:
                raise ValueError(f"Could not match type of {token}")

        return result


class SourceConstantIntNode(SourceExpressionNode):
    type: Literal["SourceConstantIntNode"] = "SourceConstantIntNode"
    value: int


class SourceStatementNode(SourceASTNode):
    pass


class SourceReturnNode(SourceStatementNode):
    type: Literal["SourceReturnNode"] = "SourceReturnNode"
    value: SourceExpressionNode


class SourceFunctionDefinitionNode(SourceASTNode):
    pass


class SourceFunctionNode(SourceFunctionDefinitionNode):
    type: Literal["SourceFunctionNode"] = "SourceFunctionNode"
    identifier: str
    body: SourceStatementNode


class SourceProgramDefinitionNode(SourceASTNode):
    pass


class SourceProgramNode(SourceProgramDefinitionNode):
    type: Literal["SourceProgramNode"] = "SourceProgramNode"
    value: SourceFunctionDefinitionNode
