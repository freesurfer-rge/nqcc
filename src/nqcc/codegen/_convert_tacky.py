from nqcc.tacky import TackyConstantIntNode, TackyValue, TackyVarNode

from ._assembler_ast import AsmImmediateIntNode, AsmOperandNode, AsmPseudoRegisterNode


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
