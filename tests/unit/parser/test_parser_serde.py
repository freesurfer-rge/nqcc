from nqcc.parser import SourceProgramNode, TokenTape, parse_program


def _check_round_trip(c_source: str):
    token_tape = TokenTape.from_c_source(c_source)
    src_node = parse_program(token_tape)

    json_str = src_node.model_dump_json()

    restored = SourceProgramNode.model_validate_json(json_str)

    assert restored == src_node


class TestParserSerde:
    def test_simple(self):
        source = " int main(void) {return - (~   566);}"
        _check_round_trip(source)

    def test_arithmetic(self):
        source = """ int main(void) {
        return - (~   1+491*5-(-2)%8);
        }
        """
        _check_round_trip(source)

    def test_comparisons(self):
        source = """ int main(void) {
        return ! 3 && 2 || 1 < 4 > 1 == 5 != 3 <= 4 >= 10;
        }
        """
        _check_round_trip(source)

    def test_multiple_statements(self):
        source = """int main( void ) {
            int a;
            ;
            int b = 1;
            a = b+1;
            a = 3 * (b = a);
            return a << b;
        }
        """
        _check_round_trip(source)

    def test_if_statement(self):
        source = """int main( void ) {
            int a;
            ;
            int b = 1;
            if( a>=1 )
            a = b+1;
            else
            a = 3 * (b = a);
            return a << b;
        }
        """
        _check_round_trip(source)

    def test_ternary_statement(self):
        source = """int main( void ) {
            int a;
            int b = 1;
            b ? a=0 : a=12;
            return a << b;
        }
        """
        _check_round_trip(source)
