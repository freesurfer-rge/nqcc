from typing import Literal, Union

from pydantic import BaseModel


class SourceASTNode(BaseModel):
    node_type: str
    start_position: int


class SourceConstantIntNode(SourceASTNode):
    node_type: Literal["SourceConstantIntNode"] = "SourceConstantIntNode"
    value: int


class SourceVarNode(SourceASTNode):
    node_type: Literal["SourceVarNode"] = "SourceVarNode"
    identifier: str


class SourceComplement(SourceASTNode):
    node_type: Literal["SourceComplementNode"] = "SourceComplementNode"


class SourceNegate(SourceASTNode):
    node_type: Literal["SourceNegateNode"] = "SourceNegateNode"


class SourceLogicalNot(SourceASTNode):
    node_type: Literal["SourceLogicalNot"] = "SourceLogicalNot"


SourceUnaryOperator = Union[SourceComplement, SourceNegate, SourceLogicalNot]


class SourceUnaryExpressionNode(SourceASTNode):
    node_type: Literal["SourceUnaryExpressionNode"] = "SourceUnaryExpressionNode"
    operator: SourceUnaryOperator
    expression: SourceExpressionNode


class SourceBinOp(SourceASTNode):
    precedence: int


class SourceAssignment(SourceBinOp):
    # Note this is distinct from an assignment in a declaration
    node_type: Literal["SourceAssignment"] = "SourceAssignment"
    precedence: Literal[1] = 1


class SourceTernary(SourceBinOp):
    node_type: Literal["SourceTernary"] = "SourceTernary"
    precedence: Literal[3] = 3


class SourceLogicalOr(SourceBinOp):
    node_type: Literal["SourceLogicalOr"] = "SourceLogicalOr"
    precedence: Literal[5] = 5


class SourceLogicalAnd(SourceBinOp):
    node_type: Literal["SourceLogicalAnd"] = "SourceLogicalAnd"
    precedence: Literal[10] = 10


class SourceBitwiseOr(SourceBinOp):
    node_type: Literal["SourceBitwiseOr"] = "SourceBitwiseOr"
    precedence: Literal[15] = 15


class SourceBitwiseXor(SourceBinOp):
    node_type: Literal["SourceBitwiseXor"] = "SourceBitwiseXor"
    precedence: Literal[20] = 20


class SourceBitwiseAnd(SourceBinOp):
    node_type: Literal["SourceBitwiseAnd"] = "SourceBitwiseAnd"
    precedence: Literal[25] = 25


class SourceEqualTo(SourceBinOp):
    node_type: Literal["SourceEqualTo"] = "SourceEqualTo"
    precedence: Literal[30] = 30


class SourceNotEqualTo(SourceBinOp):
    node_type: Literal["SourceNotEqualTo"] = "SourceNotEqualTo"
    precedence: Literal[30] = 30


class SourceLessThan(SourceBinOp):
    node_type: Literal["SourceLessThan"] = "SourceLessThan"
    precedence: Literal[35] = 35


class SourceLessThanOrEqual(SourceBinOp):
    node_type: Literal["SourceLessThanOrEqual"] = "SourceLessThanOrEqual"
    precedence: Literal[35] = 35


class SourceGreaterThan(SourceBinOp):
    node_type: Literal["SourceGreaterThan"] = "SourceGreaterThan"
    precedence: Literal[35] = 35


class SourceGreaterThanOrEqual(SourceBinOp):
    node_type: Literal["SourceGreaterThanOrEqual"] = "SourceGreaterThanOrEqual"
    precedence: Literal[35] = 35


class SourceLeftShift(SourceBinOp):
    node_type: Literal["SourceLeftShift"] = "SourceLeftShift"
    precedence: Literal[40] = 40


class SourceRightShift(SourceBinOp):
    node_type: Literal["SourceRightShift"] = "SourceRightShift"
    precedence: Literal[40] = 40


class SourceAdd(SourceBinOp):
    node_type: Literal["SourceAdd"] = "SourceAdd"
    precedence: Literal[45] = 45


class SourceSubtract(SourceBinOp):
    node_type: Literal["SourceSubtract"] = "SourceSubtract"
    precedence: Literal[45] = 45


class SourceMultiply(SourceBinOp):
    node_type: Literal["SourceMultiply"] = "SourceMultiply"
    precedence: Literal[50] = 50


class SourceDivide(SourceBinOp):
    node_type: Literal["SourceDivide"] = "SourceDivide"
    precedence: Literal[50] = 50


class SourceModulo(SourceBinOp):
    node_type: Literal["SourceModulo"] = "SourceModulo"
    precedence: Literal[50] = 50


SourceBinaryOperator = Union[
    SourceAssignment,
    SourceAdd,
    SourceSubtract,
    SourceMultiply,
    SourceDivide,
    SourceModulo,
    SourceBitwiseXor,
    SourceBitwiseAnd,
    SourceBitwiseOr,
    SourceLeftShift,
    SourceRightShift,
    SourceEqualTo,
    SourceNotEqualTo,
    SourceLessThan,
    SourceLessThanOrEqual,
    SourceGreaterThan,
    SourceGreaterThanOrEqual,
    SourceLogicalAnd,
    SourceLogicalOr,
    SourceTernary,
]


class SourceBinaryExpressionNode(SourceASTNode):
    node_type: Literal["SourceBinaryExpressionNode"] = "SourceBinaryExpressionNode"
    operator: SourceBinaryOperator
    left: SourceExpressionNode
    right: SourceExpressionNode


class SourceAssignmentNode(SourceASTNode):
    node_type: Literal["SourceAssignmentNode"] = "SourceAssignmentNode"
    left: SourceExpressionNode
    right: SourceExpressionNode


class SourceTernaryExpressonNode(SourceASTNode):
    node_type: Literal["SourceTernaryExpressonNode"] = "SourceTernaryExpressonNode"
    condition: SourceExpressionNode
    then: SourceExpressionNode
    otherwise: SourceExpressionNode


SourceExpressionNode = Union[
    SourceConstantIntNode,
    SourceVarNode,
    SourceUnaryExpressionNode,
    SourceBinaryExpressionNode,
    SourceAssignmentNode,
    SourceTernaryExpressonNode,
]


class SourceReturnNode(SourceASTNode):
    node_type: Literal["SourceReturnNode"] = "SourceReturnNode"
    value: SourceExpressionNode


class SourceExpressionStatementNode(SourceASTNode):
    node_type: Literal["SourceExpressionStatementNode"] = "SourceExpressionStatementNode"
    value: SourceExpressionNode


class SourceNullStatementNode(SourceASTNode):
    node_type: Literal["SourceNullStatementNode"] = "SourceNullStatementNode"


class SourceIfStatementNode(SourceASTNode):
    node_type: Literal["SourceIfStatementNode"] = "SourceIfStatementNode"
    condition: SourceExpressionNode
    then: SourceStatementNode
    otherwise: SourceStatementNode | None


class SourceCompoundNode(SourceASTNode):
    node_type: Literal["SourceCompoundNode"] = "SourceCompoundNode"
    block: SourceBlockNode


class SourceBreakNode(SourceASTNode):
    node_type: Literal["SourceBreakNode"] = "SourceBreakNode"
    label: str = ""


class SourceContinueNode(SourceASTNode):
    node_type: Literal["SourceContinueNode"] = "SourceContinueNode"
    label: str = ""


class SourceWhileNode(SourceASTNode):
    node_type: Literal["SourceWhileNode"] = "SourceWhileNode"
    condition: SourceExpressionNode
    body: SourceStatementNode
    label: str = ""


class SourceDoWhileNode(SourceASTNode):
    node_type: Literal["SourceDoWhileNode"] = "SourceDoWhileNode"
    condition: SourceExpressionNode
    body: SourceStatementNode
    label: str = ""


class SourceForNode(SourceASTNode):
    node_type: Literal["SourceForNode"] = "SourceForNode"
    init: SourceForInitNode
    condition: SourceExpressionNode | None
    post: SourceExpressionNode | None
    body: SourceStatementNode
    label: str = ""


SourceStatementNode = Union[
    SourceReturnNode,
    SourceExpressionStatementNode,
    SourceNullStatementNode,
    SourceIfStatementNode,
    SourceCompoundNode,
    SourceBreakNode,
    SourceContinueNode,
    SourceWhileNode,
    SourceDoWhileNode,
    SourceForNode,
]


class SourceDeclarationNode(SourceASTNode):
    node_type: Literal["SourceDeclarationNode"] = "SourceDeclarationNode"
    identifier: SourceVarNode
    initial: SourceExpressionNode | None


SourceBlockItemNode = Union[SourceDeclarationNode, SourceStatementNode]


class SourceBlockNode(SourceASTNode):
    node_type: Literal["SourceBlockNode"] = "SourceBlockNode"
    items: list[SourceBlockItemNode]


class SourceInitDeclNode(SourceASTNode):
    node_type: Literal["SourceInitDeclNode"] = "SourceInitDeclNode"
    decl: SourceDeclarationNode


class SourceInitExpressionNode(SourceASTNode):
    node_type: Literal["SourceInitExpressionNode"] = "SourceInitExpressionNode"
    expression: SourceExpressionNode | None


SourceForInitNode = Union[SourceInitDeclNode, SourceInitExpressionNode]


class SourceFunctionNode(SourceASTNode):
    node_type: Literal["SourceFunctionNode"] = "SourceFunctionNode"
    identifier: str
    body: SourceBlockNode


class SourceProgramNode(SourceASTNode):
    node_type: Literal["SourceProgramNode"] = "SourceProgramNode"
    value: SourceFunctionNode
