from nqcc.parser import TokenTape, parse_program
from nqcc.tacky import TackyGenerator
from nqcc.codegen import convert_tacky_program, AsmProgramNode

class TestAsmSerde:
    def test_simple(self):
        source = "   int main(void) {return ~(    509);}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        tg = TackyGenerator()
        tacky_program = tg.emit_program(src_node)

        asm_prog = convert_tacky_program(tacky_program)

        json_str = asm_prog.model_dump_json()
        restored = AsmProgramNode.model_validate_json(json_str)

        assert restored == asm_prog