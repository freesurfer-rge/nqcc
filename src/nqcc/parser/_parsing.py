from typing import get_args

from nqcc.lexer import (
    AdditionToken,
    BinaryOperatorToken,
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    DivideToken,
    IdentifierToken,
    KeywordToken,
    LeftShift,
    ModuloToken,
    MultiplyToken,
    NegationToken,
    OpenBraceToken,
    OpenParenToken,
    RightShift,
    SemicolonToken,
    TildeToken,
    Token,
    UnaryOperatorToken,
)

from ._exceptions import SourceASTBadValueError
from ._source_ast import (
    SourceAdd,
    SourceBinaryExpressionNode,
    SourceBinaryOperator,
    SourceBitwiseAnd,
    SourceBitwiseOr,
    SourceBitwiseXor,
    SourceComplement,
    SourceConstantIntNode,
    SourceDivide,
    SourceExpressionNode,
    SourceFunctionNode,
    SourceLeftShift,
    SourceModulo,
    SourceMultiply,
    SourceNegate,
    SourceProgramNode,
    SourceReturnNode,
    SourceRightShift,
    SourceStatementNode,
    SourceSubtract,
    SourceUnaryExpressionNode,
    SourceUnaryOperator,
)
from ._token_tape import TokenTape


def parse_unary_operator(token_tape: TokenTape) -> SourceUnaryExpressionNode:
    op_token = token_tape.expect(get_args(UnaryOperatorToken))

    op: SourceUnaryOperator
    match op_token:
        case TildeToken():
            op = SourceComplement(start_position=op_token.start_position)

        case NegationToken():
            op = SourceNegate(start_position=op_token.start_position)

        case _:
            raise ValueError(f"Could not match type of {op_token}")

    inner_exp = parse_factor(token_tape)
    result = SourceUnaryExpressionNode(
        start_position=op_token.start_position, operator=op, expression=inner_exp
    )

    return result


def convert_binary_operator(lexer_token: Token) -> SourceBinaryOperator | None:  # noqa: C901
    match lexer_token:
        case AdditionToken():
            return SourceAdd(start_position=lexer_token.start_position)
        case NegationToken():
            return SourceSubtract(start_position=lexer_token.start_position)
        case MultiplyToken():
            return SourceMultiply(start_position=lexer_token.start_position)
        case DivideToken():
            return SourceDivide(start_position=lexer_token.start_position)
        case ModuloToken():
            return SourceModulo(start_position=lexer_token.start_position)
        case BitwiseAnd():
            return SourceBitwiseAnd(start_position=lexer_token.start_position)
        case BitwiseOr():
            return SourceBitwiseOr(start_position=lexer_token.start_position)
        case BitwiseXor():
            return SourceBitwiseXor(start_position=lexer_token.start_position)
        case LeftShift():
            return SourceLeftShift(start_position=lexer_token.start_position)
        case RightShift():
            return SourceRightShift(start_position=lexer_token.start_position)
        case _:
            # Nothing to do
            return None


def parse_factor(token_tape: TokenTape) -> SourceExpressionNode:
    token = token_tape.peek()

    result: SourceExpressionNode
    match token:
        case ConstantIntegerToken():
            int_token = token_tape.take()
            result = SourceConstantIntNode(
                start_position=int_token.start_position, value=int(int_token.value)
            )

        # See
        # https://github.com/python/cpython/issues/106246
        # for the following ugliness
        # Also get_args is needed to quiet mypy
        # https://docs.python.org/3/library/typing.html#typing.get_args
        case unary if isinstance(unary, get_args(UnaryOperatorToken)):
            result = parse_unary_operator(token_tape)

        case OpenParenToken():
            _ = token_tape.take()
            result = parse_expression(token_tape, min_precedence=0)
            _ = token_tape.expect(CloseParenToken)

        case _:
            raise ValueError(f"Could not match type of {token}")
    return result


def parse_expression(token_tape: TokenTape, *, min_precedence: int) -> SourceExpressionNode:
    left = parse_factor(token_tape)

    operator = convert_binary_operator(token_tape.peek())
    while operator is not None and operator.precedence >= min_precedence:
        # First thing, actually consume the token
        _ = token_tape.expect(get_args(BinaryOperatorToken))

        right = parse_expression(token_tape, min_precedence=1 + operator.precedence)
        left = SourceBinaryExpressionNode(
            start_position=operator.start_position, operator=operator, left=left, right=right
        )

        # Set up for next iteration
        operator = convert_binary_operator(token_tape.peek())
    return left


def parse_statement(token_tape: TokenTape) -> SourceStatementNode:
    return_token = token_tape.expect(KeywordToken)
    if return_token.value != "return":
        raise SourceASTBadValueError(
            expected_value="return", actual_token=return_token, message="Unexpected keyword"
        )
    return_value = parse_expression(token_tape, min_precedence=0)
    _ = token_tape.expect(SemicolonToken)
    return SourceReturnNode(start_position=return_token.start_position, value=return_value)


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


def parse_program(token_tape: TokenTape) -> SourceProgramNode:
    f = parse_function(token_tape)

    if token_tape.tokens_remaining > 0:
        raise ValueError("Did not expect any more tokens")

    return SourceProgramNode(start_position=0, value=f)
