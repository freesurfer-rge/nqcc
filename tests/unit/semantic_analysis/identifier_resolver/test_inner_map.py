from nqcc.semantic_analysis import (
    IdentifierInfo,
    make_inner_identifier_map,
)


class TestInnerMap:
    def test_smoke(self):
        inner = {
            "a": IdentifierInfo(name="a.0", from_current_scope=True, has_linkage=True),
            "b": IdentifierInfo(name="b.1", from_current_scope=False, has_linkage=False),
        }

        result = make_inner_identifier_map(inner)
        assert len(result) == 2
        assert result["a"] == IdentifierInfo(name="a.0", from_current_scope=False, has_linkage=True)
        assert result["b"] == IdentifierInfo(name="b.1", from_current_scope=False, has_linkage=False)
