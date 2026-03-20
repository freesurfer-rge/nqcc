from nqcc.parser import (
    SourceAdd,
    SourceBinaryExpressionNode,
    SourceBinaryOperator,
    SourceComplement,
    SourceConstantIntNode,
    SourceDivide,
    SourceExpressionNode,
    SourceFunctionNode,
    SourceModulo,
    SourceMultiply,
    SourceNegate,
    SourceProgramNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceSubtract,
    SourceUnaryExpressionNode,
    SourceUnaryOperator,
)

from ._tacky_ast import (
    TackyAdd,
    TackyBinaryNode,
    TackyBinaryOperator,
    TackyComplement,
    TackyConstantIntNode,
    TackyDivide,
    TackyFunctionNode,
    TackyInstruction,
    TackyModulo,
    TackyMultiply,
    TackyNegate,
    TackyProgramNode,
    TackyReturnNode,
    TackySubtract,
    TackyUnaryNode,
    TackyUnaryOperator,
    TackyValue,
    TackyVarNode,
)


class TackyGenerator:
    def __init__(self) -> None:
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

    def convert_unary_operator(self, source: SourceUnaryOperator) -> TackyUnaryOperator:
        match source:
            case SourceComplement():
                return TackyComplement(start_position=source.start_position)
            case SourceNegate():
                return TackyNegate(start_position=source.start_position)
            case _:
                raise ValueError(f"Unrecognised: {source}")

    def convert_binary_operator(self, source: SourceBinaryOperator) -> TackyBinaryOperator:
        match source:
            case SourceAdd():
                return TackyAdd(start_position=source.start_position)
            case SourceSubtract():
                return TackySubtract(start_position=source.start_position)
            case SourceMultiply():
                return TackyMultiply(start_position=source.start_position)
            case SourceDivide():
                return TackyDivide(start_position=source.start_position)
            case SourceModulo():
                return TackyModulo(start_position=source.start_position)
            case _:
                raise ValueError(f"Unrecognised: {source}")

    def emit_expression(self, source_node: SourceExpressionNode) -> TackyValue:
        match source_node:
            case SourceConstantIntNode():
                return self.convert_constant_int(source_node)
            case SourceUnaryExpressionNode():
                src = self.emit_expression(source_node.expression)
                dst = TackyVarNode(
                    start_position=source_node.start_position,
                    identifier=self.get_function_temporary(),
                )
                tacky_operator = self.convert_unary_operator(source_node.operator)
                instr = TackyUnaryNode(
                    start_position=source_node.start_position,
                    operator=tacky_operator,
                    src=src,
                    dst=dst,
                )
                self._current_instructions.append(instr)
                return dst
            case SourceBinaryExpressionNode():
                # Note that the C standard does not guarantee
                # ordering here
                l_val = self.emit_expression(source_node.left)
                r_val = self.emit_expression(source_node.right)
                dst_b = TackyVarNode(
                    start_position=source_node.start_position,
                    identifier=self.get_function_temporary(),
                )
                bin_operator = self.convert_binary_operator(source_node.operator)
                bin_instr = TackyBinaryNode(
                    start_position=source_node.start_position,
                    operator=bin_operator,
                    left=l_val,
                    right=r_val,
                    dst=dst_b,
                )
                self._current_instructions.append(bin_instr)
                return dst_b
            case _:
                raise ValueError(f"Unrecognised: {source_node}")

    def emit_statement(self, source_node: SourceStatementNode):
        match source_node:
            case SourceReturnNode():
                src = self.emit_expression(source_node.value)
                instr = TackyReturnNode(start_position=source_node.start_position, value=src)
                self._current_instructions.append(instr)
            case _:
                raise ValueError(f"Unrecognised: {source_node}")

    def emit_function(self, source_node: SourceFunctionNode) -> TackyFunctionNode:
        assert isinstance(source_node, SourceFunctionNode)

        # Set up internal state
        self._nxt_tmp = 0
        self._curr_function = source_node.identifier
        self._current_instructions = []

        # Process the internals
        self.emit_statement(source_node.body)

        return TackyFunctionNode(
            start_position=source_node.start_position,
            identifier=source_node.identifier,
            instructions=self._current_instructions,
        )

    def emit_program(self, source_node: SourceProgramNode) -> TackyProgramNode:
        assert isinstance(source_node, SourceProgramNode)

        func = self.emit_function(source_node.value)

        return TackyProgramNode(start_position=0, function_definition=func)
