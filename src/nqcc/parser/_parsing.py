from typing import Type, get_args

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
    EqualTo,
    GreaterThan,
    GreaterThanOrEqual,
    IdentifierToken,
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
    SourceEqualTo,
    SourceExpressionNode,
    SourceFunctionNode,
    SourceGreaterThan,
    SourceGreaterThanOrEqual,
    SourceLeftShift,
    SourceLessThan,
    SourceLessThanOrEqual,
    SourceLogicalAnd,
    SourceLogicalNot,
    SourceLogicalOr,
    SourceModulo,
    SourceMultiply,
    SourceNegate,
    SourceNotEqualTo,
    SourceProgramNode,
    SourceReturnNode,
    SourceRightShift,
    SourceStatementNode,
    SourceSubtract,
    SourceUnaryExpressionNode,
    SourceUnaryOperator,
)
from ._token_tape import TokenTape

_UNARY_OPERATOR_MAP: dict[Type, Type] = {
    TildeToken: SourceComplement,
    NegationToken: SourceNegate,
    LogicalNot: SourceLogicalNot,
}

_BINARY_OPERATOR_MAP: dict[Type, Type] = {
    AdditionToken: SourceAdd,
    NegationToken: SourceSubtract,
    MultiplyToken: SourceMultiply,
    DivideToken: SourceDivide,
    ModuloToken: SourceModulo,
    BitwiseAnd: SourceBitwiseAnd,
    BitwiseOr: SourceBitwiseOr,
    BitwiseXor: SourceBitwiseXor,
    LeftShift: SourceLeftShift,
    RightShift: SourceRightShift,
    LogicalAnd: SourceLogicalAnd,
    LogicalOr: SourceLogicalOr,
    EqualTo: SourceEqualTo,
    NotEqualTo: SourceNotEqualTo,
    LessThan: SourceLessThan,
    LessThanOrEqual: SourceLessThanOrEqual,
    GreaterThan: SourceGreaterThan,
    GreaterThanOrEqual: SourceGreaterThanOrEqual,
}


def parse_unary_operator(token_tape: TokenTape) -> SourceUnaryExpressionNode:
    op_token = token_tape.expect(get_args(UnaryOperatorToken))

    if type(op_token) not in _UNARY_OPERATOR_MAP:
        raise ValueError(f"Could not match type of {op_token}")

    op: SourceUnaryOperator = _UNARY_OPERATOR_MAP[type(op_token)](
        start_position=op_token.start_position
    )

    inner_exp = parse_factor(token_tape)
    result = SourceUnaryExpressionNode(
        start_position=op_token.start_position, operator=op, expression=inner_exp
    )

    return result


def convert_binary_operator(lexer_token: Token) -> SourceBinaryOperator | None:  # noqa: C901
    if type(lexer_token) not in _BINARY_OPERATOR_MAP:
        return None
    result_type = _BINARY_OPERATOR_MAP[type(lexer_token)]
    return result_type(start_position=lexer_token.start_position)


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
