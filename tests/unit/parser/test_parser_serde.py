from nqcc.parser import SourceProgramNode, TokenTape, parse_program


class TestParserSerde:
    def test_simple(self):
        source = " int main(void) {return - (~   566);}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        json_str = src_node.model_dump_json()

        restored = SourceProgramNode.model_validate_json(json_str)

        assert restored == src_node
