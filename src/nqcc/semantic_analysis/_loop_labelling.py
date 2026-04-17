from typing import get_args

from nqcc.parser import (
    SourceBreakNode,
    SourceContinueNode,
    SourceDoWhileNode,
    SourceForNode,
    SourceStatementNode,
    SourceWhileNode,
)

from ._exceptions import SemanticAnalysisOutsideLoop

LABEL_MAP = {SourceForNode: "for", SourceWhileNode: "while", SourceDoWhileNode: "do"}


class LoopLabeller:
    def __init__(self, *, function_name: str) -> None:
        self._func_name = function_name
        self._nxt_loop = 0

    def get_loop_label(self, stmt: SourceForNode | SourceWhileNode | SourceDoWhileNode) -> str:
        label = f"{LABEL_MAP[type(stmt)]}_{self._func_name}_{self._nxt_loop}"
        self._nxt_loop += 1
        return label

    def label_statement(self, stmt: SourceStatementNode, current_label: str) -> SourceStatementNode:
        assert isinstance(stmt, get_args(SourceStatementNode))

        match stmt:
            case SourceBreakNode() | SourceContinueNode():
                if not current_label:
                    raise SemanticAnalysisOutsideLoop(stmt=stmt)
                stmt.label = current_label
                return stmt
