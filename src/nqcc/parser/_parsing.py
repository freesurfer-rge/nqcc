from typing import Type, get_args

from nqcc.lexer import (
    AdditionToken,
    AssignmentToken,
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
    QuestionMarkToken,
    ColonToken,
    UnaryOperatorToken,
)

from ._exceptions import SourceASTBadValueError
from ._source_ast import (
    SourceAdd,
    SourceAssignment,
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceBinaryOperator,
    SourceBitwiseAnd,
    SourceBitwiseOr,
    SourceBitwiseXor,
    SourceBlockItemNode,
    SourceComplement,
    SourceConstantIntNode,
    SourceDeclarationNode,
    SourceDivide,
    SourceEqualTo,
    SourceExpressionNode,
    SourceExpressionStatementNode,
    SourceFunctionNode,
    SourceGreaterThan,
    SourceGreaterThanOrEqual,
    SourceIfStatementNode,
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
    SourceNullStatementNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceRightShift,
    SourceStatementNode,
    SourceSubtract,
    SourceUnaryExpressionNode,
    SourceUnaryOperator,
    SourceVarNode,
    SourceTernary,
)
from ._token_tape import TokenTape

_UNARY_OPERATOR_MAP: dict[Type, Type] = {
    TildeToken: SourceComplement,
    NegationToken: SourceNegate,
    LogicalNot: SourceLogicalNot,
}

_BINARY_OPERATOR_MAP: dict[Type, Type] = {
    AssignmentToken: SourceAssignment,
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
    QuestionMarkToken: SourceTernary,
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


def convert_binary_operator(lexer_token: Token) -> SourceBinaryOperator | None:
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

        case IdentifierToken():
            id_token = token_tape.take()
            return SourceVarNode(start_position=id_token.start_position, identifier=id_token.value)

        case _:
            raise ValueError(f"Could not match type of {token}")
    return result


def parse_expression(token_tape: TokenTape, *, min_precedence: int) -> SourceExpressionNode:
    left = parse_factor(token_tape)

    operator = convert_binary_operator(token_tape.peek())
    while operator is not None and operator.precedence >= min_precedence:
        # First thing, actually consume the token
        lex_op = token_tape.expect(get_args(BinaryOperatorToken))
        match lex_op:
            case AssignmentToken():
                right_assign = parse_expression(token_tape, min_precedence=operator.precedence)
                left = SourceAssignmentNode(
                    start_position=lex_op.start_position, left=left, right=right_assign
                )
            case _:
                right = parse_expression(token_tape, min_precedence=1 + operator.precedence)
                left = SourceBinaryExpressionNode(
                    start_position=operator.start_position,
                    operator=operator,
                    left=left,
                    right=right,
                )

        # Set up for next iteration
        operator = convert_binary_operator(token_tape.peek())
    return left


def parse_statement(token_tape: TokenTape) -> SourceStatementNode:
    first_token = token_tape.peek()
    sp = first_token.start_position

    match first_token:
        case SemicolonToken():
            _ = token_tape.take()
            return SourceNullStatementNode(start_position=first_token.start_position)
        case KeywordToken():
            keyword_token = token_tape.expect(KeywordToken)
            match keyword_token.value:
                case "return":
                    return_value = parse_expression(token_tape, min_precedence=0)
                    _ = token_tape.expect(SemicolonToken)
                    return SourceReturnNode(start_position=sp, value=return_value)
                case "if":
                    _ = token_tape.expect(OpenParenToken)
                    if_cond = parse_expression(token_tape, min_precedence=0)
                    _ = token_tape.expect(CloseParenToken)
                    if_then = parse_statement(token_tape)

                    if_otherwise = None
                    tok_else = token_tape.peek()
                    if isinstance(tok_else, KeywordToken) and (tok_else.value == "else"):
                        _ = token_tape.expect(KeywordToken)
                        if_otherwise = parse_statement(token_tape)

                    return SourceIfStatementNode(
                        start_position=sp, condition=if_cond, then=if_then, otherwise=if_otherwise
                    )

                case _:
                    raise SourceASTBadValueError(
                        expected_value="keyword",
                        actual_token=first_token,
                        message="Unexpected keyword",
                    )
        case _:
            expr = parse_expression(token_tape, min_precedence=0)
            _ = token_tape.expect(SemicolonToken)
            return SourceExpressionStatementNode(start_position=expr.start_position, value=expr)


def parse_declaration(token_tape: TokenTape) -> SourceDeclarationNode:
    type_token = token_tape.expect(KeywordToken)
    assert type_token.value == "int", "Can only handle int declarations!"

    name_token = token_tape.expect(IdentifierToken)
    assert isinstance(name_token, IdentifierToken), "Expected variable name!"
    var = SourceVarNode(start_position=name_token.start_position, identifier=name_token.value)

    initialiser: SourceExpressionNode | None = None
    if not isinstance(token_tape.peek(), SemicolonToken):
        _ = token_tape.expect(AssignmentToken)
        initialiser = parse_expression(token_tape, min_precedence=0)
    _ = token_tape.expect(SemicolonToken)

    return SourceDeclarationNode(
        start_position=type_token.start_position, identifier=var, initial=initialiser
    )


def parse_block(token_tape: TokenTape) -> SourceBlockItemNode:
    peeked = token_tape.peek()

    # Only support 'int' declarations right now
    if isinstance(peeked, KeywordToken) and peeked.value == "int":
        return parse_declaration(token_tape)

    return parse_statement(token_tape)


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
    body_block: list[SourceBlockItemNode] = []
    while not isinstance(token_tape.peek(), CloseBraceToken):
        nxt_block = parse_block(token_tape)
        body_block.append(nxt_block)

    _ = token_tape.expect(CloseBraceToken)

    return SourceFunctionNode(
        identifier=function_name_token.value,
        body=body_block,
        start_position=type_token.start_position,
    )


def parse_program(token_tape: TokenTape) -> SourceProgramNode:
    f = parse_function(token_tape)

    if token_tape.tokens_remaining > 0:
        raise ValueError("Did not expect any more tokens")

    return SourceProgramNode(start_position=0, value=f)
