import pytest

from nqcc.parser import TokenTape, parse_expression, parse_function, parse_program, parse_statement
from nqcc.tacky import (
    TackyComplementNode,
    TackyConstantIntNode,
    TackyFunctionNode,
    TackyGenerator,
    TackyNegateNode,
    TackyProgramNode,
    TackyReturnNode,
    TackyUnaryNode,
    TackyVarNode,
    TackyAdd, TackySubtract, TackyMultiply, TackyDivide, TackyModulo, TackyBinaryNode
)

# These tests access internals of the TackyGenerator

_BINARY_EXPRESSION_MAP = {
    "+": TackyAdd,
    "-": TackySubtract,
    "*": TackyMultiply,
    "/": TackyDivide,
    "%": TackyModulo,
}

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
        assert instr.operator == TackyNegateNode(start_position=0)
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
        assert instr.operator == TackyComplementNode(start_position=0)
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
            operator=TackyComplementNode(start_position=4),
            src=TackyConstantIntNode(start_position=5, value=12),
            dst=TackyVarNode(start_position=4, identifier="tmp.test_simple_nested.0"),
        )
        instr1 = target._current_instructions[1]
        assert instr1 == TackyUnaryNode(
            start_position=1,
            operator=TackyNegateNode(start_position=1),
            src=instr0.dst,
            dst=TackyVarNode(start_position=1, identifier="tmp.test_simple_nested.1"),
        )
        assert result == instr1.dst
    
    @pytest.mark.parametrize("operator", ["+", "-", "*", "/", "%"])
    def test_simple_binary(self, operator: str):
        source = f"14 {operator} 10;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 4
        src_node = parse_expression(token_tape, min_precedence=0)

        target = TackyGenerator()
        target._curr_function = "test_simple_binary"

        result = target.emit_expression(src_node)
        assert result == TackyVarNode(start_position = 3, identifier="tmp.test_simple_binary.0")

        assert len(target._current_instructions) == 1
        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyBinaryNode)
        assert instr0.start_position == 3
        assert isinstance(instr0.operator, _BINARY_EXPRESSION_MAP[operator])
        assert instr0.left == TackyConstantIntNode(start_position=0, value=14)
        assert instr0.right == TackyConstantIntNode(start_position=5, value=10)

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1


class TestStatements:
    def test_return(self):
        source = "return ~ 162;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_statement(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_return"

        target.emit_statement(src_node)
        assert target._nxt_tmp == 1, "Expected one temporary used"
        assert len(target._current_instructions) == 2, "Expected two instructions"

        instr0 = target._current_instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=7,
            operator=TackyComplementNode(start_position=7),
            src=TackyConstantIntNode(start_position=9, value=162),
            dst=TackyVarNode(start_position=7, identifier="tmp.test_return.0"),
        )
        instr1 = target._current_instructions[1]
        assert instr1 == TackyReturnNode(start_position=0, value=instr0.dst)


class TestFunctions:
    def test_simple(self):
        source = "int main(void) {return -    508;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)

        target = TackyGenerator()

        result = target.emit_function(src_node)
        assert isinstance(result, TackyFunctionNode)
        assert result.identifier == "main"
        assert len(result.instructions) == 2

        instr0 = result.instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=23,
            operator=TackyNegateNode(start_position=23),
            src=TackyConstantIntNode(start_position=28, value=508),
            dst=TackyVarNode(start_position=23, identifier="tmp.main.0"),
        )

        instr1 = result.instructions[1]
        assert instr1 == TackyReturnNode(start_position=16, value=instr0.dst)


class TestPrograms:
    def test_simple(self):
        source = " int main(void) {return -    566;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        target = TackyGenerator()

        result = target.emit_program(src_node)
        assert isinstance(result, TackyProgramNode)
        assert result.start_position == 0

        main_func = result.function_definition
        assert isinstance(main_func, TackyFunctionNode)
        assert main_func.identifier == "main"
        assert main_func.start_position == 1
        assert len(main_func.instructions) == 2

        instr0 = main_func.instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=24,
            operator=TackyNegateNode(start_position=24),
            src=TackyConstantIntNode(start_position=29, value=566),
            dst=TackyVarNode(start_position=24, identifier="tmp.main.0"),
        )

        instr1 = main_func.instructions[1]
        assert instr1 == TackyReturnNode(start_position=17, value=instr0.dst)
