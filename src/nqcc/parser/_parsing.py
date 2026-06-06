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
    ColonToken,
    CommaToken,
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
    QuestionMarkToken,
    RightShift,
    SemicolonToken,
    TildeToken,
    Token,
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
    SourceBlockNode,
    SourceBreakNode,
    SourceComplement,
    SourceCompoundNode,
    SourceConstantIntNode,
    SourceContinueNode,
    SourceDeclarationNode,
    SourceDivide,
    SourceDoWhileNode,
    SourceEqualTo,
    SourceExpressionNode,
    SourceExpressionStatementNode,
    SourceForInitNode,
    SourceForNode,
    SourceFunctionCallNode,
    SourceFunctionDeclarationNode,
    SourceGreaterThan,
    SourceGreaterThanOrEqual,
    SourceIfStatementNode,
    SourceInitDeclNode,
    SourceInitExpressionNode,
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
    SourceStorageType,
    SourceSubtract,
    SourceTernary,
    SourceTernaryExpressonNode,
    SourceUnaryExpressionNode,
    SourceUnaryOperator,
    SourceVariableDeclarationNode,
    SourceVarNode,
    SourceWhileNode,
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


def parse_function_argument_list(token_tape: TokenTape) -> list[SourceExpressionNode]:
    result = []
    _ = token_tape.expect(OpenParenToken)
    must_have_arg = False
    while not isinstance(token_tape.peek(), CloseParenToken) or must_have_arg:
        nxt_arg = parse_expression(token_tape, min_precedence=0)
        result.append(nxt_arg)
        if isinstance(token_tape.peek(), CloseParenToken):
            break
        _ = token_tape.expect(CommaToken)
        must_have_arg = True
    _ = token_tape.expect(CloseParenToken)

    return result


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
            nxt_token = token_tape.peek()
            if isinstance(nxt_token, OpenParenToken):
                # We have a function call
                args = parse_function_argument_list(token_tape)
                return SourceFunctionCallNode(
                    start_position=id_token.start_position, identifier=id_token.value, args=args
                )
            else:
                return SourceVarNode(
                    start_position=id_token.start_position, identifier=id_token.value
                )

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

            case QuestionMarkToken():
                middle = parse_expression(token_tape, min_precedence=0)
                _ = token_tape.expect(ColonToken)
                right = parse_expression(token_tape, min_precedence=operator.precedence)
                left = SourceTernaryExpressonNode(
                    start_position=lex_op.start_position,
                    condition=left,
                    then=middle,
                    otherwise=right,
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


def parse_optional_expression(
    token_tape: TokenTape, end_token: Type
) -> SourceExpressionNode | SourceVariableDeclarationNode | None:
    first_token = token_tape.peek()
    result: SourceExpressionNode | SourceVariableDeclarationNode
    if isinstance(first_token, end_token):
        _ = token_tape.expect(end_token)
        return None
    elif isinstance(first_token, KeywordToken):
        assert first_token.value == "int", f"Was expecting int counter: {first_token}"
        parsed_decl = parse_declaration(token_tape)
        assert not isinstance(parsed_decl, SourceFunctionDeclarationNode)
        # Decl will consume the ending token
        result = parsed_decl
    else:
        result = parse_expression(token_tape, min_precedence=0)
        _ = token_tape.expect(end_token)
    return result


def parse_while_statement(token_tape: TokenTape, start_position: int) -> SourceWhileNode:
    # while was already consumed
    _ = token_tape.expect(OpenParenToken)
    condition = parse_expression(token_tape, min_precedence=0)
    _ = token_tape.expect(CloseParenToken)
    body = parse_statement(token_tape)

    return SourceWhileNode(start_position=start_position, condition=condition, body=body)


def parse_dowhile_statement(token_tape: TokenTape, start_position: int) -> SourceDoWhileNode:
    # do was already consumed
    body = parse_statement(token_tape)
    while_token = token_tape.expect(KeywordToken)
    if while_token.value != "while":
        raise SourceASTBadValueError(
            expected_value="while", actual_token=while_token, message="Expected while for do"
        )
    _ = token_tape.expect(OpenParenToken)
    condition = parse_expression(token_tape, min_precedence=0)
    _ = token_tape.expect(CloseParenToken)
    _ = token_tape.expect(SemicolonToken)
    return SourceDoWhileNode(start_position=start_position, condition=condition, body=body)


def parse_for_statement(token_tape: TokenTape, start_position: int) -> SourceForNode:
    # for was already consumed
    _ = token_tape.expect(OpenParenToken)

    # Get the 'initial' expression
    initial = parse_optional_expression(token_tape, SemicolonToken)
    init_expr: SourceForInitNode
    if initial is None:
        init_expr = SourceInitExpressionNode(start_position=start_position, expression=None)
    elif isinstance(initial, SourceAssignmentNode):
        init_expr = SourceInitExpressionNode(
            start_position=initial.start_position, expression=initial
        )
    elif isinstance(initial, SourceVariableDeclarationNode):
        init_expr = SourceInitDeclNode(start_position=initial.start_position, decl=initial)
    else:
        raise ValueError("Bad init expression")

    # Get the 'condition' expression
    condition = parse_optional_expression(token_tape, SemicolonToken)
    assert not isinstance(condition, SourceVariableDeclarationNode), (
        "Can't declare in for condition"
    )

    # Get the 'post' expression
    post = parse_optional_expression(token_tape, CloseParenToken)
    assert not isinstance(post, SourceVariableDeclarationNode), "Can't declare in for post"

    body = parse_statement(token_tape)

    return SourceForNode(
        start_position=start_position, init=init_expr, condition=condition, post=post, body=body
    )


def parse_statement(token_tape: TokenTape) -> SourceStatementNode:  # noqa: C901
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
                case "break":
                    _ = token_tape.expect(SemicolonToken)
                    return SourceBreakNode(start_position=sp)
                case "continue":
                    _ = token_tape.expect(SemicolonToken)
                    return SourceContinueNode(start_position=sp)

                case "while":
                    # Note that we already consumed the 'while'
                    return parse_while_statement(token_tape, start_position=sp)

                case "do":
                    # We already consumed the 'do'
                    return parse_dowhile_statement(token_tape, start_position=sp)

                case "for":
                    # We already consumed the 'for'
                    return parse_for_statement(token_tape, start_position=sp)

                case _:
                    raise SourceASTBadValueError(
                        expected_value="keyword",
                        actual_token=first_token,
                        message="Unexpected keyword",
                    )
        case OpenBraceToken():
            # We have a compound statement
            block = parse_block(token_tape)
            return SourceCompoundNode(start_position=first_token.start_position, block=block)

        case _:
            expr = parse_expression(token_tape, min_precedence=0)
            _ = token_tape.expect(SemicolonToken)
            return SourceExpressionStatementNode(start_position=expr.start_position, value=expr)


def parse_block(token_tape: TokenTape) -> SourceBlockNode:
    opening_token = token_tape.expect(OpenBraceToken)
    items: list[SourceBlockItemNode] = []
    while not isinstance(token_tape.peek(), CloseBraceToken):
        nxt = parse_block_item(token_tape)
        items.append(nxt)
    _ = token_tape.expect(CloseBraceToken)
    return SourceBlockNode(start_position=opening_token.start_position, items=items)


def parse_type_and_storage_class(token_tape: TokenTape) -> tuple[str, SourceStorageType | None]:
    parsed_types = []
    parsed_storage_classes = []

    # Work through until we get to the identifier
    while not isinstance(token_tape.peek(), IdentifierToken):
        nxt_token = token_tape.expect(KeywordToken)

        if nxt_token.value == "int":
            parsed_types.append(nxt_token.value)
        elif nxt_token.value in ["extern", "static"]:
            parsed_storage_classes.append(nxt_token.value)
        else:
            raise ValueError(f"Unexpected: {nxt_token}")

    if len(parsed_types) != 1:
        raise ValueError(f"Bad types: {parsed_types}")
    if len(parsed_storage_classes) > 1:
        raise ValueError(f"Bad storage classes: {parsed_storage_classes}")

    final_type = parsed_types[0]
    final_storage: SourceStorageType | None = None
    if len(parsed_storage_classes) == 1:
        match parsed_storage_classes[0]:
            case "static":
                final_storage = SourceStorageType(storage_type="Static")
            case "extern":
                final_storage = SourceStorageType(storage_type="Extern")

    return final_type, final_storage


def parse_declaration(token_tape: TokenTape) -> SourceDeclarationNode:
    decl_start_token = token_tape.peek()
    _, decl_storage = parse_type_and_storage_class(token_tape)

    name_token = token_tape.expect(IdentifierToken)
    assert isinstance(name_token, IdentifierToken), "Expected identifier!"

    result: SourceDeclarationNode
    if isinstance(token_tape.peek(), OpenParenToken):
        # We have a function declaration
        params = parse_function_parameter_list(token_tape)

        if isinstance(token_tape.peek(), OpenBraceToken):
            body_block = parse_block(token_tape)
        else:
            token_tape.expect(SemicolonToken)
            body_block = None

        result = SourceFunctionDeclarationNode(
            start_position=decl_start_token.start_position,
            identifier=name_token.value,
            params=params,
            body=body_block,
            storage_class=decl_storage,
        )
    else:
        # We have a variable declaration
        var = SourceVarNode(start_position=name_token.start_position, identifier=name_token.value)

        initialiser: SourceExpressionNode | None = None
        if not isinstance(token_tape.peek(), SemicolonToken):
            _ = token_tape.expect(AssignmentToken)
            initialiser = parse_expression(token_tape, min_precedence=0)
        _ = token_tape.expect(SemicolonToken)

        result = SourceVariableDeclarationNode(
            start_position=decl_start_token.start_position,
            identifier=var,
            initial=initialiser,
            storage_class=decl_storage,
        )

    return result


def parse_block_item(token_tape: TokenTape) -> SourceBlockItemNode:
    peeked = token_tape.peek()

    # Only support 'int' declarations right now
    if isinstance(peeked, KeywordToken) and peeked.value in ["int", "extern", "static"]:
        return parse_declaration(token_tape)

    return parse_statement(token_tape)


def parse_function_parameter_list(token_tape: TokenTape) -> list[str]:
    result = []
    _ = token_tape.expect(OpenParenToken)

    first_arg_token = token_tape.peek()
    if not isinstance(first_arg_token, KeywordToken) or first_arg_token.value not in [
        "void",
        "int",
    ]:
        raise SourceASTBadValueError(
            expected_value="void or int",
            actual_token=first_arg_token,
            message="Unexpected arguments",
        )

    if first_arg_token.value == "void":
        # Just consume the keyword
        _ = token_tape.expect(KeywordToken)
    else:
        while True:
            type_token = token_tape.expect(KeywordToken)
            assert type_token.value == "int"
            name_token = token_tape.expect(IdentifierToken)
            result.append(name_token.value)
            if isinstance(token_tape.peek(), CloseParenToken):
                break
            _ = token_tape.expect(CommaToken)

    _ = token_tape.expect(CloseParenToken)
    return result


def parse_function(token_tape: TokenTape) -> SourceFunctionDeclarationNode:
    decl = parse_declaration(token_tape)
    assert isinstance(decl, SourceFunctionDeclarationNode)
    return decl


def parse_program(token_tape: TokenTape) -> SourceProgramNode:
    decls = []
    while token_tape.tokens_remaining > 0:
        nxt_decl = parse_declaration(token_tape)
        decls.append(nxt_decl)

    return SourceProgramNode(start_position=0, declarations=decls)
