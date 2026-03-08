from nqcc.tacky import (
    TackyComplementNode,
    TackyConstantIntNode,
    TackyNegateNode,
    TackyUnaryOperator,
    TackyValue,
    TackyVarNode,
)

from ._assembler_ast import (
    AsmImmediateIntNode,
    AsmNegOperator,
    AsmNotOperator,
    AsmOperandNode,
    AsmPseudoRegisterNode,
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
