from nqcc.parser import TokenTape, parse_program
from nqcc.tacky import TackyGenerator, TackyProgramNode


class TestTackySerde:
    def test_simple(self):
        source = " int main(void) {return -  (  ~(566));}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        target = TackyGenerator()
        orig = target.emit_program(src_node)

        json_str = orig.model_dump_json()

        restored = TackyProgramNode.model_validate_json(json_str)

        assert restored == orig
