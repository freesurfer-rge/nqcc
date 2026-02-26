import abc
from typing import Literal, Union

from pydantic import BaseModel

from nqcc.lexer import (
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    ExpressionTokenItem,
    IdentifierToken,
    KeywordToken,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
)

from ._exceptions import SourceASTBadValueError
from ._token_tape import TokenTape


class SourceASTNode(BaseModel, abc.ABC):
    node_type: str
    start_position: int


class SourceExpressionNode(SourceASTNode):
    @classmethod
    def parse_token_tape(cls, token_tape: TokenTape) -> SourceExpressionNode:
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


SourceASTExpressionNode = Union[SourceExpressionNode, SourceConstantIntNode]


class SourceStatementNode(SourceASTNode):
    @classmethod
    def parse_token_tape(cls, token_tape: TokenTape) -> SourceStatementNode:
        return_token = token_tape.expect(KeywordToken)
        if return_token.value != "return":
            raise SourceASTBadValueError(
                expected_value="return", actual_token=return_token, message="Unexpected keyword"
            )
        return_value: SourceASTExpressionNode = SourceExpressionNode.parse_token_tape(token_tape)
        _ = token_tape.expect(SemicolonToken)
        return SourceReturnNode(start_position=return_token.start_position, value=return_value)


class SourceReturnNode(SourceStatementNode):
    node_type: Literal["SourceReturnNode"] = "SourceReturnNode"
    value: SourceASTExpressionNode


SourceASTStatementNode = Union[SourceStatementNode, SourceReturnNode]


class SourceFunctionDefinitionNode(SourceASTNode):
    @classmethod
    def parse_token_tape(cls, token_tape: TokenTape) -> SourceFunctionDefinitionNode:
        type_token = token_tape.expect(KeywordToken)
        if type_token.value != "int":
            raise SourceASTBadValueError(
                expected_value="int", actual_token=type_token, message="Unexpected return type"
            )
        function_name_token = token_tape.expect(IdentifierToken)

        _ = token_tape.expect(OpenParenToken)
        arg_token = token_tape.expect(KeywordToken)
        if arg_token.value != "void":
            raise SourceASTBadValueError(
                expected_value="void", actual_token=arg_token, message="Unexpected arguments"
            )
        _ = token_tape.expect(CloseParenToken)

        _ = token_tape.expect(OpenBraceToken)
        body_statement = SourceStatementNode.parse_token_tape(token_tape)
        _ = token_tape.expect(CloseBraceToken)

        return SourceFunctionNode(
            identifier=function_name_token.value,
            body=body_statement,
            start_position=type_token.start_position,
        )


class SourceFunctionNode(SourceFunctionDefinitionNode):
    node_type: Literal["SourceFunctionNode"] = "SourceFunctionNode"
    identifier: str
    body: SourceASTStatementNode


SourceASTFunctionNode = Union[SourceFunctionDefinitionNode, SourceFunctionNode]


class SourceProgramDefinitionNode(SourceASTNode):
    pass


class SourceProgramNode(SourceProgramDefinitionNode):
    node_type: Literal["SourceProgramNode"] = "SourceProgramNode"
    value: SourceASTFunctionNode
