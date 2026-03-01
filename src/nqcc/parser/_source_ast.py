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


class SourceASTNode(BaseModel):
    node_type: str
    start_position: int


def parse_expression(token_tape: TokenTape) -> SourceExpressionNode:
    token = token_tape.expect(ExpressionTokenItem)

    match token:
        case ConstantIntegerToken():
            result = SourceConstantIntNode(
                start_position=token.start_position, value=int(token.value)
            )

        case _:
            raise ValueError(f"Could not match type of {token}")

    return result


class SourceConstantIntNode(SourceASTNode):
    node_type: Literal["SourceConstantIntNode"] = "SourceConstantIntNode"
    value: int


SourceExpressionNode = Union[SourceConstantIntNode]


def parse_statement(token_tape: TokenTape) -> SourceStatementNode:
    return_token = token_tape.expect(KeywordToken)
    if return_token.value != "return":
        raise SourceASTBadValueError(
            expected_value="return", actual_token=return_token, message="Unexpected keyword"
        )
    return_value = parse_expression(token_tape)
    _ = token_tape.expect(SemicolonToken)
    return SourceReturnNode(start_position=return_token.start_position, value=return_value)


class SourceReturnNode(SourceASTNode):
    node_type: Literal["SourceReturnNode"] = "SourceReturnNode"
    value: SourceExpressionNode


SourceStatementNode = Union[SourceReturnNode]


def parse_function(token_tape: TokenTape) -> SourceFunctionNode:
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
    body_statement = parse_statement(token_tape)
    _ = token_tape.expect(CloseBraceToken)

    return SourceFunctionNode(
        identifier=function_name_token.value,
        body=body_statement,
        start_position=type_token.start_position,
    )


class SourceFunctionNode(SourceASTNode):
    node_type: Literal["SourceFunctionNode"] = "SourceFunctionNode"
    identifier: str
    body: SourceStatementNode


class SourceProgramNode(SourceASTNode):
    node_type: Literal["SourceProgramNode"] = "SourceProgramNode"
    value: SourceFunctionNode


def parse_program(token_tape: TokenTape) -> SourceProgramNode:
    f = parse_function(token_tape)

    if token_tape.tokens_remaining > 0:
        raise ValueError("Did not expect any more tokens")

    return SourceProgramNode(start_position=0, value=f)
