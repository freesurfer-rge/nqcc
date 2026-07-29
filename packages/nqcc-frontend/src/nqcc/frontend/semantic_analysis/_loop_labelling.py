from nqcc.frontend._type_guards import is_block_item, is_statement
from nqcc.frontend.parser import (
    SourceBlockItemNode,
    SourceBlockNode,
    SourceBreakNode,
    SourceCompoundNode,
    SourceContinueNode,
    SourceDoWhileNode,
    SourceExpressionStatementNode,
    SourceForNode,
    SourceFunctionDeclarationNode,
    SourceIfStatementNode,
    SourceNullStatementNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceVariableDeclarationNode,
    SourceWhileNode,
)

from ._exceptions import SemanticAnalysisOutsideLoop

LABEL_MAP = {SourceForNode: "for", SourceWhileNode: "while", SourceDoWhileNode: "do"}


# Note that in this file, we do in-place updates
# Unlike the variable resolver, we only have to deal with a subset of the statements
# so we can do a simpler in-place update


class LoopLabeller:
    def __init__(self, *, function_name: str) -> None:
        self._func_name = function_name
        self._nxt_loop = 0

    def get_loop_label(self, stmt: SourceForNode | SourceWhileNode | SourceDoWhileNode) -> str:
        if isinstance(stmt, SourceForNode):
            loop_type = "for"
        elif isinstance(stmt, SourceWhileNode):
            loop_type = "while"
        else:
            loop_type = "do"
        label = f"{loop_type}.{self._func_name}.{self._nxt_loop}"
        self._nxt_loop += 1
        return label

    def label_statement(self, stmt: SourceStatementNode, current_label: str) -> None:
        assert is_statement(stmt)

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
            case SourceDoWhileNode():
                loop_label = self.get_loop_label(stmt)
                self.label_statement(stmt.body, loop_label)
                stmt.label = loop_label
            case SourceForNode():
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
        assert is_block_item(bi)

        if is_statement(bi):
            self.label_statement(bi, current_label)


def label_loops_function(func: SourceFunctionDeclarationNode) -> None:
    # Note that this (and everything else) updates in-place
    assert isinstance(func, SourceFunctionDeclarationNode)

    if not func.body:
        return

    labeller = LoopLabeller(function_name=func.identifier)
    labeller.label_block(func.body, "")


def label_loops_program(prog: SourceProgramNode) -> None:
    # An in-place update
    assert isinstance(prog, SourceProgramNode)

    for decl in prog.declarations:
        if isinstance(decl, SourceFunctionDeclarationNode):
            label_loops_function(decl)
