from typing import get_args

from nqcc.parser import (
    SourceBlockItemNode,
    SourceBlockNode,
    SourceBreakNode,
    SourceCompoundNode,
    SourceContinueNode,
    SourceDoWhileNode,
    SourceForNode,
    SourceFunctionNode,
    SourceIfStatementNode,
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
        label = f"{LABEL_MAP[type(stmt)]}.{self._func_name}.{self._nxt_loop}"
        self._nxt_loop += 1
        return label

    def label_statement(self, stmt: SourceStatementNode, current_label: str) -> None:
        assert isinstance(stmt, get_args(SourceStatementNode))

        match stmt:
            case SourceBreakNode() | SourceContinueNode():
                if not current_label:
                    raise SemanticAnalysisOutsideLoop(stmt=stmt)
                stmt.label = current_label
            case SourceCompoundNode():
                self.label_block(stmt.block, current_label)
            case SourceIfStatementNode():
                self.label_statement(stmt.then, current_label)
                if stmt.otherwise is not None:
                    self.label_statement(stmt.otherwise, current_label)
            case SourceWhileNode():
                loop_label = self.get_loop_label(stmt)
                self.label_statement(stmt.body, loop_label)
                stmt.label = loop_label

            case _:
                # We're modifying in place and don't need to worry about other types
                pass

    def label_block(self, block: SourceBlockNode, current_label: str) -> None:
        assert isinstance(block, SourceBlockNode)

        for item in block.items:
            self.label_blockitem(item, current_label)

    def label_blockitem(self, bi: SourceBlockItemNode, current_label: str) -> None:
        assert isinstance(bi, get_args(SourceBlockItemNode))

        if isinstance(bi, get_args(SourceStatementNode)):
            self.label_statement(bi, current_label)


def label_loops_function(func: SourceFunctionNode) -> None:
    # Note that this (and everything else) updates in-place
    assert isinstance(func, SourceFunctionNode)

    labeller = LoopLabeller(function_name=func.identifier)
    labeller.label_block(func.body, "")
