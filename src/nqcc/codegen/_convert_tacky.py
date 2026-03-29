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

from ._assembler_ast import (
    AsmAdd,
    AsmBinaryNode,
    AsmBinaryOperator,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmCdqNode,
    AsmCmpNode,
    AsmCondCode,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmJmpCCNode,
    AsmJmpNode,
    AsmLabelNode,
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
    AsmSetCCNode,
    AsmSubtract,
    AsmUnaryNode,
    AsmUnaryOperator,
)

_UNARY_OPERATOR_MAP: dict[Type[TackyUnaryOperator], Type] = {
    TackyComplement: AsmNot,
    TackyNegate: AsmNeg,
}

_BINARY_OPERATOR_MAP: dict[Type[TackyBinaryOperator], Type] = {
    TackyAdd: AsmAdd,
    TackySubtract: AsmSubtract,
    TackyMultiply: AsmMultiply,
    TackyBitwiseAnd: AsmBitwiseAnd,
    TackyBitwiseOr: AsmBitwiseOr,
    TackyBitwiseXor: AsmBitwiseXor,
    TackyLeftShift: AsmLeftShift,
    TackyRightShift: AsmRightShift,
}

_COND_CODE_MAP: dict[Type[TackyBinaryOperator], AsmCondCode] = {
    TackyEqualTo: "E",
    TackyNotEqualTo: "NE",
    TackyGreaterThan: "G",
    TackyGreaterThanOrEqual: "GE",
    TackyLessThan: "L",
    TackyLessThanOrEqual: "LE",
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


def convert_tacky_unary_node(tacky_node: TackyUnaryNode) -> list[AsmInstructionNode]:
    sp = tacky_node.start_position
    src_unary = convert_tacky_operand(tacky_node.src)
    dst_unary = convert_tacky_operand(tacky_node.dst)
    if isinstance(tacky_node.operator, TackyLogicalNot):
        i0 = AsmCmpNode(
            start_position=sp, src=AsmImmediateIntNode(start_position=sp, value=0), dst=src_unary
        )
        i1 = AsmMovNode(
            start_position=sp, src=AsmImmediateIntNode(start_position=sp, value=0), dst=dst_unary
        )
        i2 = AsmSetCCNode(start_position=sp, src=dst_unary, cond_code="E")
        return [i0, i1, i2]
    else:
        op_unary = convert_tacky_unary_operator(tacky_node.operator)
        i0_unary = AsmMovNode(start_position=sp, src=src_unary, dst=dst_unary)
        i1_unary = AsmUnaryNode(start_position=sp, operator=op_unary, src=dst_unary)
        return [i0_unary, i1_unary]


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
            div_eax = AsmRegisterNode(start_position=tacky_node.start_position, value="AX")
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
                    start_position=tacky_node.start_position, value="DX"
                )
            i4_div_op = AsmMovNode(
                start_position=tacky_node.start_position, src=result_register, dst=dest
            )
            return [i0_div_op, i1_div_op, i2_div_op, i4_div_op]
        case (
            TackyEqualTo()
            | TackyNotEqualTo()
            | TackyGreaterThan()
            | TackyGreaterThanOrEqual()
            | TackyLessThan()
            | TackyLessThanOrEqual()
        ):
            i0_cmp_op = AsmCmpNode(start_position=tacky_node.start_position, src=right, dst=left)
            i1_cmp_op = AsmMovNode(
                start_position=tacky_node.start_position,
                src=AsmImmediateIntNode(start_position=tacky_node.start_position, value=0),
                dst=dest,
            )
            i2_cmp_op = AsmSetCCNode(
                start_position=tacky_node.start_position,
                src=dest,
                cond_code=_COND_CODE_MAP[type(tacky_node.operator)],
            )
            return [i0_cmp_op, i1_cmp_op, i2_cmp_op]
        case _:
            raise ValueError(f"Unrecognised: {tacky_node.operator}")


def convert_tacky_instruction(tacky_instruction: TackyInstruction) -> list[AsmInstructionNode]:
    sp = tacky_instruction.start_position
    match tacky_instruction:
        case TackyReturnNode():
            src_ret = convert_tacky_operand(tacky_instruction.value)
            dst_ret = AsmRegisterNode(start_position=sp, value="AX")
            i0_ret = AsmMovNode(
                start_position=sp,
                src=src_ret,
                dst=dst_ret,
            )
            i1_ret = AsmRetNode(start_position=sp)
            return [i0_ret, i1_ret]
        case TackyUnaryNode():
            return convert_tacky_unary_node(tacky_instruction)
        case TackyBinaryNode():
            return convert_tacky_binary_node(tacky_instruction)
        case TackyJumpNode():
            return [AsmJmpNode(start_position=sp, target=tacky_instruction.target)]
        case TackyJumpIfZeroNode() | TackyJumpIfNotZeroNode():
            cond_jmpzero = convert_tacky_operand(tacky_instruction.condition)
            i0_jmpzero = AsmCmpNode(
                start_position=sp,
                src=AsmImmediateIntNode(start_position=sp, value=0),
                dst=cond_jmpzero,
            )

            cond_code: AsmCondCode = "E"
            if isinstance(tacky_instruction, TackyJumpIfNotZeroNode):
                cond_code = "NE"

            i1_jmpzero = AsmJmpCCNode(
                start_position=sp, target=tacky_instruction.target, cond_code=cond_code
            )
            return [i0_jmpzero, i1_jmpzero]
        case TackyLabelNode():
            return [AsmLabelNode(start_position=sp, identifier=tacky_instruction.identifier)]
        case TackyCopyNode():
            copy_src = convert_tacky_operand(tacky_instruction.src)
            copy_dst = convert_tacky_operand(tacky_instruction.dst)
            return [AsmMovNode(start_position=sp, src=copy_src, dst=copy_dst)]
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
