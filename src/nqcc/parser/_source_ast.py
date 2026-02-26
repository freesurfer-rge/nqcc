import abc
from typing import Literal

from pydantic import BaseModel

from nqcc.lexer import (
    ConstantIntegerToken,
    ExpressionTokenItem,
    KeywordToken,
    SemicolonToken
)

from ._exceptions import SourceASTBadValueError
from ._token_tape import TokenTape


class SourceASTNode(BaseModel, abc.ABC):
    node_type: str
    start_position: int

    @classmethod
    @abc.abstractmethod
    def parse(cls, token_tape: TokenTape) -> SourceASTNode:
        pass


class SourceExpressionNode(SourceASTNode):
    @classmethod
    def parse(cls, token_tape: TokenTape) -> SourceASTNode:
        token = token_tape.expect(ExpressionTokenItem)

        match token:
            case ConstantIntegerToken():
                result = SourceConstantIntNode(
                    start_position=token.start_position, value=int(token.value)
                )

            case _:
                raise ValueError(f"Could not match type of {token}")

        return result


class SourceConstantIntNode(SourceExpressionNode):
    node_type: Literal["SourceConstantIntNode"] = "SourceConstantIntNode"
    value: int


class SourceStatementNode(SourceASTNode):
    @classmethod
    def parse(cls, token_tape: TokenTape) -> SourceASTNode:
        return_token = token_tape.expect(KeywordToken)
        if return_token.value != "return":
            raise SourceASTBadValueError(expected_value="return", actual_token=return_token, message="Unexpected keyword")
        return_value = SourceExpressionNode.parse(token_tape)
        _ = token_tape.expect(SemicolonToken)
        return SourceReturnNode(start_position=return_token.start_position, value=return_value)




class SourceReturnNode(SourceStatementNode):
    node_type: Literal["SourceReturnNode"] = "SourceReturnNode"
    value: SourceExpressionNode


class SourceFunctionDefinitionNode(SourceASTNode):
    pass


class SourceFunctionNode(SourceFunctionDefinitionNode):
    node_type: Literal["SourceFunctionNode"] = "SourceFunctionNode"
    identifier: str
    body: SourceStatementNode


class SourceProgramDefinitionNode(SourceASTNode):
    pass


class SourceProgramNode(SourceProgramDefinitionNode):
    node_type: Literal["SourceProgramNode"] = "SourceProgramNode"
    value: SourceFunctionDefinitionNode
