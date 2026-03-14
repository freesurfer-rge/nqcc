from nqcc.parser import (
    SourceComplementNode,
    SourceConstantIntNode,
    SourceExpressionNode,
    SourceFunctionNode,
    SourceNegateNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceUnaryExpressionNode,
    SourceBinaryOperator, SourceAddOperator, SourceSubtractOperator, SourceDivideOperator, SourceMultiplyOperator, SourceModuloOperator
)

from ._tacky_ast import (
    TackyComplementNode,
    TackyConstantIntNode,
    TackyFunctionNode,
    TackyInstruction,
    TackyNegateNode,
    TackyProgramNode,
    TackyReturnNode,
    TackyUnaryNode,
    TackyUnaryOperator,
    TackyValue,
    TackyVarNode,
    TackyBinaryOperator, TackyAdd, TackySubtract,TackyMultiply, TackyDivide, TackyModulo, TackyBinaryNode
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

    def convert_unary_operator(self, source: SourceUnaryExpressionNode) -> TackyUnaryOperator:
        match source:
            case SourceComplementNode():
                return TackyComplementNode(start_position=source.start_position)
            case SourceNegateNode():
                return TackyNegateNode(start_position=source.start_position)
            case _:
                raise ValueError(f"Unrecognised: {source}")

    def convert_binary_operator(self, source: SourceBinaryOperator) -> TackyBinaryOperator:
        match source:
            case SourceAddOperator():
                return TackyAdd(start_position=source.start_position)
            case SourceSubtractOperator():
                return TackySubtract(start_position=source.start_position)
            case TackyMultiply():
                return TackyMultiply(start_positino=source.start_position)
            case TackyDivide():
                return TackyDivide(start_position=source.start_position)
            case TackyModulo():
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
                tacky_operator = self.convert_unary_operator(source_node)
                instr = TackyUnaryNode(
                    start_position=source_node.start_position,
                    operator=tacky_operator,
                    src=src,
                    dst=dst,
                )
                self._current_instructions.append(instr)
                return dst
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
