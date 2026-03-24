import pytest

from nqcc.lexer import CloseParenToken, ConstantIntegerToken, KeywordToken, SemicolonToken
from nqcc.parser import (
    SourceAdd,
    SourceASTBadTypeError,
    SourceASTBadValueError,
    SourceBinaryExpressionNode,
    SourceBitwiseAnd,
    SourceBitwiseOr,
    SourceBitwiseXor,
    SourceComplement,
    SourceConstantIntNode,
    SourceDivide,
    SourceEqualTo,
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
    TokenTape,
    parse_expression,
    parse_function,
    parse_program,
    parse_statement,
)

_BINARY_EXPRESSION_MAP = {
    "+": SourceAdd,
    "-": SourceSubtract,
    "*": SourceMultiply,
    "/": SourceDivide,
    "%": SourceModulo,
    "&": SourceBitwiseAnd,
    "|": SourceBitwiseOr,
    "^": SourceBitwiseXor,
    "<<": SourceLeftShift,
    ">>": SourceRightShift,
    "&&": SourceLogicalAnd,
    "||": SourceLogicalOr,
    "==": SourceEqualTo,
    "!=": SourceNotEqualTo,
    "<": SourceLessThan,
    "<=": SourceLessThanOrEqual,
    ">": SourceGreaterThan,
    ">=": SourceGreaterThanOrEqual,
}


class TestSourceExpressionNode:
    def test_constant_integer(self):
        tokens = [
            ConstantIntegerToken(start_position=1, value="123"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceConstantIntNode)
        assert node.start_position == 1
        assert node.value == 123

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_complement_integer(self):
        source = " ~ 2 ;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 3

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceUnaryExpressionNode)
        assert node.start_position == 1
        assert node.operator == SourceComplement(start_position=1)
        assert node.expression == SourceConstantIntNode(start_position=3, value=2)

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_negate_integer(self):
        source = "  -3;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 3

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceUnaryExpressionNode)
        assert node.operator == SourceNegate(start_position=2)
        assert node.start_position == 2
        assert node.expression == SourceConstantIntNode(start_position=3, value=3)

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_logicalnot_integer(self):
        source = "  !3;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 3

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceUnaryExpressionNode)
        assert node.operator == SourceLogicalNot(start_position=2)
        assert node.start_position == 2
        assert node.expression == SourceConstantIntNode(start_position=3, value=3)

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_parens_integer(self):
        source = "(-((~12)));"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 10

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceUnaryExpressionNode)
        assert node.operator == SourceNegate(start_position=1)
        assert node.start_position == 1
        inner_exp = node.expression
        assert isinstance(inner_exp, SourceUnaryExpressionNode)
        assert inner_exp.operator == SourceComplement(start_position=4)
        assert inner_exp.start_position == 4
        assert inner_exp.expression == SourceConstantIntNode(start_position=5, value=12)

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    @pytest.mark.parametrize(
        "operator",
        [
            "+",
            "-",
            "*",
            "/",
            "%",
            "|",
            "&",
            "^",
            "<<",
            ">>",
            "&&",
            "||",
            "==",
            "!=",
            "<",
            "<=",
            ">",
            ">=",
        ],
    )
    def test_simple_binary(self, operator: str):
        source = f"14 {operator} 10;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 4

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceBinaryExpressionNode)
        assert node.operator == _BINARY_EXPRESSION_MAP[operator](start_position=3)

        assert node.left == SourceConstantIntNode(start_position=0, value=14)
        assert node.right == SourceConstantIntNode(start_position=4 + len(operator), value=10)

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_simple_binary_with_parens(self):
        source = "1 + (2 * 3);"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 8

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceBinaryExpressionNode)
        assert node.operator == SourceAdd(start_position=2)

        assert node.left == SourceConstantIntNode(start_position=0, value=1)

        r_exp = node.right
        assert isinstance(r_exp, SourceBinaryExpressionNode)
        assert r_exp.operator == SourceMultiply(start_position=7)
        assert r_exp.left == SourceConstantIntNode(start_position=5, value=2)
        assert r_exp.right == SourceConstantIntNode(start_position=9, value=3)

        # We are using the semi colon to mark the end of the expression
        assert token_tape.tokens_remaining == 1

    def test_simple_binary_precedence(self):
        # This should be the same AST as "1 + (2 * 3);""
        source = "1 + 2 * 3;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 6

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceBinaryExpressionNode)
        assert node.operator == SourceAdd(start_position=2)

        assert node.left == SourceConstantIntNode(start_position=0, value=1)

        r_exp = node.right
        assert isinstance(r_exp, SourceBinaryExpressionNode)
        assert r_exp.operator == SourceMultiply(start_position=6)
        assert r_exp.left == SourceConstantIntNode(start_position=4, value=2)
        assert r_exp.right == SourceConstantIntNode(start_position=8, value=3)

        # We are using the semi colon to mark the end of the expression
        assert token_tape.tokens_remaining == 1

    def test_simple_binary_req_parens(self):
        source = "(1+2)*3;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 8

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceBinaryExpressionNode)
        assert node.operator == SourceMultiply(start_position=5)

        assert isinstance(node.left, SourceBinaryExpressionNode)
        assert node.left.operator == SourceAdd(start_position=2)
        assert node.left.left == SourceConstantIntNode(start_position=1, value=1)
        assert node.left.right == SourceConstantIntNode(start_position=3, value=2)

        assert node.right == SourceConstantIntNode(start_position=6, value=3)

        # We are using the semi colon to mark the end of the expression
        assert token_tape.tokens_remaining == 1

    def test_simple_binary_with_negation(self):
        # This should be the same AST as "1 + ((-2) * 3);""
        source = "1 + -2 * 3;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 7

        node = parse_expression(token_tape, min_precedence=0)
        assert isinstance(node, SourceBinaryExpressionNode)
        assert node.operator == SourceAdd(start_position=2)

        assert node.left == SourceConstantIntNode(start_position=0, value=1)
        r_exp = node.right
        assert isinstance(r_exp, SourceBinaryExpressionNode)
        assert r_exp.operator == SourceMultiply(start_position=7)
        assert r_exp.left == SourceUnaryExpressionNode(
            start_position=4,
            operator=SourceNegate(start_position=4),
            expression=SourceConstantIntNode(start_position=5, value=2),
        )
        assert r_exp.right == SourceConstantIntNode(start_position=9, value=3)

        # We are using the semi colon to mark the end of the expression
        assert token_tape.tokens_remaining == 1

    @pytest.mark.parametrize(
        ["a_str", "b_str"],
        [
            ("1 + -2 ;", "1 +(-2);"),
            ("1+ 2*3 +4;", "1+(2*3)+4;"),
            (" ~1 -2;", "(~1)-2;"),
            ("1 + (4/5) ;", "1 +  4/5 ;"),
            ("1 + ((-4)/5) ;", "1 +   -4 /5  ;"),
            ("1 + (4%5) ;", "1 +  4%5 ;"),
            (" 1+2 +3;", "(1+2)+3;"),
            (" 1+2 -3;", "(1+2)-3;"),
            (" 1-2 +3;", "(1-2)+3;"),
            (" 1*2 /3;", "(1*2)/3;"),
            (" 1/2 *3;", "(1/2)*3;"),
            (" 1*2 %3;", "(1*2)%3;"),
            (" 1%2 *3;", "(1%2)*3;"),
            (" 1^ 2*3;", " 1^(2*3);"),
            (" 1& 2*3;", " 1&(2*3);"),
            (" 1| 2*3;", " 1|(2*3);"),
            (" 1| 2<<3;", " 1|(2<<3);"),
            (" 1| 2>>3;", " 1|(2>>3);"),
            (" 1|| 2==2;", " 1||(2==2);"),
        ],
    )
    def test_paired_expressions(self, a_str: str, b_str: str):
        tt_a = TokenTape.from_c_source(a_str)
        tt_b = TokenTape.from_c_source(b_str)

        a_node = parse_expression(tt_a, min_precedence=0)
        b_node = parse_expression(tt_b, min_precedence=0)

        print(f"{a_node.model_dump_json(indent=2)}")
        print(f"{b_node.model_dump_json(indent=2)}")

        assert a_node == b_node


class TestSourceStatementNode:
    def test_return_statement(self):
        tokens = [
            KeywordToken(start_position=0, value="return"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = parse_statement(token_tape)

        assert isinstance(node, SourceReturnNode)
        assert node.start_position == 0
        assert isinstance(node.value, SourceConstantIntNode)
        sen: SourceConstantIntNode = node.value
        assert sen.start_position == 1
        assert sen.value == 321

        assert token_tape.tokens_remaining == 0

    def test_return_serde(self):
        tokens = [
            KeywordToken(start_position=0, value="return"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = parse_statement(token_tape)

        node_str = node.model_dump_json()

        node_serde = SourceStatementNode.model_validate_json(node_str)

        assert node == node_serde

    def test_return_mispelled(self):
        tokens = [
            KeywordToken(start_position=0, value="returns"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        with pytest.raises(SourceASTBadValueError) as sabve:
            _ = parse_statement(token_tape)
        assert sabve.value.message == "Unexpected keyword"
        assert sabve.value.actual_token == tokens[0]

    def test_return_has_space(self):
        tokens = [
            KeywordToken(start_position=0, value="retur n"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        with pytest.raises(SourceASTBadValueError) as sabve:
            _ = parse_statement(token_tape)
        assert sabve.value.message == "Unexpected keyword"
        assert sabve.value.actual_token == tokens[0]


class TestSourceFunctionNode:
    def test_function(self):
        program_str = "int main( void ) { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        assert isinstance(node, SourceFunctionNode)
        assert node.start_position == program_str.find("int")
        assert node.identifier == "main"

        body_node = node.body
        assert isinstance(body_node, SourceReturnNode)
        assert body_node.start_position == program_str.find("return")

        return_value_node = body_node.value
        assert isinstance(return_value_node, SourceConstantIntNode)
        assert return_value_node.start_position == program_str.find("2")

    def test_serde(self):
        program_str = "int main( void ) { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        node_str = node.model_dump_json()

        node_serde = SourceFunctionNode.model_validate_json(node_str)
        assert node == node_serde

    def test_switched_parens(self):
        program_str = "int main) void ( { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        with pytest.raises(SourceASTBadTypeError) as sabte:
            _ = parse_function(token_tape)
        assert sabte.value.message == "Received token of unexpected type"
        assert sabte.value.actual_token == CloseParenToken(start_position=8, value=")")

    def test_missing_close_brace(self):
        program_str = "int main( void ) { return 2;"
        token_tape = TokenTape.from_c_source(program_str)

        with pytest.raises(IndexError, match="No tokens remaining in TokenTape"):
            _ = parse_function(token_tape)


class TestSourceProgramNode:
    def test_program(self):
        program_str = " int main( void ) { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_program(token_tape)

        assert isinstance(node, SourceProgramNode)
        assert node.start_position == 0

        func_node = node.value
        assert isinstance(func_node, SourceFunctionNode)

        assert func_node.identifier == "main"

        body_node = func_node.body
        assert isinstance(body_node, SourceReturnNode)
        assert body_node.start_position == program_str.find("return")

        return_value_node = body_node.value
        assert isinstance(return_value_node, SourceConstantIntNode)
        assert return_value_node.start_position == program_str.find("2")

    def test_program_serde(self):
        program_str = "   int main( void ) { return 6;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_program(token_tape)
        node_str = node.model_dump_json()

        node_serde = SourceProgramNode.model_validate_json(node_str)
        assert node == node_serde
