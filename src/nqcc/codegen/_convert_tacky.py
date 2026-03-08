from nqcc.tacky import (
    TackyComplementNode,
    TackyConstantIntNode,
    TackyInstruction,
    TackyNegateNode,
    TackyReturnNode,
    TackyUnaryNode,
    TackyUnaryOperator,
    TackyValue,
    TackyVarNode,
)

from ._assembler_ast import (
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmMovNode,
    AsmNegOperator,
    AsmNotOperator,
    AsmOperandNode,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmUnaryNode,
    AsmUnaryOperator,
)


def convert_tacky_operand(tacky_value: TackyValue) -> AsmOperandNode:
    match tacky_value:
        case v if isinstance(v, TackyConstantIntNode):
            return AsmImmediateIntNode(
                start_position=tacky_value.start_position, value=tacky_value.value
            )
        case v if isinstance(v, TackyVarNode):
            return AsmPseudoRegisterNode(
                start_position=tacky_value.start_position, identifier=tacky_value.identifier
            )
        case _:
            raise ValueError(f"Unrecognised: {tacky_value}")


def convert_tacky_unary_operator(tacky_operator: TackyUnaryOperator) -> AsmUnaryOperator:
    match tacky_operator:
        case v if isinstance(v, TackyComplementNode):
            return AsmNotOperator(start_position=tacky_operator.start_position)
        case v if isinstance(v, TackyNegateNode):
            return AsmNegOperator(start_position=tacky_operator.start_position)
        case _:
            raise ValueError(f"Unrecognised: {tacky_operator}")


def convert_tacky_instruction(tacky_instruction: TackyInstruction) -> list[AsmInstructionNode]:
    sp = tacky_instruction.start_position
    match tacky_instruction:
        case TackyReturnNode():
            src_ret = convert_tacky_operand(tacky_instruction.value)
            dst_ret = AsmRegisterNode(start_position=sp, value="eax")
            i0_ret = AsmMovNode(
                start_position=sp,
                source=src_ret,
                destination=dst_ret,
            )
            i1_ret = AsmRetNode(start_position=sp)
            return [i0_ret, i1_ret]
        case TackyUnaryNode():
            op_unary = convert_tacky_unary_operator(tacky_instruction.operator)
            src_unary = convert_tacky_operand(tacky_instruction.src)
            dst_unary = convert_tacky_operand(tacky_instruction.dst)
            i0_unary = AsmMovNode(start_position=sp, source=src_unary, destination=dst_unary)
            i1_unary = AsmUnaryNode(start_position=sp, operator=op_unary, source=dst_unary)
            return [i0_unary, i1_unary]
        case _:
            raise ValueError(f"Unrecognised: {tacky_instruction}")
