from nqcc.parser import TokenTape, parse_function, parse_program, parse_statement, parse_block
from nqcc.tacky import (
    TackyBinaryNode,
    TackyComplement,
    TackyConstantIntNode,
    TackyFunctionNode,
    TackyGenerator,
    TackyNegate,
    TackyProgramNode,
    TackyReturnNode,
    TackySubtract,
    TackyUnaryNode,
    TackyVarNode,
)

# These tests access internals of the TackyGenerator


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
            operator=TackyComplement(start_position=7),
            src=TackyConstantIntNode(start_position=9, value=162),
            dst=TackyVarNode(start_position=7, identifier="tmp.test_return.0"),
        )
        instr1 = target._current_instructions[1]
        assert instr1 == TackyReturnNode(start_position=0, value=instr0.dst)

    def test_return_longer(self):
        # Note the space, to avoid parsing as decrement operator
        source = "return 2- -1;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_statement(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_return_longer"

        target.emit_statement(src_node)
        assert target._nxt_tmp == 2
        assert len(target._current_instructions) == 3

        instr0 = target._current_instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=10,
            operator=TackyNegate(start_position=10),
            src=TackyConstantIntNode(start_position=11, value=1),
            dst=TackyVarNode(start_position=10, identifier="tmp.test_return_longer.0"),
        )

        instr1 = target._current_instructions[1]
        assert instr1 == TackyBinaryNode(
            start_position=8,
            operator=TackySubtract(start_position=8),
            left=TackyConstantIntNode(start_position=7, value=2),
            right=instr0.dst,
            dst=TackyVarNode(start_position=8, identifier="tmp.test_return_longer.1"),
        )

        instr2 = target._current_instructions[2]
        assert instr2 == TackyReturnNode(start_position=0, value=instr1.dst)

class TestBlockItems:

    def test_declaration(self):
        source = "int a;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_block(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_declaration"

        # Skip semantic analysis for now
        target.emit_blockitem(src_node)

        # Nothing generated for a plain declaration
        assert len(target._current_instructions) == 0


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
            operator=TackyNegate(start_position=23),
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
            operator=TackyNegate(start_position=24),
            src=TackyConstantIntNode(start_position=29, value=566),
            dst=TackyVarNode(start_position=24, identifier="tmp.main.0"),
        )

        instr1 = main_func.instructions[1]
        assert instr1 == TackyReturnNode(start_position=17, value=instr0.dst)
