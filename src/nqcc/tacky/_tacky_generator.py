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
    SourceBlockNode,
    SourceBreakNode,
    SourceComplement,
    SourceCompoundNode,
    SourceConstantIntNode,
    SourceContinueNode,
    SourceDeclarationNode,
    SourceDivide,
    SourceDoWhileNode,
    SourceEqualTo,
    SourceExpressionNode,
    SourceExpressionStatementNode,
    SourceFunctionNode,
    SourceGreaterThan,
    SourceGreaterThanOrEqual,
    SourceIfStatementNode,
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
    SourceNullStatementNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceRightShift,
    SourceStatementNode,
    SourceSubtract,
    SourceTernaryExpressonNode,
    SourceUnaryExpressionNode,
    SourceUnaryOperator,
    SourceVarNode,
    SourceWhileNode,
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


def get_start_label(loop_label: str) -> str:
    return f"start_{loop_label}"


def get_break_label(loop_label: str) -> str:
    return f"break_{loop_label}"


def get_continue_label(loop_label: str) -> str:
    return f"continue_{loop_label}"


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

    def emit_ternary(self, source_node: SourceTernaryExpressonNode) -> TackyValue:
        assert isinstance(source_node, SourceTernaryExpressonNode)
        OTHERWISE_LABEL = "ternaryotherwise"
        END_LABEL = "ternaryend"
        otherwise_label = TackyLabelNode(
            start_position=source_node.start_position,
            identifier=self.get_function_label(OTHERWISE_LABEL),
        )
        end_label = TackyLabelNode(
            start_position=source_node.start_position, identifier=self.get_function_label(END_LABEL)
        )
        result_var = TackyVarNode(
            start_position=source_node.start_position,
            identifier=self.get_function_temporary(),
        )

        # Evaluate the condition
        cond_val = self.emit_expression(source_node.condition)
        # See if we should jump
        jmp0 = TackyJumpIfZeroNode(
            start_position=source_node.start_position,
            target=otherwise_label.identifier,
            condition=cond_val,
        )
        self._current_instructions.append(jmp0)

        # Run 'then'
        then_val = self.emit_expression(source_node.then)
        copy_then_result = TackyCopyNode(
            start_position=source_node.start_position,
            src=then_val,
            dst=result_var,
        )
        self._current_instructions.append(copy_then_result)
        jmp_end = TackyJumpNode(
            start_position=source_node.start_position, target=end_label.identifier
        )
        self._current_instructions.append(jmp_end)

        # And 'otherwise'
        self._current_instructions.append(otherwise_label)
        otherwise_val = self.emit_expression(source_node.otherwise)
        copy_otherwise_result = TackyCopyNode(
            start_position=source_node.start_position, src=otherwise_val, dst=result_var
        )
        self._current_instructions.append(copy_otherwise_result)

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
            case SourceTernaryExpressonNode():
                return self.emit_ternary(source_node)
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

    def emit_if_statement(self, source_node: SourceIfStatementNode):
        assert isinstance(source_node, SourceIfStatementNode)
        OTHERWISE_LABEL = "ifotherwise"
        END_LABEL = "ifend"
        otherwise_label = TackyLabelNode(
            start_position=source_node.start_position,
            identifier=self.get_function_label(OTHERWISE_LABEL),
        )
        end_label = TackyLabelNode(
            start_position=source_node.start_position, identifier=self.get_function_label(END_LABEL)
        )

        has_otherwise = source_node.otherwise is not None

        cond_val = self.emit_expression(source_node.condition)
        jmp0 = TackyJumpIfZeroNode(
            start_position=source_node.start_position,
            condition=cond_val,
            target=otherwise_label.identifier if has_otherwise else end_label.identifier,
        )
        self._current_instructions.append(jmp0)
        self.emit_statement(source_node.then)

        if has_otherwise:
            # Assert should never fire, shuts up mypy
            assert source_node.otherwise is not None
            # 'then' has to jump to end
            jmp1 = TackyJumpNode(
                start_position=source_node.start_position, target=end_label.identifier
            )
            self._current_instructions.append(jmp1)

            # Add the 'otherwise' label and instructions
            self._current_instructions.append(otherwise_label)
            self.emit_statement(source_node.otherwise)

        # Finally end the if block
        self._current_instructions.append(end_label)

    def emit_while_statement(self, source_node: SourceWhileNode):
        assert isinstance(source_node, SourceWhileNode)

        cont_label = TackyLabelNode(
            start_position=source_node.start_position,
            identifier=get_continue_label(source_node.label),
        )
        self._current_instructions.append(cont_label)

        cond_val = self.emit_expression(source_node.condition)
        jump_condition = TackyJumpIfZeroNode(
            start_position=source_node.condition.start_position,
            target=get_break_label(source_node.label),
            condition=cond_val,
        )
        self._current_instructions.append(jump_condition)

        self.emit_statement(source_node.body)

        jump_continue = TackyJumpNode(
            start_position=source_node.start_position, target=get_continue_label(source_node.label)
        )
        self._current_instructions.append(jump_continue)

        break_label = TackyLabelNode(
            start_position=source_node.start_position, identifier=get_break_label(source_node.label)
        )
        self._current_instructions.append(break_label)

    def emit_dowhile_statement(self, source_node: SourceDoWhileNode):
        assert isinstance(source_node, SourceDoWhileNode)

        start_label = TackyLabelNode(
            start_position=source_node.start_position, identifier=get_start_label(source_node.label)
        )
        self._current_instructions.append(start_label)

        self.emit_statement(source_node.body)

        cont_label = TackyLabelNode(
            start_position=source_node.start_position,
            identifier=get_continue_label(source_node.label),
        )
        self._current_instructions.append(cont_label)

        cond_val = self.emit_expression(source_node.condition)
        jump_condition = TackyJumpIfNotZeroNode(
            start_position=source_node.condition.start_position,
            target=get_start_label(source_node.label),
            condition=cond_val,
        )
        self._current_instructions.append(jump_condition)

        break_label = TackyLabelNode(
            start_position=source_node.start_position, identifier=get_break_label(source_node.label)
        )
        self._current_instructions.append(break_label)

    def emit_statement(self, source_node: SourceStatementNode):
        assert isinstance(source_node, get_args(SourceStatementNode))
        match source_node:
            case SourceNullStatementNode():
                return
            case SourceExpressionStatementNode():
                self.emit_expression(source_node.value)
            case SourceReturnNode():
                src = self.emit_expression(source_node.value)
                ret_instr = TackyReturnNode(start_position=source_node.start_position, value=src)
                self._current_instructions.append(ret_instr)
            case SourceIfStatementNode():
                self.emit_if_statement(source_node)
            case SourceCompoundNode():
                self.emit_block(source_node.block)
            case SourceBreakNode():
                break_instr = TackyJumpNode(
                    start_position=source_node.start_position,
                    target=get_break_label(source_node.label),
                )
                self._current_instructions.append(break_instr)
            case SourceContinueNode():
                continue_instr = TackyJumpNode(
                    start_position=source_node.start_position,
                    target=get_continue_label(source_node.label),
                )
                self._current_instructions.append(continue_instr)
            case SourceWhileNode():
                self.emit_while_statement(source_node)
            case SourceDoWhileNode():
                self.emit_dowhile_statement(source_node)
            case _:
                raise ValueError(f"Unrecognised: {source_node}")

    def emit_blockitem(self, source_node: SourceBlockItemNode):
        assert isinstance(source_node, get_args(SourceBlockItemNode))
        match source_node:
            case _ if isinstance(source_node, get_args(SourceStatementNode)):
                self.emit_statement(source_node)
            case _ if isinstance(source_node, SourceDeclarationNode):
                if source_node.initial is None:
                    return
                src_decl = self.emit_expression(source_node.initial)
                dst_decl = self.emit_expression(source_node.identifier)
                tacky_copy = TackyCopyNode(
                    start_position=source_node.start_position, src=src_decl, dst=dst_decl
                )
                self._current_instructions.append(tacky_copy)
            case _:
                raise ValueError(f"Unrecognised blockitem: {source_node}")

    def emit_block(self, source_node: SourceBlockNode):
        assert isinstance(source_node, SourceBlockNode)
        for block_item in source_node.items:
            self.emit_blockitem(block_item)

    def emit_function(self, source_node: SourceFunctionNode) -> TackyFunctionNode:
        assert isinstance(source_node, SourceFunctionNode)

        # Set up internal state
        self._nxt_tmp = 0
        self._nxt_lbl = 0
        self._curr_function = source_node.identifier
        self._current_instructions = []

        # Process the internals
        self.emit_block(source_node.body)

        # What if there's no return statement?
        # We add an extra; this will not run if there is
        # a return
        # See "Functions with no return statement" in CH 5
        self._current_instructions.append(
            TackyReturnNode(start_position=0, value=TackyConstantIntNode(start_position=0, value=0))
        )

        return TackyFunctionNode(
            start_position=source_node.start_position,
            identifier=source_node.identifier,
            instructions=self._current_instructions,
        )

    def emit_program(self, source_node: SourceProgramNode) -> TackyProgramNode:
        assert isinstance(source_node, SourceProgramNode)

        func = self.emit_function(source_node.value)

        return TackyProgramNode(start_position=0, function_definition=func)
