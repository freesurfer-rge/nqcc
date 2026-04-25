from nqcc.semantic_analysis import (
    IdentifierInfo,
    make_inner_variable_map,
)


class TestInnerMap:
    def test_smoke(self):
        inner = {
            "a": IdentifierInfo(name="a.0", defined_in_block=True),
            "b": IdentifierInfo(name="b.1", defined_in_block=False),
        }

        result = make_inner_variable_map(inner)
        assert len(result) == 2
        assert result["a"] == IdentifierInfo(name="a.0", defined_in_block=False)
        assert result["b"] == IdentifierInfo(name="b.1", defined_in_block=False)
