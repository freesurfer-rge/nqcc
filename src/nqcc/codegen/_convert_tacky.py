from typing import Type

from nqcc.tacky import (
    TackyAdd,
    TackyBinaryNode,
    TackyBinaryOperator,
    TackyBitwiseAnd,
    TackyBitwiseOr,
    TackyBitwiseXor,
    TackyComplement,
    TackyConstantIntNode,
    TackyDivide,
    TackyFunctionNode,
    TackyInstruction,
    TackyLeftShift,
    TackyModulo,
    TackyMultiply,
    TackyNegate,
    TackyProgramNode,
    TackyReturnNode,
    TackyRightShift,
    TackySubtract,
    TackyUnaryNode,
    TackyUnaryOperator,
    TackyValue,
    TackyVarNode,
)

from ._assembler_ast import (
    AsmAdd,
    AsmBinaryNode,
    AsmBinaryOperator,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmCdqNode,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmLeftShift,
    AsmMovNode,
    AsmMultiply,
    AsmNeg,
    AsmNot,
    AsmOperandNode,
    AsmProgramNode,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmRightShift,
    AsmSubtract,
    AsmUnaryNode,
    AsmUnaryOperator,
)

_UNARY_OPERATOR_MAP: dict[Type, Type] = {
    TackyComplement: AsmNot,
    TackyNegate: AsmNeg,
}

_BINARY_OPERATOR_MAP: dict[Type, Type] = {
    TackyAdd: AsmAdd,
    TackySubtract: AsmSubtract,
    TackyMultiply: AsmMultiply,
    TackyBitwiseAnd: AsmBitwiseAnd,
    TackyBitwiseOr: AsmBitwiseOr,
    TackyBitwiseXor: AsmBitwiseXor,
    TackyLeftShift: AsmLeftShift,
    TackyRightShift: AsmRightShift,
}


def convert_tacky_operand(tacky_value: TackyValue) -> AsmOperandNode:
    match tacky_value:
        case TackyConstantIntNode():
            return AsmImmediateIntNode(
                start_position=tacky_value.start_position, value=tacky_value.value
            )
        case TackyVarNode():
            return AsmPseudoRegisterNode(
                start_position=tacky_value.start_position, identifier=tacky_value.identifier
            )
        case _:
            raise ValueError(f"Unrecognised: {tacky_value}")


def convert_tacky_unary_operator(tacky_operator: TackyUnaryOperator) -> AsmUnaryOperator:
    if type(tacky_operator) not in _UNARY_OPERATOR_MAP:
        raise ValueError(f"Unrecognised unary: {tacky_operator}")

    op_type = _UNARY_OPERATOR_MAP[type(tacky_operator)]
    return op_type(start_position=tacky_operator.start_position)


def convert_tacky_binary_operator(tacky_operator: TackyBinaryOperator) -> AsmBinaryOperator:
    if type(tacky_operator) not in _BINARY_OPERATOR_MAP:
        # Div and Modulo handled separately
        raise ValueError(f"Unrecognised binary: {tacky_operator}")

    op_type = _BINARY_OPERATOR_MAP[type(tacky_operator)]
    return op_type(start_position=tacky_operator.start_position)


def convert_tacky_binary_node(tacky_node: TackyBinaryNode) -> list[AsmInstructionNode]:
    assert isinstance(tacky_node, TackyBinaryNode)

    left = convert_tacky_operand(tacky_node.left)
    right = convert_tacky_operand(tacky_node.right)
    dest = convert_tacky_operand(tacky_node.dst)
    match tacky_node.operator:
        case (
            TackyAdd()
            | TackySubtract()
            | TackyMultiply()
            | TackyBitwiseAnd()
            | TackyBitwiseOr()
            | TackyBitwiseXor()
            | TackyLeftShift()
            | TackyRightShift()
        ):
            asm_bin_op = convert_tacky_binary_operator(tacky_node.operator)
            i0_bin_op = AsmMovNode(start_position=tacky_node.start_position, src=left, dst=dest)
            i1_bin_op = AsmBinaryNode(
                start_position=tacky_node.start_position,
                operator=asm_bin_op,
                src=right,
                dst=i0_bin_op.dst,
            )
            return [i0_bin_op, i1_bin_op]
        case TackyDivide() | TackyModulo():
            div_eax = AsmRegisterNode(start_position=tacky_node.start_position, value="eax")
            i0_div_op = AsmMovNode(
                start_position=tacky_node.start_position,
                src=left,
                dst=div_eax,
            )
            i1_div_op = AsmCdqNode(start_position=tacky_node.start_position)
            i2_div_op = AsmIDivNode(start_position=tacky_node.start_position, src=right)
            if isinstance(tacky_node.operator, TackyDivide):
                result_register = div_eax
            else:
                # Modulo
                result_register = AsmRegisterNode(
                    start_position=tacky_node.start_position, value="edx"
                )
            i4_div_op = AsmMovNode(
                start_position=tacky_node.start_position, src=result_register, dst=dest
            )
            return [i0_div_op, i1_div_op, i2_div_op, i4_div_op]
        case _:
            raise ValueError(f"Unrecognised: {tacky_node.operator}")


def convert_tacky_instruction(tacky_instruction: TackyInstruction) -> list[AsmInstructionNode]:
    sp = tacky_instruction.start_position
    match tacky_instruction:
        case TackyReturnNode():
            src_ret = convert_tacky_operand(tacky_instruction.value)
            dst_ret = AsmRegisterNode(start_position=sp, value="eax")
            i0_ret = AsmMovNode(
                start_position=sp,
                src=src_ret,
                dst=dst_ret,
            )
            i1_ret = AsmRetNode(start_position=sp)
            return [i0_ret, i1_ret]
        case TackyUnaryNode():
            op_unary = convert_tacky_unary_operator(tacky_instruction.operator)
            src_unary = convert_tacky_operand(tacky_instruction.src)
            dst_unary = convert_tacky_operand(tacky_instruction.dst)
            i0_unary = AsmMovNode(start_position=sp, src=src_unary, dst=dst_unary)
            i1_unary = AsmUnaryNode(start_position=sp, operator=op_unary, src=dst_unary)
            return [i0_unary, i1_unary]
        case TackyBinaryNode():
            return convert_tacky_binary_node(tacky_instruction)
        case _:
            raise ValueError(f"Unrecognised: {tacky_instruction}")


def convert_tacky_function(tacky_function: TackyFunctionNode) -> AsmFunctionNode:
    assert isinstance(tacky_function, TackyFunctionNode)

    asm_instructions = []
    for instr in tacky_function.instructions:
        asm = convert_tacky_instruction(instr)
        asm_instructions += asm

    return AsmFunctionNode(
        start_position=tacky_function.start_position,
        identifier=tacky_function.identifier,
        instructions=asm_instructions,
    )


def convert_tacky_program(tacky_program: TackyProgramNode) -> AsmProgramNode:
    assert isinstance(tacky_program, TackyProgramNode)

    func = convert_tacky_function(tacky_program.function_definition)

    return AsmProgramNode(start_position=tacky_program.start_position, function_definition=func)
