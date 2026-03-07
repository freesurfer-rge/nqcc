from typing import get_args

from nqcc.parser import (
    SourceComplementNode,
    SourceConstantIntNode,
    SourceExpressionNode,
    SourceNegateNode,
    SourceUnaryExpressionNode,
)

from ._tacky_ast import (
    TackyComplementNode,
    TackyConstantIntNode,
    TackyInstruction,
    TackyNegateNode,
    TackyUnaryNode,
    TackyValue,
    TackyVarNode,
)


class TackyGenerator:
    def __init__(self):
        self._nxt_tmp = 0
        self._curr_function = ""
        self._current_instructions: list[TackyInstruction] = []

    def get_function_temporary(self) -> str:
        result = f"tmp.{self._curr_function}.{self._nxt_tmp}"
        self._nxt_tmp += 1
        return result

    def convert_constant_int(self, source: SourceConstantIntNode) -> TackyConstantIntNode:
        assert isinstance(source, SourceConstantIntNode)
        return TackyConstantIntNode(start_position=source.start_position, value=source.value)

    def convert_unary_operator(self, source: SourceUnaryExpressionNode) -> TackyUnaryNode:
        match source:
            case SourceComplementNode():
                return TackyComplementNode(start_position=source.start_position)
            case SourceNegateNode():
                return TackyNegateNode(start_position=source.start_position)
            case _:
                raise ValueError(f"Unrecognised: {source}")

    def emit_expression(self, source_node: SourceExpressionNode) -> TackyValue:
        match source_node:
            case SourceConstantIntNode():
                return self.convert_constant_int(source_node)
            case t if isinstance(t, get_args(SourceUnaryExpressionNode)):
                src = self.emit_expression(source_node.expression)
                dst = TackyVarNode(
                    start_position=source_node.start_position,
                    identifier=self.get_function_temporary(),
                )
                tacky_operator = self.convert_unary_operator(source_node)
                instr = TackyUnaryNode(
                    start_position=source_node.start_position,
                    oeprator=tacky_operator,
                    src=src,
                    dst=dst,
                )
                self._current_instructions.append(instr)
            case _:
                raise ValueError(f"Unrecognised: {source_node}")
