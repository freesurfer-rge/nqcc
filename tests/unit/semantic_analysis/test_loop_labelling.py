import pytest

from nqcc.parser import SourceBreakNode, SourceContinueNode
from nqcc.semantic_analysis import LoopLabeller, SemanticAnalysisOutsideLoop


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
