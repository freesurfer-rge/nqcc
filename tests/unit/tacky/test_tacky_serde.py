from nqcc.parser import TokenTape, parse_program
from nqcc.tacky import TackyGenerator, TackyProgramNode


class TestTackySerde:
    def _round_trip(self, source: str) -> None:
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        target = TackyGenerator()
        orig = target.emit_program(src_node)

        json_str = orig.model_dump_json()

        restored = TackyProgramNode.model_validate_json(json_str)

        assert restored == orig

    def test_simple(self):
        source = " int main(void) {return -  (  ~(566));}"
        self._round_trip(source)

    def test_binary(self):
        source = "int main  (void ) { return 3- -5 * ~9 % 8 ^ 11 >> 12 | 13 & 1 << 2;}"
        self._round_trip(source)

    def test_logical_and(self):
        source = "int main (void) { return (1-3) && (3-2); }"
        self._round_trip(source)

    def test_logical_or(self):
        source = "int main (void) { return (1-3) || (3-2); }"
        self._round_trip(source)

    def test_conditionals(self):
        source = """
int main( void ) {
    int a;
    int b = 1;
    a = b * 2;
    if( a<2 )
      b = a ? b+1 : 5;
    else
      a = 6;
    return a + b;
}
"""
        self._round_trip(source)