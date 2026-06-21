from nqcc.frontend.parser import SourceProgramNode, TokenTape, parse_program
from nqcc.frontend import FrontEnd


def _check_round_trip(c_source: str):
    fe = FrontEnd(c_source, working_dir=None)
    fe.run_lexer()
    fe.run_parser()

    json_str = fe.source_ast.model_dump_json()

    restored = SourceProgramNode.model_validate_json(json_str)

    assert restored == fe.source_ast


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

    def test_for_loop(self):
        source = """
        int main( void ) {
            int a = 10;
            for( int i=0; i<2*5; i=i+2) {
                a = a * i;
            }
            return a;
        }
        """
        _check_round_trip(source)

    def test_static_variables(self):
        source = """
        int main(void) {
            static int i = 2;
            return i;
        }
        """
        _check_round_trip(source)
