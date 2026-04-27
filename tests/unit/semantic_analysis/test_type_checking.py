from nqcc.semantic_analysis import SymbolTable, resolve_program, label_loops_program, FunctionType, VariableType, VariableInt


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
