from nqcc.semantic_analysis import (
    SymbolTable,
    resolve_program,
    label_loops_program,
    FunctionType,
    VariableType,
    VariableInt,
)


from nqcc.parser import TokenTape, parse_program, SourceProgramNode


def prepare_program(c_str: str) -> SourceProgramNode:
    token_tape = TokenTape.from_c_source(c_str)

    program = parse_program(token_tape)

    resolved = resolve_program(program)

    # Recall that label_loops_program is in-place
    label_loops_program(resolved)

    return resolved


class TestTypesOK:
    def test_smoke(self):
        c_str = "int main(void){ return 2;}"

        prog = prepare_program(c_str)

        target = SymbolTable()
        target.check_program(prog)

        assert len(target.symbol_table) == 1
        assert isinstance(target.symbol_table["main"], FunctionType)

    def test_simple_decl(self):
        c_str = "int main(void) { int a = 2; return a;}"

        prog = prepare_program(c_str)

        target = SymbolTable()
        target.check_program(prog)

        assert len(target.symbol_table) == 2
        assert isinstance(target.symbol_table["main"], FunctionType)
        assert isinstance(target.symbol_table["a.0"], VariableInt)

    def test_extra_function(self):
        c_str = """int foo(void) { return 2; }

        int main( void ) {
            return foo();
        }
        """
        prog = prepare_program(c_str)

        target = SymbolTable()
        target.check_program(prog)

        assert len(target.symbol_table) == 2
        assert isinstance(target.symbol_table["main"], FunctionType)
        assert isinstance(target.symbol_table["foo"], FunctionType)

    def test_func_with_arg(self):
        c_str = """int check(int a) { return a%2 ? 1: 2;}

        int main( void ) {
            int a = 10;
            return check(a);
        }
        """

        prog = prepare_program(c_str)

        target = SymbolTable()
        target.check_program(prog)

        assert len(target.symbol_table) == 4
        assert isinstance(target.symbol_table["main"], FunctionType)
        assert isinstance(target.symbol_table["check"], FunctionType)
        assert isinstance(target.symbol_table["a.arg.0"], VariableInt)
        assert isinstance(target.symbol_table["a.1"], VariableInt)
