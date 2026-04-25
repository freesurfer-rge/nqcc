import pytest

from nqcc.parser import (
    SourceBinaryExpressionNode,
    SourceCompoundNode,
    SourceReturnNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    TokenTape,
    parse_function,
    parse_program,
)
from nqcc.semantic_analysis import (
    resolve_function,
    resolve_program,
)


class TestFunction:
    def test_simple(self):
        c_str = "int main(void) { int a = 1; return a;}"
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_function(func)
        assert updated.identifier == "main"
        assert len(updated.body.items) == 2
        decl = updated.body.items[0]
        assert isinstance(decl, SourceVariableDeclarationNode)
        assert isinstance(decl.identifier, SourceVarNode)
        assert decl.identifier.identifier == "a.0"
        ret = updated.body.items[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "a.0"

    def test_with_nested(self):
        c_str = """int main( void ) {
            int x=1;
            {
                int y = x+1;
                int x = 2;
            }
            return x;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_function(func)
        assert updated.identifier == "main"
        assert len(updated.body.items) == 3

        decl0 = updated.body.items[0]
        assert isinstance(decl0, SourceVariableDeclarationNode)
        assert isinstance(decl0.identifier, SourceVarNode)
        assert decl0.identifier.identifier == "x.0"

        compound0 = updated.body.items[1]
        assert isinstance(compound0, SourceCompoundNode)
        assert len(compound0.block.items) == 2

        decl1 = compound0.block.items[0]
        assert isinstance(decl1, SourceVariableDeclarationNode)
        assert isinstance(decl1.identifier, SourceVarNode)
        assert decl1.identifier.identifier == "y.1"
        assert isinstance(decl1.initial, SourceBinaryExpressionNode)
        assert isinstance(decl1.initial.left, SourceVarNode)
        assert decl1.initial.left.identifier == "x.0"

        decl2 = compound0.block.items[1]
        assert isinstance(decl2, SourceVariableDeclarationNode)
        assert isinstance(decl2.identifier, SourceVarNode)
        assert decl2.identifier.identifier == "x.2"

        ret = updated.body.items[2]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "x.0"

    def test_internal_func_defn(self):
        c_str = """
        int main(void){
            int foo(void);
            return foo();
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_function(func)
        assert updated.identifier == "main"
        assert len(updated.body.items) == 3

    def test_no_nested_functions(self):
        c_str = """int main( void ) {
            int my_func(int a)
            {
                return a;
            }
            return 2;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        with pytest.raises(ValueError, match="Soemthing"):
            _ = resolve_function(func)


class TestProgram:
    def test_simple(self):
        c_str = "int main(void) { int a = 1; return a;}"
        token_tape = TokenTape.from_c_source(c_str)
        prog = parse_program(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_program(prog)

        updated_func = updated.functions[0]
        assert updated_func.identifier == "main"
        assert len(updated_func.body.items) == 2
        decl = updated_func.body.items[0]
        assert isinstance(decl, SourceVariableDeclarationNode)
        assert isinstance(decl.identifier, SourceVarNode)
        assert decl.identifier.identifier == "a.0"
        ret = updated_func.body.items[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "a.0"
