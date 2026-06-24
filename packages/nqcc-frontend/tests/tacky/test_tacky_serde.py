from nqcc.frontend import FrontEnd
from nqcc.frontend.tacky import TackyProgramNode


class TestTackySerde:
    def _round_trip(self, source: str) -> None:

        fe = FrontEnd(source, working_dir=None)
        fe.run_lexer()
        fe.run_parser()
        fe.run_semantic_analysis()
        fe.run_tacky_generation()

        json_str = fe.tacky.model_dump_json()

        restored = TackyProgramNode.model_validate_json(json_str)

        assert restored == fe.tacky

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

    def test_loops(self):
        source = """
        int main( void ) {
            int counter;

            for( int a=0; a<10; a=a+1){
                int b = 0;
                while( b< 10) {
                    if( a == 6 ) continue;
                    b = b + 1;
                    if( a>8) break;

                    do {
                        counter = counter + 1;
                    } while( b<2);
                }
            }
        }
        """
        self._round_trip(source)

    def test_statics(self):
        source = """
        static int plus_one(int a) {
            static int call_count = 0;
            call_count = call_count + 1;
            return a+1;
        }

        int main(void) {
            int b = 0;
            int c = plus_one(b);
            return c;
        }
        """

        self._round_trip(source)
