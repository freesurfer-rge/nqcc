from typing import Literal, Union

from pydantic import BaseModel

from nqcc.parser import SourceConstantIntNode, SourceExpressionNode, SourceStatementNode, SourceReturnNode, SourceFunctionNode, SourceProgramNode


class AsmASTNode(BaseModel):
    node_type: str
    start_position: int


class AsmImmediateIntNode(AsmASTNode):
    node_type: Literal["AsmImmediateIntNode"] = "AsmImmediateIntNode"
    value: int


class AsmRegisterNode(AsmASTNode):
    node_type: Literal["AsmRegisterNode"] = "AsmRegisterNode"
    value: Literal["eax", "rbp", "rsp"]


AsmOperandNode = Union[AsmImmediateIntNode, AsmRegisterNode]


class AsmMovNode(AsmASTNode):
    node_type: Literal["AsmMovNode"] = "AsmMovNode"
    source: AsmOperandNode
    destination: AsmOperandNode


class AsmRetNode(AsmASTNode):
    node_type: Literal["AsmRetNode"] = "AsmRetNode"


AsmInstructionNode = Union[AsmMovNode, AsmRetNode]


class AsmFunctionNode(AsmASTNode):
    node_type: Literal["AsmFunctionNode"] = "AsmFunctionNode"
    identifier: str
    instruction: list[AsmInstructionNode]


class AsmProgramNode(AsmASTNode):
    node_type: Literal["AsmFunctionNode"] = "AsmFunctionNode"


def convert_expression_node(node: SourceExpressionNode) -> AsmOperandNode:
    match node:
        case SourceConstantIntNode():
            return AsmImmediateIntNode(start_position=node.start_position, value=node.value)

        case _:
            raise ValueError(f"Unrecognised: {node.model_dump_json()}")

def convert_statement_node(node: SourceStatementNode) -> list[AsmInstructionNode]:
    match node:
        case SourceReturnNode():
            value_node = convert_expression_node(node.value)
            ret_node = AsmRetNode(start_position=value_node.start_position)
            return [value_node, ret_node]
        
        case _:
            raise Value(f"Unrecognised: {node.model_dump_json()}")