from typing import Type, get_args

from nqcc.parser import (
    SourceAdd,
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceBinaryOperator,
    SourceBitwiseAnd,
    SourceBitwiseOr,
    SourceBitwiseXor,
    SourceBlockItemNode,
    SourceComplement,
    SourceConstantIntNode,
    SourceDivide,
    SourceEqualTo,
    SourceExpressionNode,
    SourceFunctionNode,
    SourceGreaterThan,
    SourceGreaterThanOrEqual,
    SourceLeftShift,
    SourceLessThan,
    SourceLessThanOrEqual,
    SourceLogicalAnd,
    SourceLogicalNot,
    SourceLogicalOr,
    SourceModulo,
    SourceMultiply,
    SourceNegate,
    SourceNotEqualTo,
    SourceProgramNode,
    SourceReturnNode,
    SourceRightShift,
    SourceSubtract,
    SourceUnaryExpressionNode,
    SourceUnaryOperator,
    SourceVarNode,SourceStatementNode
)

from ._tacky_ast import (
    TackyAdd,
    TackyBinaryNode,
    TackyBinaryOperator,
    TackyBitwiseAnd,
    TackyBitwiseOr,
    TackyBitwiseXor,
    TackyComplement,
    TackyConstantIntNode,
    TackyCopyNode,
    TackyDivide,
    TackyEqualTo,
    TackyFunctionNode,
    TackyGreaterThan,
    TackyGreaterThanOrEqual,
    TackyInstruction,
    TackyJumpIfNotZeroNode,
    TackyJumpIfZeroNode,
    TackyJumpNode,
    TackyLabelNode,
    TackyLeftShift,
    TackyLessThan,
    TackyLessThanOrEqual,
    TackyLogicalNot,
    TackyModulo,
    TackyMultiply,
    TackyNegate,
    TackyNotEqualTo,
    TackyProgramNode,
    TackyReturnNode,
    TackyRightShift,
    TackySubtract,
    TackyUnaryNode,
    TackyUnaryOperator,
    TackyValue,
    TackyVarNode,
)

_UNARY_OPERATOR_MAP: dict[Type[SourceUnaryOperator], Type[TackyUnaryOperator]] = {
    SourceComplement: TackyComplement,
    SourceNegate: TackyNegate,
    SourceLogicalNot: TackyLogicalNot,
}

_BINARY_OPERATOR_MAP: dict[Type[SourceBinaryOperator], Type[TackyBinaryOperator]] = {
    SourceAdd: TackyAdd,
    SourceSubtract: TackySubtract,
    SourceMultiply: TackyMultiply,
    SourceDivide: TackyDivide,
    SourceModulo: TackyModulo,
    SourceBitwiseAnd: TackyBitwiseAnd,
    SourceBitwiseOr: TackyBitwiseOr,
    SourceBitwiseXor: TackyBitwiseXor,
    SourceLeftShift: TackyLeftShift,
    SourceRightShift: TackyRightShift,
    SourceEqualTo: TackyEqualTo,
    SourceNotEqualTo: TackyNotEqualTo,
    SourceLessThan: TackyLessThan,
    SourceLessThanOrEqual: TackyLessThanOrEqual,
    SourceGreaterThan: TackyGreaterThan,
    SourceGreaterThanOrEqual: TackyGreaterThanOrEqual,
}


class TackyGenerator:
    def __init__(self) -> None:
        self._nxt_tmp = 0
        self._nxt_lbl = 0
        self._curr_function = ""
        self._current_instructions: list[TackyInstruction] = []

    def get_function_temporary(self) -> str:
        result = f"tmp.{self._curr_function}.{self._nxt_tmp}"
        self._nxt_tmp += 1
        return result

    def get_function_label(self, source_reference: str) -> str:
        result = f"label.{self._curr_function}.{source_reference}.{self._nxt_lbl}"
        self._nxt_lbl += 1
        return result

    def convert_constant_int(self, source: SourceConstantIntNode) -> TackyConstantIntNode:
        assert isinstance(source, SourceConstantIntNode)
        return TackyConstantIntNode(start_position=source.start_position, value=source.value)

    def convert_unary_operator(self, source: SourceUnaryOperator) -> TackyUnaryOperator:
        if type(source) not in _UNARY_OPERATOR_MAP:
            raise ValueError(f"Unrecognised unary: {source}")

        op_type = _UNARY_OPERATOR_MAP[type(source)]
        return op_type(start_position=source.start_position)

    def convert_binary_operator(self, source: SourceBinaryOperator) -> TackyBinaryOperator:
        if type(source) not in _BINARY_OPERATOR_MAP:
            raise ValueError(f"Unrecognised binary: {source}")

        op_type = _BINARY_OPERATOR_MAP[type(source)]
        return op_type(start_position=source.start_position)

    def emit_logical_and(self, source_node: SourceBinaryExpressionNode) -> TackyValue:
        assert isinstance(source_node, SourceBinaryExpressionNode)
        assert isinstance(source_node.operator, SourceLogicalAnd)
        FALSE_LABEL = "logicalandfalse"
        END_LABEL = "logicalandend"
        false_label = TackyLabelNode(
            start_position=source_node.start_position,
            identifier=self.get_function_label(FALSE_LABEL),
        )
        end_label = TackyLabelNode(
            start_position=source_node.start_position, identifier=self.get_function_label(END_LABEL)
        )
        result_var = TackyVarNode(
            start_position=source_node.start_position,
            identifier=self.get_function_temporary(),
        )

        # Evaluate left and short circuit
        l_val = self.emit_expression(source_node.left)
        jmp0 = TackyJumpIfZeroNode(
            start_position=source_node.start_position,
            target=false_label.identifier,
            condition=l_val,
        )
        self._current_instructions.append(jmp0)

        # Evaluate right, and jump if needed
        r_val = self.emit_expression(source_node.right)
        jmp1 = TackyJumpIfZeroNode(
            start_position=source_node.start_position,
            target=false_label.identifier,
            condition=r_val,
        )
        self._current_instructions.append(jmp1)

        # If we get here, && evaluated to True
        copy_true_result = TackyCopyNode(
            start_position=source_node.start_position,
            src=TackyConstantIntNode(start_position=source_node.start_position, value=1),
            dst=result_var,
        )
        self._current_instructions.append(copy_true_result)
        jmp_end = TackyJumpNode(
            start_position=source_node.start_position, target=end_label.identifier
        )
        self._current_instructions.append(jmp_end)

        # Now handle the case where && evaluated to false
        self._current_instructions.append(false_label)
        copy_false_result = TackyCopyNode(
            start_position=source_node.start_position,
            src=TackyConstantIntNode(start_position=source_node.start_position, value=0),
            dst=result_var,
        )
        self._current_instructions.append(copy_false_result)

        self._current_instructions.append(end_label)
        return result_var

    def emit_logical_or(self, source_node: SourceBinaryExpressionNode) -> TackyValue:
        assert isinstance(source_node, SourceBinaryExpressionNode)
        assert isinstance(source_node.operator, SourceLogicalOr)
        TRUE_LABEL = "logicalortrue"
        END_LABEL = "logicalorend"
        true_label = TackyLabelNode(
            start_position=source_node.start_position,
            identifier=self.get_function_label(TRUE_LABEL),
        )
        end_label = TackyLabelNode(
            start_position=source_node.start_position, identifier=self.get_function_label(END_LABEL)
        )
        result_var = TackyVarNode(
            start_position=source_node.start_position,
            identifier=self.get_function_temporary(),
        )

        # Evaluate left and short circuit if we can
        l_val = self.emit_expression(source_node.left)
        jmp0 = TackyJumpIfNotZeroNode(
            start_position=source_node.start_position,
            target=true_label.identifier,
            condition=l_val,
        )
        self._current_instructions.append(jmp0)

        # Evaluate right, and jump if needed
        r_val = self.emit_expression(source_node.right)
        jmp1 = TackyJumpIfNotZeroNode(
            start_position=source_node.start_position,
            target=true_label.identifier,
            condition=r_val,
        )
        self._current_instructions.append(jmp1)

        # If we get here, || evaluated to False
        copy_false_result = TackyCopyNode(
            start_position=source_node.start_position,
            src=TackyConstantIntNode(start_position=source_node.start_position, value=0),
            dst=result_var,
        )
        self._current_instructions.append(copy_false_result)
        jmp_end = TackyJumpNode(
            start_position=source_node.start_position, target=end_label.identifier
        )
        self._current_instructions.append(jmp_end)

        # Now handle the case where || evaluated to True
        self._current_instructions.append(true_label)
        copy_true_result = TackyCopyNode(
            start_position=source_node.start_position,
            src=TackyConstantIntNode(start_position=source_node.start_position, value=1),
            dst=result_var,
        )
        self._current_instructions.append(copy_true_result)

        self._current_instructions.append(end_label)
        return result_var

    def emit_expression(self, source_node: SourceExpressionNode) -> TackyValue:
        assert isinstance(source_node, get_args(SourceExpressionNode))
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
                # First check for short circuiting
                if isinstance(source_node.operator, SourceLogicalAnd):
                    return self.emit_logical_and(source_node)
                if isinstance(source_node.operator, SourceLogicalOr):
                    return self.emit_logical_or(source_node)
                # If we get to this point, we have a 'regular' operator
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
            case SourceVarNode():
                return TackyVarNode(
                    start_position=source_node.start_position, identifier=source_node.identifier
                )
            case SourceAssignmentNode():
                result = self.emit_expression(source_node.right)
                assert isinstance(source_node.left, SourceVarNode)
                dst_assign = self.emit_expression(source_node.left)
                tacky_copy = TackyCopyNode(
                    start_position=source_node.start_position, src=result, dst=dst_assign
                )
                self._current_instructions.append(tacky_copy)
                return dst_assign
            case _:
                raise ValueError(f"Unrecognised: {source_node}")

    def emit_statement(self, source_node: SourceStatementNode):
        assert isinstance(source_node, get_args(SourceStatementNode))
        match source_node:
            case SourceReturnNode():
                src = self.emit_expression(source_node.value)
                instr = TackyReturnNode(start_position=source_node.start_position, value=src)
                self._current_instructions.append(instr)
            case _:
                raise ValueError(f"Unrecognised: {source_node}")

    def emit_blockitem(self, source_node: SourceBlockItemNode):
        assert isinstance(source_node, get_args(SourceBlockItemNode))
        match source_node:
            case _ if isinstance(source_node, get_args(SourceStatementNode)):
                self.emit_statement(source_node)
            case _:
                raise ValueError(f"Unrecognised blockitem: {source_node}")

    def emit_function(self, source_node: SourceFunctionNode) -> TackyFunctionNode:
        assert isinstance(source_node, SourceFunctionNode)

        # Set up internal state
        self._nxt_tmp = 0
        self._nxt_lbl = 0
        self._curr_function = source_node.identifier
        self._current_instructions = []

        # Process the internals
        for block_item in source_node.body:
            self.emit_blockitem(block_item)

        return TackyFunctionNode(
            start_position=source_node.start_position,
            identifier=source_node.identifier,
            instructions=self._current_instructions,
        )

    def emit_program(self, source_node: SourceProgramNode) -> TackyProgramNode:
        assert isinstance(source_node, SourceProgramNode)

        func = self.emit_function(source_node.value)

        return TackyProgramNode(start_position=0, function_definition=func)
