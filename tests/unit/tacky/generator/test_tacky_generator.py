from nqcc.parser import TokenTape, parse_block_item, parse_function, parse_program, parse_statement
from nqcc.semantic_analysis import LoopLabeller, resolve_function
from nqcc.tacky import (
    TackyAdd,
    TackyBinaryNode,
    TackyComplement,
    TackyConstantIntNode,
    TackyCopyNode,
    TackyFunctionNode,
    TackyGenerator,
    TackyJumpIfZeroNode,
    TackyJumpNode,
    TackyLabelNode,
    TackyLessThan,
    TackyMultiply,
    TackyNegate,
    TackyProgramNode,
    TackyReturnNode,
    TackySubtract,
    TackyUnaryNode,
    TackyVarNode,
)

# These tests access internals of the TackyGenerator

# In general, we will skip the semantic analysis step here


class TestStatements:
    def test_null_statement(self):
        source = " ;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_statement(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_return"

        target.emit_statement(src_node)
        assert len(target._current_instructions) == 0

    def test_expression_statement(self):
        source = "a = 1;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_statement(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_expression_statement"

        target.emit_statement(src_node)
        assert len(target._current_instructions) == 1
        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyCopyNode)
        assert instr0.dst == TackyVarNode(start_position=0, identifier="a")
        assert instr0.src == TackyConstantIntNode(start_position=4, value=1)

    def test_return(self):
        source = "return ~ 162;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_statement(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_return"

        target.emit_statement(src_node)
        assert target._nxt_tmp == 1, "Expected one temporary used"
        assert len(target._current_instructions) == 2, "Expected two instructions"

        instr0 = target._current_instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=7,
            operator=TackyComplement(start_position=7),
            src=TackyConstantIntNode(start_position=9, value=162),
            dst=TackyVarNode(start_position=7, identifier="tmp.test_return.0"),
        )
        instr1 = target._current_instructions[1]
        assert instr1 == TackyReturnNode(start_position=0, value=instr0.dst)

    def test_return_longer(self):
        # Note the space, to avoid parsing as decrement operator
        source = "return 2- -1;"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_statement(token_tape)

        target = TackyGenerator()
        target._curr_function = "test_return_longer"

        target.emit_statement(src_node)
        assert target._nxt_tmp == 2
        assert len(target._current_instructions) == 3

        instr0 = target._current_instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=10,
            operator=TackyNegate(start_position=10),
            src=TackyConstantIntNode(start_position=11, value=1),
            dst=TackyVarNode(start_position=10, identifier="tmp.test_return_longer.0"),
        )

        instr1 = target._current_instructions[1]
        assert instr1 == TackyBinaryNode(
            start_position=8,
            operator=TackySubtract(start_position=8),
            left=TackyConstantIntNode(start_position=7, value=2),
            right=instr0.dst,
            dst=TackyVarNode(start_position=8, identifier="tmp.test_return_longer.1"),
        )

        instr2 = target._current_instructions[2]
        assert instr2 == TackyReturnNode(start_position=0, value=instr1.dst)

    def test_if_then(self):
        # Add a non-else statement to make sure we parse OK
        source = "if(a) a=a+1; int b;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 13
        src_node = parse_statement(token_tape)
        # Make sure we left the declaration
        assert token_tape.tokens_remaining == 3

        # As ever, we skip semantic analysis for simplicity

        target = TackyGenerator()
        target._curr_function = "test_if_then"

        target.emit_statement(src_node)
        assert target._nxt_tmp == 1
        assert len(target._current_instructions) == 4

        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyJumpIfZeroNode)
        assert instr0.condition == TackyVarNode(start_position=3, identifier="a")
        assert instr0.target == "label.test_if_then.ifend.1"

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyBinaryNode)
        assert instr1.dst == TackyVarNode(start_position=9, identifier="tmp.test_if_then.0")
        assert instr1.left == TackyVarNode(start_position=8, identifier="a")
        assert instr1.right == TackyConstantIntNode(start_position=10, value=1)
        assert isinstance(instr1.operator, TackyAdd)

        instr2 = target._current_instructions[2]
        assert isinstance(instr2, TackyCopyNode)
        assert instr2.dst == TackyVarNode(start_position=6, identifier="a")
        assert instr2.src == instr1.dst

        instr3 = target._current_instructions[3]
        assert isinstance(instr3, TackyLabelNode)
        assert instr3.identifier == "label.test_if_then.ifend.1"

    def test_if_then_else(self):
        # Add a non-else statement to make sure we parse OK
        source = "if(a<9) a=a+1; else b=a+3;"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 19
        src_node = parse_statement(token_tape)
        # With the else, should consume everything
        assert token_tape.tokens_remaining == 0

        # As ever, we skip semantic analysis for simplicity

        target = TackyGenerator()
        target._curr_function = "test_if_then_else"

        target.emit_statement(src_node)
        assert target._nxt_tmp == 3
        assert target._nxt_lbl == 2
        assert len(target._current_instructions) == 9

        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyBinaryNode)
        assert isinstance(instr0.operator, TackyLessThan)
        assert instr0.left == TackyVarNode(start_position=3, identifier="a")
        assert instr0.right == TackyConstantIntNode(start_position=5, value=9)
        assert instr0.dst == TackyVarNode(start_position=4, identifier="tmp.test_if_then_else.0")

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyJumpIfZeroNode)
        assert instr1.condition == TackyVarNode(
            start_position=4, identifier="tmp.test_if_then_else.0"
        )
        assert instr1.target == "label.test_if_then_else.ifotherwise.0"

        instr2 = target._current_instructions[2]
        assert isinstance(instr2, TackyBinaryNode)
        assert isinstance(instr2.operator, TackyAdd)
        assert instr2.left == TackyVarNode(start_position=10, identifier="a")
        assert instr2.right == TackyConstantIntNode(start_position=12, value=1)
        assert instr2.dst == TackyVarNode(start_position=11, identifier="tmp.test_if_then_else.1")

        instr3 = target._current_instructions[3]
        assert isinstance(instr3, TackyCopyNode)
        assert instr3.src == instr2.dst
        assert instr3.dst == TackyVarNode(start_position=8, identifier="a")

        instr4 = target._current_instructions[4]
        assert isinstance(instr4, TackyJumpNode)
        assert instr4.target == "label.test_if_then_else.ifend.1"

        instr5 = target._current_instructions[5]
        assert isinstance(instr5, TackyLabelNode)
        assert instr5.identifier == "label.test_if_then_else.ifotherwise.0"

        instr6 = target._current_instructions[6]
        assert isinstance(instr6, TackyBinaryNode)
        assert isinstance(instr6.operator, TackyAdd)
        assert instr6.left == TackyVarNode(start_position=22, identifier="a")
        assert instr6.right == TackyConstantIntNode(start_position=24, value=3)
        assert instr6.dst == TackyVarNode(start_position=23, identifier="tmp.test_if_then_else.2")

        instr7 = target._current_instructions[7]
        assert isinstance(instr7, TackyCopyNode)
        assert instr7.src == instr6.dst
        assert instr7.dst == TackyVarNode(start_position=20, identifier="b")

        instr8 = target._current_instructions[8]
        assert isinstance(instr8, TackyLabelNode)
        assert instr8.identifier == "label.test_if_then_else.ifend.1"

    def test_compound(self):
        source = "{ int a = 1; }"
        token_tape = TokenTape.from_c_source(source)
        assert token_tape.tokens_remaining == 7
        src_node = parse_statement(token_tape)
        # With the else, should consume everything
        assert token_tape.tokens_remaining == 0

        # We skip semantic analysis for simplicity

        target = TackyGenerator()
        target._curr_function = "test_compound"

        target.emit_statement(src_node)

        assert len(target._current_instructions) == 1
        instr0 = target._current_instructions[0]
        assert isinstance(instr0, TackyCopyNode)
        assert instr0.dst == TackyVarNode(start_position=6, identifier="a")
        assert instr0.src == TackyConstantIntNode(start_position=10, value=1)

    def test_while(self):
        source = """
        while( a < 10 ) {
          if( a==2 ) continue;
          a = a + 1;
          break;
        }
        """
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_block_item(token_tape)

        labeller = LoopLabeller(function_name="test_while")
        labeller.label_statement(src_node, current_label="")

        target = TackyGenerator()
        target._curr_function = "test_while"

        # Skip semantic analysis for now
        target.emit_statement(src_node)
        assert len(target._current_instructions) == 12

        instr0 = target._current_instructions[0]
        assert instr0 == TackyLabelNode(start_position=9, identifier="continue_while.test_while.0")

        instr1 = target._current_instructions[1]
        assert isinstance(instr1, TackyBinaryNode)

        instr2 = target._current_instructions[2]
        assert instr2 == TackyJumpIfZeroNode(
            start_position=18, target="break_while.test_while.0", condition=instr1.dst
        )

        instr3 = target._current_instructions[3]
        assert isinstance(instr3, TackyBinaryNode)

        instr4 = target._current_instructions[4]
        assert instr4 == TackyJumpIfZeroNode(
            start_position=37, target="label.test_while.ifend.1", condition=instr3.dst
        )

        instr5 = target._current_instructions[5]
        assert instr5 == TackyJumpNode(start_position=48, target="continue_while.test_while.0")

        instr6 = target._current_instructions[6]
        assert instr6 == TackyLabelNode(start_position=37, identifier="label.test_while.ifend.1")

        instr7 = target._current_instructions[7]
        assert isinstance(instr7, TackyBinaryNode)

        instr8 = target._current_instructions[8]
        assert isinstance(instr8, TackyCopyNode)

        instr9 = target._current_instructions[9]
        assert instr9 == TackyJumpNode(start_position=89, target="break_while.test_while.0")

        instr10 = target._current_instructions[10]
        assert instr10 == TackyJumpNode(start_position=9, target="continue_while.test_while.0")

        instr11 = target._current_instructions[11]
        assert instr11 == TackyLabelNode(start_position=9, identifier="break_while.test_while.0")


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
    def test_simple(self):
        source = "int main(void) {return -    508;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)

        target = TackyGenerator()

        result = target.emit_function(src_node)
        assert isinstance(result, TackyFunctionNode)
        assert result.identifier == "main"
        assert len(result.instructions) == 3

        instr0 = result.instructions[0]
        assert instr0 == TackyUnaryNode(
            start_position=23,
            operator=TackyNegate(start_position=23),
            src=TackyConstantIntNode(start_position=28, value=508),
            dst=TackyVarNode(start_position=23, identifier="tmp.main.0"),
        )

        instr1 = result.instructions[1]
        assert instr1 == TackyReturnNode(start_position=16, value=instr0.dst)

        # Recall that we force an extra 'return 0' in the tacky function generator
        assert result.instructions[-1] == TackyReturnNode(
            start_position=0, value=TackyConstantIntNode(start_position=0, value=0)
        )

    def test_simple_decl(self):
        source = """int main (  void ) {
            int a;
            int b = 1;
            a = b * 2;
            return a;
        }"""

        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)
        resolved_node = resolve_function(src_node)

        target = TackyGenerator()

        result = target.emit_function(resolved_node)
        assert isinstance(result, TackyFunctionNode)
        assert result.identifier == "main"
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


class TestPrograms:
    def test_simple(self):
        source = " int main(void) {return -    566;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        target = TackyGenerator()

        result = target.emit_program(src_node)
        assert isinstance(result, TackyProgramNode)
        assert result.start_position == 0

        main_func = result.function_definition
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
