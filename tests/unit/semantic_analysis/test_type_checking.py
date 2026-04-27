from nqcc.semantic_analysis import SymbolTable, resolve_program, label_loops_program


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
