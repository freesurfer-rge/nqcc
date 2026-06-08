import pytest

from nqcc.parser import SourceProgramNode, TokenTape, parse_program
from nqcc.semantic_analysis import (
    FunctionType,
    LocalVariableType,
    NoInitialiser,
    StaticVariableType,
    SymbolTable,
    label_loops_program,
    resolve_program,
)


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
        assert target.symbol_table["main"].is_global

    def test_simple_decl(self):
        c_str = "int main(void) { int a = 2; return a;}"

        prog = prepare_program(c_str)

        target = SymbolTable()
        target.check_program(prog)

        assert len(target.symbol_table) == 2
        assert isinstance(target.symbol_table["main"], FunctionType)
        assert target.symbol_table["main"].is_global
        assert isinstance(target.symbol_table["a.0"], LocalVariableType)
        assert target.symbol_table["a.0"].variable_type == "int"

    def test_extern_decl(self):
        c_str = "int main(void) { extern int a; return a;}"

        prog = prepare_program(c_str)

        target = SymbolTable()
        target.check_program(prog)

        assert len(target.symbol_table) == 2
        assert isinstance(target.symbol_table["main"], FunctionType)
        assert target.symbol_table["main"].is_global
        var_a = target.symbol_table["a"]
        assert isinstance(var_a, StaticVariableType)
        assert isinstance(var_a.initial_value, NoInitialiser)
        assert var_a.is_global

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
        assert target.symbol_table["main"].is_global
        assert isinstance(target.symbol_table["check"], FunctionType)
        assert target.symbol_table["check"].is_global
        assert isinstance(target.symbol_table["a.arg.0"], LocalVariableType)
        assert target.symbol_table["a.arg.0"].variable_type == "int"
        assert isinstance(target.symbol_table["a.1"], LocalVariableType)
        assert target.symbol_table["a.1"].variable_type == "int"

    def test_static_func(self):
        c_str = """static int check(int a) { return a%2 ? 1: 2;}

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
        assert target.symbol_table["main"].is_global
        assert isinstance(target.symbol_table["check"], FunctionType)
        assert not target.symbol_table["check"].is_global
        assert isinstance(target.symbol_table["a.arg.0"], LocalVariableType)
        assert target.symbol_table["a.arg.0"].variable_type == "int"
        assert isinstance(target.symbol_table["a.1"], LocalVariableType)
        assert target.symbol_table["a.1"].variable_type == "int"


class TestTypesFail:
    def test_arg_mismatch(self):
        c_str = """int foo(void) { return 10; }

        int main(void) {
            return foo(1);
        }
        """

        prog = prepare_program(c_str)

        target = SymbolTable()
        with pytest.raises(ValueError, match="Wrong arg count"):
            target.check_program(prog)

    def test_incompatible_redeclaration(self):
        c_str = """
        int main(void) {
            int foo(int a);
            return foo(10);
        }

        int foo(int a, int b);
        """

        prog = prepare_program(c_str)

        target = SymbolTable()
        with pytest.raises(ValueError, match="Incompatible function declarations"):
            target.check_program(prog)

    def test_multiple_definitions(self):
        c_str = """
        int foo(void) { return 10; }
        int foo(void) {return 11; }
        """
        prog = prepare_program(c_str)

        target = SymbolTable()
        with pytest.raises(ValueError, match="Function defined more than once"):
            target.check_program(prog)

    def test_var_as_func(self):
        c_str = """
        int main(void) {
            int a = 1;
            return a();
        }
        """

        prog = prepare_program(c_str)

        target = SymbolTable()
        with pytest.raises(ValueError, match="Variable used as function name"):
            target.check_program(prog)

    def test_func_as_var(self):
        c_str = """
        int main(void) {
            int a(void);

            return a + 1;
        }
        """

        prog = prepare_program(c_str)

        target = SymbolTable()
        with pytest.raises(ValueError, match="Function name used as variable"):
            target.check_program(prog)

    def test_extern_decl_with_initialiser(self):
        c_str = "int main(void) { extern int a = 2; return a;}"

        prog = prepare_program(c_str)

        target = SymbolTable()
        with pytest.raises(ValueError, match="Initialiser on local extern variable"):
            target.check_program(prog)

    def test_extern_decl_redeclare_func(self):
        c_str = """
        int main(void) {
            int a(void);
            extern int a;

            return 1;
        }
        """

        prog = prepare_program(c_str)

        target = SymbolTable()
        with pytest.raises(ValueError, match="Function redeclared as variable"):
            target.check_program(prog)
