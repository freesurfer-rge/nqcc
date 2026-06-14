from nqcc.parser import (
    SourceFunctionDeclarationNode,
    SourceProgramNode,
    TokenTape,
    parse_block_item,
    parse_function,
    parse_program,
)
from nqcc.semantic_analysis import (
    IdentifierInfo,
    IdentifierResolver,
    SymbolTable,
    label_loops_program,
    resolve_program,
)
from nqcc.tacky import (
    TackyAdd,
    TackyBinaryNode,
    TackyConstantIntNode,
    TackyCopyNode,
    TackyFunctionCallNode,
    TackyFunctionNode,
    TackyGenerator,
    TackyMultiply,
    TackyNegate,
    TackyProgramNode,
    TackyReturnNode,
    TackyUnaryNode,
    TackyVarNode,
)

# These tests access internals of the TackyGenerator

# In general, we will skip the semantic analysis step here


class TestBlockItems:
    def test_declaration(self):
        source = "int a;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_block_item(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_declaration"

        # Skip semantic analysis for now
        target.emit_blockitem(src_node)

        # Nothing generated for a plain declaration
        assert len(target._current_instructions) == 0

    def test_declaration_with_init(self):
        source = "int a=1+2;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_block_item(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_declaration"

        # Skip semantic analysis for now
        target.emit_blockitem(src_node)

        assert len(target._current_instructions) == 2
        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyBinaryNode)
        assert isinstance(instr0.operator, TackyAdd)
        assert instr0.dst == TackyVarNode(start_position=7, identifier="tmp.test_declaration.0")
        assert instr0.left == TackyConstantIntNode(start_position=6, value=1)
        assert instr0.right == TackyConstantIntNode(start_position=8, value=2)


class TestFunctions:
    def test_simple(self) -> None:
        source = "int main(void) {return -    508;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)

        st = SymbolTable()
        st.check_function_declaration(src_node)

        target = TackyGenerator()

        result = target.emit_function(src_node, st)
        assert isinstance(result, TackyFunctionNode)
        assert result.identifier == "main"
        assert result.is_global
        assert len(result.instructions) == 3

        instr0 = result.instructions[0]
        assert isinstance(instr0, TackyUnaryNode)
        assert instr0 == TackyUnaryNode(
            start_position=23,
            operator=TackyNegate(start_position=23),
            src=TackyConstantIntNode(start_position=28, value=508),
            dst=TackyVarNode(start_position=23, identifier="tmp.main.0"),
        )

        instr1 = result.instructions[1]
        assert isinstance(instr1, TackyReturnNode)
        assert instr1 == TackyReturnNode(start_position=16, value=instr0.dst)

        # Recall that we force an extra 'return 0' in the tacky function generator
        assert result.instructions[-1] == TackyReturnNode(
            start_position=0, value=TackyConstantIntNode(start_position=0, value=0)
        )

    def test_simple_static(self) -> None:
        source = "static int get_const(void) {return -    508;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)

        st = SymbolTable()
        st.check_function_declaration(src_node)

        target = TackyGenerator()

        result = target.emit_function(src_node, st)
        assert isinstance(result, TackyFunctionNode)
        assert result.identifier == "get_const"
        assert not result.is_global
        assert len(result.instructions) == 3

        instr0 = result.instructions[0]
        assert isinstance(instr0, TackyUnaryNode)
        assert instr0 == TackyUnaryNode(
            start_position=35,
            operator=TackyNegate(start_position=35),
            src=TackyConstantIntNode(start_position=40, value=508),
            dst=TackyVarNode(start_position=35, identifier="tmp.get_const.0"),
        )

        instr1 = result.instructions[1]
        assert isinstance(instr1, TackyReturnNode)
        assert instr1 == TackyReturnNode(start_position=28, value=instr0.dst)

        # Recall that we force an extra 'return 0' in the tacky function generator
        assert result.instructions[-1] == TackyReturnNode(
            start_position=0, value=TackyConstantIntNode(start_position=0, value=0)
        )

    def test_simple_decl(self) -> None:
        source = """int main (  void ) {
            int a;
            int b = 1;
            a = b * 2;
            return a;
        }"""

        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)

        st = SymbolTable()
        st.check_function_declaration(src_node)

        resolver = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        resolved_node = resolver.resolve_declaration(src_node, identifier_map, at_file_scope=True)
        assert isinstance(resolved_node, SourceFunctionDeclarationNode)

        target = TackyGenerator()

        result = target.emit_function(resolved_node, st)
        assert isinstance(result, TackyFunctionNode)
        assert result.identifier == "main"
        assert result.is_global
        assert len(result.instructions) == 5

        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyCopyNode)
        assert instr0.src == TackyConstantIntNode(start_position=60, value=1)
        assert instr0.dst == TackyVarNode(start_position=56, identifier="b.1")

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyBinaryNode)
        assert isinstance(instr1.operator, TackyMultiply)
        assert instr1.dst == TackyVarNode(start_position=81, identifier="tmp.main.0")
        assert instr1.left == TackyVarNode(start_position=79, identifier="b.1")
        assert instr1.right == TackyConstantIntNode(start_position=83, value=2)

        instr2 = target._current_instructions[2]
        assert isinstance(instr2, TackyCopyNode)
        assert instr2.src == TackyVarNode(start_position=81, identifier="tmp.main.0")
        assert instr2.dst == TackyVarNode(start_position=75, identifier="a.0")

        instr3 = target._current_instructions[3]
        assert isinstance(instr3, TackyReturnNode)
        assert instr3.value == TackyVarNode(start_position=105, identifier="a.0")

        # Recall that we force an extra 'return 0' in the tacky function generator
        assert result.instructions[-1] == TackyReturnNode(
            start_position=0, value=TackyConstantIntNode(start_position=0, value=0)
        )


def prepare_program(c_str: str) -> tuple[SourceProgramNode, SymbolTable]:
    token_tape = TokenTape.from_c_source(c_str)

    program = parse_program(token_tape)

    resolved_program = resolve_program(program)

    # Recall that label_loops_program is in-place
    label_loops_program(resolved_program)

    st = SymbolTable()
    st.check_program(resolved_program)

    return resolved_program, st


class TestPrograms:
    def test_simple(self):
        source = " int main(void) {return -    566;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        st = SymbolTable()
        st.check_program(src_node)

        target = TackyGenerator()

        result = target.emit_program(src_node, st)
        assert isinstance(result, TackyProgramNode)
        assert result.start_position == 0

        assert len(result.definitions) == 1
        main_func = result.definitions[0]
        assert isinstance(main_func, TackyFunctionNode)
        assert main_func.identifier == "main"
        assert main_func.start_position == 1
        assert len(main_func.instructions) == 3

        instr0 = main_func.instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=24,
            operator=TackyNegate(start_position=24),
            src=TackyConstantIntNode(start_position=29, value=566),
            dst=TackyVarNode(start_position=24, identifier="tmp.main.0"),
        )

        instr1 = main_func.instructions[1]
        assert instr1 == TackyReturnNode(start_position=17, value=instr0.dst)

        # Recall that we force an extra 'return 0' in the tacky function generator
        assert main_func.instructions[-1] == TackyReturnNode(
            start_position=0, value=TackyConstantIntNode(start_position=0, value=0)
        )

    def test_func_call(self):
        c_str = """
        int inc(int a);

        int inc(int a) {
            return a+1;
        }

        int main( void ) {
            return inc(2);
        }
        """

        src_node, symbol_table = prepare_program(c_str)
        assert isinstance(src_node, SourceProgramNode)

        target = TackyGenerator()

        result = target.emit_program(src_node, symbol_table)
        assert isinstance(result, TackyProgramNode)
        # Make sure we don't have duplicate from the declaration of 'inc'
        assert len(result.definitions) == 2

        tacky_inc = result.definitions[0]
        assert isinstance(tacky_inc, TackyFunctionNode)
        assert tacky_inc.identifier == "inc"
        assert len(tacky_inc.params) == 1
        assert tacky_inc.params[0] == "a.arg.1"
        assert len(tacky_inc.instructions) == 3
        inc_instr0 = tacky_inc.instructions[0]
        assert isinstance(inc_instr0, TackyBinaryNode)
        assert isinstance(inc_instr0.operator, TackyAdd)
        assert inc_instr0.left == TackyVarNode(start_position=70, identifier="a.arg.1")
        assert inc_instr0.right == TackyConstantIntNode(start_position=72, value=1)
        assert inc_instr0.dst == TackyVarNode(start_position=71, identifier="tmp.inc.0")
        inc_instr1 = tacky_inc.instructions[1]
        assert isinstance(inc_instr1, TackyReturnNode)
        assert inc_instr1.value == inc_instr0.dst
        inc_instr2 = tacky_inc.instructions[2]
        # The 'guard' return
        assert isinstance(inc_instr2, TackyReturnNode)
        assert inc_instr2 == TackyReturnNode(
            start_position=0, value=TackyConstantIntNode(start_position=0, value=0)
        )

        tacky_main = result.definitions[1]
        assert isinstance(tacky_main, TackyFunctionNode)
        assert tacky_main.identifier == "main"
        assert len(tacky_main.params) == 0
        assert len(tacky_main.instructions) == 3

        main_instr0 = tacky_main.instructions[0]
        assert isinstance(main_instr0, TackyFunctionCallNode)
        assert main_instr0.identifier == "inc"
        assert len(main_instr0.args) == 1
        assert main_instr0.args[0] == TackyConstantIntNode(start_position=136, value=2)
        assert main_instr0.dst == TackyVarNode(start_position=132, identifier="tmp.main.0")

        main_instr1 = tacky_main.instructions[1]
        assert isinstance(main_instr1, TackyReturnNode)
        assert main_instr1.value == main_instr0.dst

        main_instr2 = tacky_main.instructions[2]
        # The 'guard' return
        assert isinstance(main_instr2, TackyReturnNode)
        assert main_instr2 == TackyReturnNode(
            start_position=0, value=TackyConstantIntNode(start_position=0, value=0)
        )

    def test_shadow_name(self):
        # This is OK, since the function declaration is a separate scope
        # (modified from the book's test suite)
        c_str = """
        int main(void) {
            int a = 10;
            int g(int a);
            return g(a);
        }

        int g(int a) {
            return a % 2;
        }
        """
        src_node, symbol_table = prepare_program(c_str)
        assert isinstance(src_node, SourceProgramNode)

        target = TackyGenerator()

        result = target.emit_program(src_node, symbol_table)
        assert isinstance(result, TackyProgramNode)
        # Make sure we don't have duplicate from the declaration of 'g'
        assert len(result.definitions) == 2
