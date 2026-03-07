from nqcc.parser import TokenTape, parse_expression
from nqcc.tacky import TackyGenerator, TackyConstantIntNode

# These tests access internals of the TackyGenerator

class TestExpressions:
    def test_constant(self):
        source = "  3;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_expression(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_constant"

        result = target.emit_expression(src_node)
        assert target._nxt_tmp == 0, "Should not advance nxt_tmp counter"
        assert len(target._current_instructions) == 0, "Should not emit instructions"
        assert isinstance(result, TackyConstantIntNode)
        assert result.value == 3
        assert result.start_position == 2

    def test_negation(self):
        source = "-4";
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_expression(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_negation"

        result = target.emit_expression(src_node)
        assert target._nxt_tmp == 1, "Should have a temporary for result"
        assert len(target._current_instructions) == 1, "Should emit negation instructions"
        instr = target._current_instructions[0]