import pathlib
import tempfile

from nqcc.codegen import (
    AsmProgramNode,
    PseudoRegisterReplacer,
    convert_tacky_program,
    fixup_program_instructions,
)
from nqcc.parser import TokenTape, parse_program
from nqcc.semantic_analysis import semantic_analysis_driver
from nqcc.tacky import TackyGenerator


class TestAsmSerde:
    def _round_trip(self, asm_ast: AsmProgramNode) -> None:
        json_str = asm_ast.model_dump_json()
        restored = AsmProgramNode.model_validate_json(json_str)
        assert asm_ast == restored

    def _check_from_source(self, source: str) -> None:

        with tempfile.TemporaryDirectory() as working_dir:
            token_tape = TokenTape.from_c_source(source)
            src_node = parse_program(token_tape)

            src_node, symbol_table = semantic_analysis_driver(
                src_node, working_dir=pathlib.Path(working_dir)
            )

            tg = TackyGenerator()
            tacky_program = tg.emit_program(src_node, symbol_table)
            asm_prog = convert_tacky_program(tacky_program)

            self._round_trip(asm_prog)

            prr = PseudoRegisterReplacer(symbol_table)
            prr.pseudo_replace(asm_prog)
            self._round_trip(asm_prog)

            fixup_program_instructions(asm_prog)
            self._round_trip(asm_prog)

    def test_simple(self):
        source = "   int main(void) {return ~(    509);}"
        self._check_from_source(source)

    def test_binary_ops(self):
        source = "  int main( void ) {return ~1 + 3 - 8/4;}"
        self._check_from_source(source)

    def test_simple_call(self):
        source = """
        int get_val(void) { return 2;}

        int main(void) { return get_val(); }
        """
        self._check_from_source(source)

    def test_nested_call(self):
        source = """
        int inc_val(int v) { return v+1; }

        int main(void) { int a = 10; return inc_val(inc_val(a)); }
        """
        self._check_from_source(source)

    def test_simple_statics(self):
        source = """
        static int a = 0;

        static int my_func(void) { a = a+ 1;}

        int main( void ) { my_func(); return a;}
        """
        self._check_from_source(source)
