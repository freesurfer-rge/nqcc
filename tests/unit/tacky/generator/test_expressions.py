from typing import Type

import pytest

from nqcc.parser import TokenTape, parse_expression
from nqcc.tacky import (
    TackyAdd,
    TackyBinaryNode,
    TackyBinaryOperator,
    TackyBitwiseAnd,
    TackyBitwiseOr,
    TackyBitwiseXor,
    TackyComplement,
    TackyConstantIntNode,
    TackyCopyNode,
    TackyDivide,
    TackyEqualTo,
    TackyGenerator,
    TackyGreaterThan,
    TackyGreaterThanOrEqual,
    TackyJumpIfNotZeroNode,
    TackyJumpIfZeroNode,
    TackyJumpNode,
    TackyLabelNode,
    TackyLeftShift,
    TackyLessThan,
    TackyLessThanOrEqual,
    TackyLogicalNot,
    TackyModulo,
    TackyMultiply,
    TackyNegate,
    TackyNotEqualTo,
    TackyRightShift,
    TackySubtract,
    TackyUnaryNode,
    TackyVarNode,
)

_BINARY_EXPRESSION_MAP: dict[str, Type[TackyBinaryOperator]] = {
    "+": TackyAdd,
    "-": TackySubtract,
    "*": TackyMultiply,
    "/": TackyDivide,
    "%": TackyModulo,
    "&": TackyBitwiseAnd,
    "|": TackyBitwiseOr,
    "^": TackyBitwiseXor,
    "<<": TackyLeftShift,
    ">>": TackyRightShift,
    "==": TackyEqualTo,
    "!=": TackyNotEqualTo,
    "<": TackyLessThan,
    "<=": TackyLessThanOrEqual,
    ">": TackyGreaterThan,
    ">=": TackyGreaterThanOrEqual,
}


# These tests access internals of the TackyGenerator


class TestExpressions:
    def test_constant(self):
        source = "  3;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_constant"

        result = target.emit_expression(src_node)
        assert target._nxt_tmp == 0, "Should not advance nxt_tmp counter"
        assert len(target._current_instructions) == 0, "Should not emit instructions"
        assert isinstance(result, TackyConstantIntNode)
        assert result.value == 3
        assert result.start_position == 2

    def test_negation(self):
        source = "-4;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_negation"

        result = target.emit_expression(src_node)
        assert target._nxt_tmp == 1, "Should have a temporary for result"
        assert len(target._current_instructions) == 1, "Should emit negation instructions"
        instr = target._current_instructions[0]
        assert isinstance(instr, TackyUnaryNode)
        assert instr.start_position == 0
        assert instr.src == TackyConstantIntNode(start_position=1, value=4)
        assert instr.dst == TackyVarNode(start_position=0, identifier="tmp.test_negation.0")
        assert instr.operator == TackyNegate(start_position=0)
        assert result == instr.dst

    def test_complement(self):
        source = "~ 10;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_complement"

        result = target.emit_expression(src_node)
        assert target._nxt_tmp == 1, "Should have a temporary for result"
        assert len(target._current_instructions) == 1, "Should emit complement instruction"
        instr = target._current_instructions[0]
        assert isinstance(instr, TackyUnaryNode)
        assert instr.start_position == 0
        assert instr.src == TackyConstantIntNode(start_position=2, value=10)
        assert instr.dst == TackyVarNode(start_position=0, identifier="tmp.test_complement.0")
        assert instr.operator == TackyComplement(start_position=0)
        assert result == instr.dst

    def test_logical_not(self):
        source = "!4;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_logical_not"

        result = target.emit_expression(src_node)
        assert target._nxt_tmp == 1, "Should have a temporary for result"
        assert len(target._current_instructions) == 1
        instr = target._current_instructions[0]
        assert isinstance(instr, TackyUnaryNode)
        assert instr.start_position == 0
        assert instr.src == TackyConstantIntNode(start_position=1, value=4)
        assert instr.dst == TackyVarNode(start_position=0, identifier="tmp.test_logical_not.0")
        assert instr.operator == TackyLogicalNot(start_position=0)
        assert result == instr.dst

    def test_simple_nested(self):
        source = "(-((~12)));"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_simple_nested"

        result = target.emit_expression(src_node)
        assert target._nxt_tmp == 2, "Needs two temporaries"
        assert len(target._current_instructions) == 2, "Should emit two instructions"
        instr0 = target._current_instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=4,
            operator=TackyComplement(start_position=4),
            src=TackyConstantIntNode(start_position=5, value=12),
            dst=TackyVarNode(start_position=4, identifier="tmp.test_simple_nested.0"),
        )
        instr1 = target._current_instructions[1]
        assert instr1 == TackyUnaryNode(
            start_position=1,
            operator=TackyNegate(start_position=1),
            src=instr0.dst,
            dst=TackyVarNode(start_position=1, identifier="tmp.test_simple_nested.1"),
        )
        assert result == instr1.dst

    @pytest.mark.parametrize(
        "operator",
        ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>", "==", "!=", "<", "<=", ">", ">="],
    )
    def test_simple_binary(self, operator: str):
        source = f"14 {operator} 10;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 4
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_simple_binary"

        result = target.emit_expression(src_node)
        assert result == TackyVarNode(start_position=3, identifier="tmp.test_simple_binary.0")

        assert len(target._current_instructions) == 1
        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyBinaryNode)
        assert instr0.start_position == 3
        assert instr0.operator == _BINARY_EXPRESSION_MAP[operator](start_position=3)
        assert instr0.left == TackyConstantIntNode(start_position=0, value=14)
        assert instr0.right == TackyConstantIntNode(start_position=4 + len(operator), value=10)
        assert instr0.dst == result

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_logical_and(self):
        source = "(1+2) && (3+4);"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 12
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_logical_and"

        result = target.emit_expression(src_node)
        assert result == TackyVarNode(start_position=6, identifier="tmp.test_logical_and.0")

        assert len(target._current_instructions) == 9

        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyBinaryNode)
        assert instr0 == TackyBinaryNode(
            start_position=2,
            operator=TackyAdd(start_position=2),
            left=TackyConstantIntNode(start_position=1, value=1),
            right=TackyConstantIntNode(start_position=3, value=2),
            dst=TackyVarNode(start_position=2, identifier="tmp.test_logical_and.1"),
        )

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyJumpIfZeroNode)
        assert instr1 == TackyJumpIfZeroNode(
            start_position=6,
            target="label.test_logical_and.logicalandfalse.0",
            condition=instr0.dst,
        )

        instr2 = target._current_instructions[2]
        assert isinstance(instr2, TackyBinaryNode)
        assert instr2 == TackyBinaryNode(
            start_position=11,
            operator=TackyAdd(start_position=11),
            left=TackyConstantIntNode(start_position=10, value=3),
            right=TackyConstantIntNode(start_position=12, value=4),
            dst=TackyVarNode(start_position=11, identifier="tmp.test_logical_and.2"),
        )

        instr3 = target._current_instructions[3]
        assert isinstance(instr3, TackyJumpIfZeroNode)
        assert instr3 == TackyJumpIfZeroNode(
            start_position=6,
            target="label.test_logical_and.logicalandfalse.0",
            condition=instr2.dst,
        )

        instr4 = target._current_instructions[4]
        assert isinstance(instr4, TackyCopyNode)
        assert instr4 == TackyCopyNode(
            start_position=6, src=TackyConstantIntNode(start_position=6, value=1), dst=result
        )

        instr5 = target._current_instructions[5]
        assert isinstance(instr5, TackyJumpNode)
        assert instr5 == TackyJumpNode(
            start_position=6, target="label.test_logical_and.logicalandend.1"
        )

        instr6 = target._current_instructions[6]
        assert isinstance(instr6, TackyLabelNode)
        assert instr6 == TackyLabelNode(
            start_position=6, identifier="label.test_logical_and.logicalandfalse.0"
        )

        instr7 = target._current_instructions[7]
        assert isinstance(instr4, TackyCopyNode)
        assert instr7 == TackyCopyNode(
            start_position=6, src=TackyConstantIntNode(start_position=6, value=0), dst=result
        )

        instr8 = target._current_instructions[8]
        assert isinstance(instr8, TackyLabelNode)
        assert instr8 == TackyLabelNode(
            start_position=6, identifier="label.test_logical_and.logicalandend.1"
        )

        # And the semi colon should remain
        assert token_tape.tokens_remaining == 1

    def test_logical_or(self):
        source = "(9+8) || (7+6);"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 12
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_logical_or"

        result = target.emit_expression(src_node)
        assert result == TackyVarNode(start_position=6, identifier="tmp.test_logical_or.0")

        assert len(target._current_instructions) == 9

        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyBinaryNode)
        assert instr0 == TackyBinaryNode(
            start_position=2,
            operator=TackyAdd(start_position=2),
            left=TackyConstantIntNode(start_position=1, value=9),
            right=TackyConstantIntNode(start_position=3, value=8),
            dst=TackyVarNode(start_position=2, identifier="tmp.test_logical_or.1"),
        )

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyJumpIfNotZeroNode)
        assert instr1 == TackyJumpIfNotZeroNode(
            start_position=6,
            target="label.test_logical_or.logicalortrue.0",
            condition=instr0.dst,
        )

        instr2 = target._current_instructions[2]
        assert isinstance(instr2, TackyBinaryNode)
        assert instr2 == TackyBinaryNode(
            start_position=11,
            operator=TackyAdd(start_position=11),
            left=TackyConstantIntNode(start_position=10, value=7),
            right=TackyConstantIntNode(start_position=12, value=6),
            dst=TackyVarNode(start_position=11, identifier="tmp.test_logical_or.2"),
        )

        instr3 = target._current_instructions[3]
        assert isinstance(instr3, TackyJumpIfNotZeroNode)
        assert instr3 == TackyJumpIfNotZeroNode(
            start_position=6,
            target="label.test_logical_or.logicalortrue.0",
            condition=instr2.dst,
        )

        instr4 = target._current_instructions[4]
        assert isinstance(instr4, TackyCopyNode)
        assert instr4 == TackyCopyNode(
            start_position=6, src=TackyConstantIntNode(start_position=6, value=0), dst=result
        )

        instr5 = target._current_instructions[5]
        assert isinstance(instr5, TackyJumpNode)
        assert instr5 == TackyJumpNode(
            start_position=6, target="label.test_logical_or.logicalorend.1"
        )

        instr6 = target._current_instructions[6]
        assert isinstance(instr6, TackyLabelNode)
        assert instr6 == TackyLabelNode(
            start_position=6, identifier="label.test_logical_or.logicalortrue.0"
        )

        instr7 = target._current_instructions[7]
        assert isinstance(instr4, TackyCopyNode)
        assert instr7 == TackyCopyNode(
            start_position=6, src=TackyConstantIntNode(start_position=6, value=1), dst=result
        )

        instr8 = target._current_instructions[8]
        assert isinstance(instr8, TackyLabelNode)
        assert instr8 == TackyLabelNode(
            start_position=6, identifier="label.test_logical_or.logicalorend.1"
        )

        # And the semi colon should remain
        assert token_tape.tokens_remaining == 1

    def test_ternary(self):
        source = "a?1:2;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 6
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_ternary"

        result = target.emit_expression(src_node)
        assert result == TackyVarNode(start_position=1, identifier="tmp.test_ternary.0")

        assert len(target._current_instructions) == 6

        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyJumpIfZeroNode)
        assert instr0.condition == TackyVarNode(start_position=0, identifier="a")
        assert instr0.target == "label.test_ternary.ternaryotherwise.0"

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyCopyNode)
        assert instr1.dst == TackyVarNode(start_position=1, identifier="tmp.test_ternary.0")
        assert instr1.src == TackyConstantIntNode(start_position=2, value=1)

        instr2 = target._current_instructions[2]
        assert isinstance(instr2, TackyJumpNode)
        assert instr2.target == "label.test_ternary.ternaryend.1"

        instr3 = target._current_instructions[3]
        assert isinstance(instr3, TackyLabelNode)
        assert instr3.identifier == "label.test_ternary.ternaryotherwise.0"

        instr4 = target._current_instructions[4]
        assert isinstance(instr4, TackyCopyNode)
        assert instr4.dst == TackyVarNode(start_position=1, identifier="tmp.test_ternary.0")
        assert instr4.src == TackyConstantIntNode(start_position=4, value=2)

        instr5 = target._current_instructions[5]
        assert isinstance(instr5, TackyLabelNode)
        assert instr5.identifier == "label.test_ternary.ternaryend.1"

        # Should not consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_multiple_binary(self):
        source = "1 + 2 * 3;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 6
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_multiple_binary"

        result = target.emit_expression(src_node)
        assert result == TackyVarNode(start_position=2, identifier="tmp.test_multiple_binary.1")

        assert len(target._current_instructions) == 2
        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyBinaryNode)
        assert instr0.operator == TackyMultiply(start_position=6)
        assert instr0.left == TackyConstantIntNode(start_position=4, value=2)
        assert instr0.right == TackyConstantIntNode(start_position=8, value=3)
        assert instr0.dst == TackyVarNode(start_position=6, identifier="tmp.test_multiple_binary.0")

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyBinaryNode)
        assert instr1.operator == TackyAdd(start_position=2)
        assert instr1.left == TackyConstantIntNode(start_position=0, value=1)
        assert instr1.right == instr0.dst
        assert instr1.dst == result

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    @pytest.mark.parametrize(
        "operator",
        ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>", "==", "!=", "<", "<=", ">", ">="],
    )
    def test_nested_binary(self, operator: str):
        source = f"(!1) {operator} (~4);"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 10
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_nested_binary"

        result = target.emit_expression(src_node)
        assert result == TackyVarNode(start_position=5, identifier="tmp.test_nested_binary.2")

        assert len(target._current_instructions) == 3

        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyUnaryNode)
        assert instr0.start_position == 1
        assert instr0.operator == TackyLogicalNot(start_position=1)
        assert instr0.src == TackyConstantIntNode(start_position=2, value=1)
        assert instr0.dst == TackyVarNode(start_position=1, identifier="tmp.test_nested_binary.0")

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyUnaryNode)
        assert instr1.start_position == 7 + len(operator)
        assert instr1.operator == TackyComplement(start_position=7 + len(operator))
        assert instr1.src == TackyConstantIntNode(start_position=8 + len(operator), value=4)
        assert instr1.dst == TackyVarNode(
            start_position=7 + len(operator), identifier="tmp.test_nested_binary.1"
        )

        instr2 = target._current_instructions[2]
        assert isinstance(instr2, TackyBinaryNode)
        assert instr2.start_position == 5
        assert instr2.operator == _BINARY_EXPRESSION_MAP[operator](start_position=5)
        assert instr2.left == instr0.dst
        assert instr2.right == instr1.dst
        assert instr2.dst == result

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_assignment(self):
        source = "a = 1;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 4
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_assignment"

        # We will skip semantic analysis for these fragments
        result = target.emit_expression(src_node)
        assert result == TackyVarNode(start_position=0, identifier="a")

        assert len(target._current_instructions) == 1
        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyCopyNode)
        assert instr0.dst == result
        assert instr0.src == TackyConstantIntNode(start_position=4, value=1)
