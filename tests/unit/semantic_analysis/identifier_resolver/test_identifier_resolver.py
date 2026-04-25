import pytest

from nqcc.parser import (
    SourceBinaryExpressionNode,
    SourceCompoundNode,
    SourceFunctionCallNode,
    SourceFunctionDeclarationNode,
    SourceReturnNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    TokenTape,
    parse_function,
    parse_program,
)
from nqcc.semantic_analysis import (
    IdentifierInfo,
    IdentifierResolver,
    SemanticAnalysisUnknownIdentifier,
    resolve_program,
)


class TestFunction:
    def test_simple(self) -> None:
        resolver = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        c_str = "int main(void) { int a = 1; return a;}"
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolver.resolve_declaration(func, identifier_map)
        assert isinstance(updated, SourceFunctionDeclarationNode)
        assert updated.identifier == "main"
        assert updated.body is not None
        assert len(updated.body.items) == 2
        decl = updated.body.items[0]
        assert isinstance(decl, SourceVariableDeclarationNode)
        assert isinstance(decl.identifier, SourceVarNode)
        assert decl.identifier.identifier == "a.0"
        ret = updated.body.items[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "a.0"

    def test_with_nested(self) -> None:
        resolver = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

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

        updated = resolver.resolve_declaration(func, identifier_map)
        assert isinstance(updated, SourceFunctionDeclarationNode)
        assert updated.identifier == "main"
        assert updated.body is not None
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

    def test_internal_func_decl(self) -> None:
        resolver = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        c_str = """
        int main(void){
            int foo(void);
            return foo();
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolver.resolve_declaration(func, identifier_map)
        assert isinstance(updated, SourceFunctionDeclarationNode)
        assert updated.identifier == "main"
        assert updated.body is not None
        assert len(updated.body.items) == 2

        decl = updated.body.items[0]
        assert isinstance(decl, SourceFunctionDeclarationNode)
        assert decl.identifier == "foo"

        ret = updated.body.items[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceFunctionCallNode)
        assert ret.value.identifier == "foo"

    def test_no_nested_functions(self) -> None:
        resolver = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

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

        with pytest.raises(ValueError, match="Cannot nest function definitions"):
            _ = resolver.resolve_declaration(func, identifier_map)

    def test_func_one_arg(self) -> None:
        resolver = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        c_str = """
        int identity(int a){
            return a;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolver.resolve_declaration(func, identifier_map)
        assert isinstance(updated, SourceFunctionDeclarationNode)
        assert updated.identifier == "identity"
        assert len(updated.params) == 1
        assert updated.params[0] == "a.0"
        assert updated.body is not None
        assert len(updated.body.items) == 1

        instr0 = updated.body.items[0]
        assert isinstance(instr0, SourceReturnNode)
        assert isinstance(instr0.value, SourceVarNode)
        assert instr0.value.identifier == "a.0"

    def test_func_bad_arg(self) -> None:
        resolver = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        c_str = """
        int identity(int a){
            return b;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        with pytest.raises(SemanticAnalysisUnknownIdentifier, match="'b'"):
            _ = resolver.resolve_declaration(func, identifier_map)

    def test_arg_shadow_local_var(self) -> None:
        resolver = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        # OK since the function args are a separate scope
        c_str = """
        int main(void) {
            int a = 10;
            int f(int a);
            return f(a);
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolver.resolve_declaration(func, identifier_map)
        assert isinstance(updated, SourceFunctionDeclarationNode)
        assert updated.identifier == "main"


class TestProgram:
    def test_simple(self) -> None:
        c_str = "int main(void) { int a = 1; return a;}"
        token_tape = TokenTape.from_c_source(c_str)
        prog = parse_program(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_program(prog)

        updated_func = updated.functions[0]
        assert updated_func.identifier == "main"
        assert updated_func.body is not None
        assert len(updated_func.body.items) == 2
        decl = updated_func.body.items[0]
        assert isinstance(decl, SourceVariableDeclarationNode)
        assert isinstance(decl.identifier, SourceVarNode)
        assert decl.identifier.identifier == "a.0"
        ret = updated_func.body.items[1]
        assert isinstance(ret, SourceReturnNode)
        assert isinstance(ret.value, SourceVarNode)
        assert ret.value.identifier == "a.0"

    def test_func_with_decl(self) -> None:
        c_str = """
        int my_func(int a);

        int main(void) {
            return my_func(2);
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        prog = parse_program(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_program(prog)

        # Not much, but at least it's something...
        assert len(updated.functions) == 2

    def test_func_with_defn(self) -> None:
        c_str = """
        int my_func(int a) {
            return a + 1;
        }

        int main(void) {
            return my_func(2);
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        prog = parse_program(token_tape)
        assert token_tape.tokens_remaining == 0

        updated = resolve_program(prog)

        # Not much, but at least it's something...
        assert len(updated.functions) == 2
