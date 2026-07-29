from typing import TypeGuard

from .parser import (
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceBlockItemNode,
    SourceBreakNode,
    SourceCompoundNode,
    SourceConstantIntNode,
    SourceContinueNode,
    SourceDeclarationNode,
    SourceDoWhileNode,
    SourceExpressionNode,
    SourceExpressionStatementNode,
    SourceForInitNode,
    SourceForNode,
    SourceFunctionCallNode,
    SourceFunctionDeclarationNode,
    SourceIfStatementNode,
    SourceInitDeclNode,
    SourceInitExpressionNode,
    SourceNullStatementNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceTernaryExpressonNode,
    SourceUnaryExpressionNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    SourceWhileNode,
)


def is_expression(node: object) -> TypeGuard[SourceExpressionNode]:
    return isinstance(
        node,
        (
            SourceConstantIntNode,
            SourceVarNode,
            SourceUnaryExpressionNode,
            SourceBinaryExpressionNode,
            SourceAssignmentNode,
            SourceTernaryExpressonNode,
            SourceFunctionCallNode,
        ),
    )


def is_declaration(node: object) -> TypeGuard[SourceDeclarationNode]:
    return isinstance(node, (SourceVariableDeclarationNode, SourceFunctionDeclarationNode))


def is_statement(node: object) -> TypeGuard[SourceStatementNode]:
    return isinstance(
        node,
        (
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
        ),
    )


def is_block_item(node: object) -> TypeGuard[SourceBlockItemNode]:
    return isinstance(node, (SourceVariableDeclarationNode, SourceFunctionDeclarationNode)) or is_statement(node)


def is_for_init(node: object) -> TypeGuard[SourceForInitNode]:
    return isinstance(node, (SourceInitDeclNode, SourceInitExpressionNode))
