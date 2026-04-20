from nqcc.parser import (
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceBlockNode,
    SourceCompoundNode,
    SourceConstantIntNode,
    SourceExpressionStatementNode,
    SourceGreaterThan,
    SourceIfStatementNode,
    SourceReturnNode,
    SourceVarNode,
    TokenTape,
    parse_statement,
)


class TestSourceIfStatementNode:
    def test_simple(self):
        # Have extra semicolon to ensure we don't run out of tokens
        c_str = "if( a ) b=1; ;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 9

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceExpressionStatementNode)
        assert isinstance(node.then.value, SourceAssignmentNode)
        assert isinstance(node.then.value.left, SourceVarNode)
        assert node.then.value.left.identifier == "b"
        assert isinstance(node.then.value.right, SourceConstantIntNode)
        assert node.then.value.right.value == 1

        assert node.otherwise is None

        # Should not have touched the extra semicolon
        assert token_tape.tokens_remaining == 1

    def test_with_else(self):
        c_str = "if( a ) b=1; else c=2;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 13

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceExpressionStatementNode)
        assert isinstance(node.then.value, SourceAssignmentNode)
        assert isinstance(node.then.value.left, SourceVarNode)
        assert node.then.value.left.identifier == "b"
        assert isinstance(node.then.value.right, SourceConstantIntNode)
        assert node.then.value.right.value == 1

        assert isinstance(node.otherwise, SourceExpressionStatementNode)
        assert isinstance(node.otherwise.value, SourceAssignmentNode)
        assert isinstance(node.otherwise.value.left, SourceVarNode)
        assert node.otherwise.value.left.identifier == "c"
        assert isinstance(node.otherwise.value.right, SourceConstantIntNode)
        assert node.otherwise.value.right.value == 2

        # Should have consumed everything
        assert token_tape.tokens_remaining == 0

    def test_nested(self):
        # Again, tag an extra semicolon onto the end
        c_str = """if (a)
        if( a>10 )
           return a;
        else
           return b;

        ;
        """
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 18

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceIfStatementNode)
        assert node.otherwise is None
        inner = node.then
        assert isinstance(inner.condition, SourceBinaryExpressionNode)
        assert isinstance(inner.condition.operator, SourceGreaterThan)
        assert isinstance(inner.condition.left, SourceVarNode)
        assert inner.condition.left.identifier == "a"
        assert isinstance(inner.condition.right, SourceConstantIntNode)
        assert inner.condition.right.value == 10

        assert isinstance(inner.then, SourceReturnNode)
        assert isinstance(inner.then.value, SourceVarNode)
        assert inner.then.value.identifier == "a"
        assert isinstance(inner.otherwise, SourceReturnNode)
        assert isinstance(inner.otherwise.value, SourceVarNode)
        assert inner.otherwise.value.identifier == "b"

    def test_braced(self):
        # Again, tag an extra semicolon onto the end
        c_str = """if (a) {
            return a;
        } else {
            return b;
        }
        """
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 15

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceCompoundNode)
        assert isinstance(node.then.block, SourceBlockNode)
        assert len(node.then.block.items) == 1
        assert node.then.block.items[0] == SourceReturnNode(
            start_position=21, value=SourceVarNode(start_position=28, identifier="a")
        )

        assert isinstance(node.otherwise, SourceCompoundNode)
        assert isinstance(node.otherwise.block, SourceBlockNode)
        assert len(node.otherwise.block.items) == 1
        assert node.otherwise.block.items[0] == SourceReturnNode(
            start_position=60, value=SourceVarNode(start_position=67, identifier="b")
        )
