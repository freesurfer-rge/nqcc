import pytest

from nqcc.parser import (
    SourceBreakNode,
    SourceCompoundNode,
    SourceContinueNode,
    SourceDoWhileNode,
    SourceIfStatementNode,SourceForNode,
    SourceWhileNode,
    TokenTape,
    parse_function,
)
from nqcc.semantic_analysis import LoopLabeller, SemanticAnalysisOutsideLoop, label_loops_function


class TestErrors:
    def test_outside_break(self):
        target = LoopLabeller(function_name="aaaa")

        stmt = SourceBreakNode(start_position=1)
        with pytest.raises(SemanticAnalysisOutsideLoop) as saeol:
            _ = target.label_statement(stmt, "")
        assert saeol.value.message == "Outside loop: SourceBreakNode 1"

    def test_outside_continue(self):
        target = LoopLabeller(function_name="aaaa")

        stmt = SourceContinueNode(start_position=112)
        with pytest.raises(SemanticAnalysisOutsideLoop) as saeol:
            _ = target.label_statement(stmt, "")
        assert saeol.value.message == "Outside loop: SourceContinueNode 112"


class TestWhileLabelling:
    def test_simple(self):
        # This looks odd, but we need to check both side of the if
        c_str = """
        int main( void ) {
            int a = 0;
            int b = 2;
            while( a < 10 ) {
                if( a== 2) continue; else continue;
                if( b> 120) break;
                b = b * 2;
            }
            return b;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        # We don't need to do variable resolution to test

        label_loops_function(func)

        assert len(func.body.items) == 4
        while_stmt = func.body.items[2]
        assert isinstance(while_stmt, SourceWhileNode)
        assert while_stmt.label == "while.main.0"

        assert isinstance(while_stmt.body, SourceCompoundNode)
        assert len(while_stmt.body.block.items) == 3

        if_cont = while_stmt.body.block.items[0]
        assert isinstance(if_cont, SourceIfStatementNode)
        assert isinstance(if_cont.then, SourceContinueNode)
        assert if_cont.then.label == "while.main.0"
        assert isinstance(if_cont.otherwise, SourceContinueNode)
        assert if_cont.otherwise.label == "while.main.0"

        if_break = while_stmt.body.block.items[1]
        assert isinstance(if_break, SourceIfStatementNode)
        assert isinstance(if_break.then, SourceBreakNode)
        assert if_break.then.label == "while.main.0"

    def test_nested(self):
        c_str = """
        int main( void ) {
            int a = 0;
            int b = 2;
            while( a < 10 ) {
                int c = 0;
                while( c < 12 ) {
                    if( c%2 == 0) break;
                    b = b+1;
                    c = c + 3;
                }
                if( b> 120) continue;
                b = b * 2;
            }
            return b;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        # We don't need to do variable resolution to test

        label_loops_function(func)
        assert len(func.body.items) == 4

        outer_while = func.body.items[2]
        assert isinstance(outer_while, SourceWhileNode)
        assert outer_while.label == "while.main.0"

        assert isinstance(outer_while.body, SourceCompoundNode)
        assert len(outer_while.body.block.items) == 4

        inner_while = outer_while.body.block.items[1]
        assert isinstance(inner_while, SourceWhileNode)
        assert inner_while.label == "while.main.1"
        assert isinstance(inner_while.body, SourceCompoundNode)
        assert len(inner_while.body.block.items) == 3
        inner_if = inner_while.body.block.items[0]
        assert isinstance(inner_if, SourceIfStatementNode)
        assert isinstance(inner_if.then, SourceBreakNode)
        assert inner_if.then.label == "while.main.1"

        outer_if = outer_while.body.block.items[2]
        assert isinstance(outer_if, SourceIfStatementNode)
        assert isinstance(outer_if.then, SourceContinueNode)
        assert outer_if.then.label == "while.main.0"


class TestDowhileLabelling:
    def test_simple(self):
        c_str = """
        int main( void ) {
            int a = 0;
            int b = 2;
            do {
                if( a == 2) continue;
                if( b > 120) break;
                b = b * 2;
                a = a + 1;
            } while ( a< 10 );
            return b;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        # We don't need to do variable resolution to test

        label_loops_function(func)
        assert len(func.body.items) == 4

        do_stmt = func.body.items[2]
        assert isinstance(do_stmt, SourceDoWhileNode)
        assert do_stmt.label == "do.main.0"

        assert isinstance(do_stmt.body, SourceCompoundNode)
        assert len(do_stmt.body.block.items) == 4
        if_cont = do_stmt.body.block.items[0]
        assert isinstance(if_cont, SourceIfStatementNode)
        assert isinstance(if_cont.then, SourceContinueNode)
        assert if_cont.then.label == "do.main.0"
        if_break = do_stmt.body.block.items[1]
        assert isinstance(if_break, SourceIfStatementNode)
        assert isinstance(if_break.then, SourceBreakNode)
        assert if_break.then.label == "do.main.0"


class TestForLabelling:
    def test_simple(self):
        c_str = """
        int main( void ) {
            int a =0;
            for( ; a<10; a=a+1) continue;
            return a;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        func = parse_function(token_tape)
        assert token_tape.tokens_remaining == 0

        # We don't need to do variable resolution to test

        label_loops_function(func)
        assert len(func.body.items) == 3

        for_stmt = func.body.items[1]
        assert isinstance(for_stmt, SourceForNode)
        assert for_stmt.label == "for.main.0"

        assert isinstance(for_stmt.body, SourceContinueNode)
        assert for_stmt.body.label == "for.main.0"