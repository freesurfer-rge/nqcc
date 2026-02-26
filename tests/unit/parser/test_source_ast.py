from nqcc.lexer import ConstantIntegerToken, KeywordToken, SemicolonToken, Lexer
from nqcc.parser import (
    SourceConstantIntNode,
    SourceExpressionNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceFunctionDefinitionNode,
    TokenTape,
)


class TestSourceExpressionNode:
    def test_constant_integer(self):
        tokens = [
            ConstantIntegerToken(start_position=1, value="123"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = SourceExpressionNode.parse_token_tape(token_tape)
        assert isinstance(node, SourceConstantIntNode)
        assert node.start_position == 1
        assert node.value == 123

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1

    def test_return_statement(self):
        tokens = [
            KeywordToken(start_position=0, value="return"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = SourceStatementNode.parse_token_tape(token_tape)

        assert isinstance(node, SourceReturnNode)
        assert node.start_position == 0
        assert isinstance(node.value, SourceConstantIntNode)
        sen: SourceConstantIntNode = node.value
        assert sen.start_position == 1
        assert sen.value == 321

        assert token_tape.tokens_remaining == 0

    def test_function(self):
        program_str = "int main( void ) { return 2;}"
        lexer = Lexer()
        for c in program_str:
            lexer.push_character(c)
        lexer.character_stream_done()
        lexer.completed_token_list

        # Sanity check the tokens
        assert len(lexer.completed_token_list) == 10

        token_tape = TokenTape(lexer.completed_token_list)

        node = SourceFunctionDefinitionNode.parse_token_tape(token_tape)
        print(node.model_dump_json(indent=2))
        assert False