from nqcc.codegen import (
    AsmAdd,
    AsmBinaryNode,
    AsmFunctionNode,
    AsmImmediateIntNode,
    AsmMovNode,
    AsmNeg,
    AsmNot,
    AsmProgramNode,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmStaticVariableNode,
    AsmUnaryNode,
    convert_tacky_function,
    convert_tacky_operand,
    convert_tacky_program,
)
from nqcc.parser import TokenTape, parse_function, parse_program
from nqcc.semantic_analysis import SymbolTable
from nqcc.tacky import (
    TackyConstantIntNode,
    TackyGenerator,
    TackyVarNode,
)


class TestConvertOperands:
    def test_constant_int(self):
        target = TackyConstantIntNode(start_position=123, value=345)
        result = convert_tacky_operand(target)
        assert isinstance(result, AsmImmediateIntNode)
        assert result.start_position == target.start_position
        assert result.value == target.value

    def test_var(self):
        target = TackyVarNode(start_position=222, identifier="my.value.0")
        result = convert_tacky_operand(target)
        assert isinstance(result, AsmPseudoRegisterNode)
        assert result.start_position == target.start_position
        assert result.identifier == target.identifier


class TestFunctions:
    def test_simple(self):
        source = "   int main(void) {return -    508;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)

        st = SymbolTable()
        st.check_function_declaration(src_node)

        tg = TackyGenerator()
        tacky_func = tg.emit_function(src_node, st)

        asm_func = convert_tacky_function(tacky_func)
        assert isinstance(asm_func, AsmFunctionNode)
        assert asm_func.start_position == 3
        assert asm_func.identifier == "main"
        # Add two instructions for 'guard' return added by Tacky
        assert len(asm_func.instructions) == 4 + 2

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=26,
            src=AsmImmediateIntNode(start_position=31, value=508),
            dst=AsmPseudoRegisterNode(start_position=26, identifier="tmp.main.0"),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmUnaryNode(start_position=26, operator=AsmNeg(start_position=26), src=i0.dst)

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            src=i1.src,
            dst=AsmRegisterNode(start_position=19, value="AX"),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmRetNode(start_position=19)

    def test_simple_add(self):
        source = "   int main(void) {return 1 + 4;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)

        st = SymbolTable()
        st.check_function_declaration(src_node)

        tg = TackyGenerator()
        tacky_func = tg.emit_function(src_node, st)

        asm_func = convert_tacky_function(tacky_func)
        assert isinstance(asm_func, AsmFunctionNode)
        assert asm_func.start_position == 3
        assert asm_func.identifier == "main"
        # Add two instructions for 'guard' return added by Tacky
        assert len(asm_func.instructions) == 4 + 2

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=28,
            src=AsmImmediateIntNode(start_position=26, value=1),
            dst=AsmPseudoRegisterNode(start_position=28, identifier="tmp.main.0"),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmBinaryNode(
            start_position=28,
            operator=AsmAdd(start_position=28),
            src=AsmImmediateIntNode(start_position=30, value=4),
            dst=AsmPseudoRegisterNode(start_position=28, identifier="tmp.main.0"),
        )

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            src=i1.dst,
            dst=AsmRegisterNode(start_position=19, value="AX"),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmRetNode(start_position=19)


class TestPrograms:
    def test_simple(self):
        source = "   int main(void) {return ~(    509);}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        st = SymbolTable()
        st.check_program(src_node)

        tg = TackyGenerator()
        tacky_program = tg.emit_program(src_node, st)

        asm_prog = convert_tacky_program(tacky_program)
        assert isinstance(asm_prog, AsmProgramNode)
        assert asm_prog.start_position == 0

        assert len(asm_prog.definitions) == 1
        asm_func = asm_prog.definitions[0]
        assert asm_func.start_position == 3
        assert asm_func.identifier == "main"
        # Add two instructions for 'guard' return added by Tacky
        assert len(asm_func.instructions) == 4 + 2

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=26,
            src=AsmImmediateIntNode(start_position=32, value=509),
            dst=AsmPseudoRegisterNode(start_position=26, identifier="tmp.main.0"),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmUnaryNode(start_position=26, operator=AsmNot(start_position=26), src=i0.dst)

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            src=i1.src,
            dst=AsmRegisterNode(start_position=19, value="AX"),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmRetNode(start_position=19)

    def test_simple_function_call(self):
        # This is little more than a smoke test
        source = """
        int get_val(void) { return 2;}

        int main(void) { return get_val(); }
        """
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        st = SymbolTable()
        st.check_program(src_node)

        tg = TackyGenerator()
        tacky_program = tg.emit_program(src_node, st)

        asm_prog = convert_tacky_program(tacky_program)
        assert isinstance(asm_prog, AsmProgramNode)
        assert asm_prog.start_position == 0

        assert len(asm_prog.definitions) == 2

        f0 = asm_prog.definitions[0]
        assert isinstance(f0, AsmFunctionNode)
        assert f0.identifier == "get_val"
        assert f0.is_global
        # Guard, addition and return
        assert len(f0.instructions) == 2 + 2

        f1 = asm_prog.definitions[1]
        assert isinstance(f1, AsmFunctionNode)
        assert f1.identifier == "main"
        assert f1.is_global
        assert len(f1.instructions) == 2 + 4

    def test_simple_static_function_call(self):
        # Like the previous, but make get_val static
        source = """
        static int get_val(void) { return 2;}

        int main(void) { return get_val(); }
        """
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        st = SymbolTable()
        st.check_program(src_node)

        tg = TackyGenerator()
        tacky_program = tg.emit_program(src_node, st)

        asm_prog = convert_tacky_program(tacky_program)
        assert isinstance(asm_prog, AsmProgramNode)
        assert asm_prog.start_position == 0

        assert len(asm_prog.definitions) == 2

        f0 = asm_prog.definitions[0]
        assert isinstance(f0, AsmFunctionNode)
        assert f0.identifier == "get_val"
        assert not f0.is_global
        # Guard, addition and return
        assert len(f0.instructions) == 2 + 2

        f1 = asm_prog.definitions[1]
        assert isinstance(f1, AsmFunctionNode)
        assert f1.identifier == "main"
        assert f1.is_global
        assert len(f1.instructions) == 2 + 4

    def test_simple_static_variable(self):
        # Like the previous, but make get_val static
        source = """
        static int value = 2;

        int main(void) { return value; }
        """
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        st = SymbolTable()
        st.check_program(src_node)

        tg = TackyGenerator()
        tacky_program = tg.emit_program(src_node, st)

        asm_prog = convert_tacky_program(tacky_program)
        assert isinstance(asm_prog, AsmProgramNode)
        assert asm_prog.start_position == 0

        assert len(asm_prog.definitions) == 2

        f_0 = asm_prog.definitions[0]
        assert isinstance(f_0, AsmFunctionNode)
        assert f_0.identifier == "main"
        assert f_0.is_global
        assert len(f_0.instructions) == 2 + 2

        v_0 = asm_prog.definitions[1]
        assert isinstance(v_0, AsmStaticVariableNode)
        assert v_0.identifier == "value"
        assert not v_0.is_global
        assert v_0.init == 2
