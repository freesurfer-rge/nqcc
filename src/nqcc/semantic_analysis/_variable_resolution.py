from typing import get_args

from pydantic import BaseModel

from nqcc.parser import (
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceBlockItemNode,
    SourceBlockNode,
    SourceBreakNode,
    SourceCompoundNode,
    SourceConstantIntNode,
    SourceContinueNode,
    SourceDeclarationNode,
    SourceExpressionNode,
    SourceExpressionStatementNode,
    SourceFunctionNode,
    SourceIfStatementNode,
    SourceNullStatementNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceDoWhileNode,
    SourceTernaryExpressonNode,
    SourceUnaryExpressionNode,
    SourceVarNode,
    SourceWhileNode,
)

from ._exceptions import (
    SemanticAnalysisBadLValue,
    SemanticAnalysisDuplicateDeclaration,
    SemanticAnalysisUnknownVariable,
)


class VariableInfo(BaseModel):
    name: str
    defined_in_block: bool


def make_inner_variable_map(outer_map: dict[str, VariableInfo]) -> dict[str, VariableInfo]:
    result: dict[str, VariableInfo] = {}
    for k, v in outer_map.items():
        nxt = VariableInfo(name=v.name, defined_in_block=False)
        result[k] = nxt
    return result


class VariableResolver:
    def __init__(self) -> None:
        self._counter = 0

    def resolve_declaration(
        self, decl: SourceDeclarationNode, variable_map: dict[str, VariableInfo]
    ):
        assert isinstance(decl, SourceDeclarationNode)

        orig_name = decl.identifier.identifier
        if orig_name in variable_map and variable_map[orig_name].defined_in_block:
            raise SemanticAnalysisDuplicateDeclaration(decl=decl)
        unique_name = f"{orig_name}.{self._counter}"
        self._counter += 1
        variable_map[orig_name] = VariableInfo(name=unique_name, defined_in_block=True)
        nxt_init: SourceExpressionNode | None = None
        if decl.initial is not None:
            nxt_init = self.resolve_expression(decl.initial, variable_map)

        nxt_var = SourceVarNode(
            start_position=decl.identifier.start_position, identifier=unique_name
        )
        return SourceDeclarationNode(
            start_position=decl.start_position, identifier=nxt_var, initial=nxt_init
        )

    def resolve_statement(
        self, stmt: SourceStatementNode, variable_map: dict[str, VariableInfo]
    ) -> SourceStatementNode:
        sp = stmt.start_position
        match stmt:
            case SourceReturnNode():
                updated = self.resolve_expression(stmt.value, variable_map)
                return SourceReturnNode(start_position=sp, value=updated)
            case SourceIfStatementNode():
                cond_update = self.resolve_expression(stmt.condition, variable_map)
                then_update = self.resolve_statement(stmt.then, variable_map)
                otherwise_update = None
                if stmt.otherwise:
                    otherwise_update = self.resolve_statement(stmt.otherwise, variable_map)
                return SourceIfStatementNode(
                    start_position=sp,
                    condition=cond_update,
                    then=then_update,
                    otherwise=otherwise_update,
                )
            case SourceExpressionStatementNode():
                updated = self.resolve_expression(stmt.value, variable_map)
                return SourceExpressionStatementNode(start_position=sp, value=updated)
            case SourceNullStatementNode() | SourceContinueNode() | SourceBreakNode():
                return stmt
            case SourceCompoundNode():
                inner_map = make_inner_variable_map(variable_map)
                resolved_block = self.resolve_block(stmt.block, inner_map)
                return SourceCompoundNode(start_position=sp, block=resolved_block)
            case SourceWhileNode():
                updated_cond = self.resolve_expression(stmt.condition, variable_map)
                updated_body = self.resolve_statement(stmt.body, variable_map)
                return SourceWhileNode(start_position=sp, condition=updated_cond, body=updated_body)
            case SourceDoWhileNode():
                updated_cond = self.resolve_expression(stmt.condition, variable_map)
                updated_body = self.resolve_statement(stmt.body, variable_map)
                return SourceDoWhileNode(
                    start_position=sp, condition=updated_cond, body=updated_body
                )
            case _:
                raise ValueError(f"Unrecognised: {stmt}")

    def resolve_expression(
        self, expr: SourceExpressionNode, variable_map: dict[str, VariableInfo]
    ) -> SourceExpressionNode:
        match expr:
            case SourceAssignmentNode():
                if not isinstance(expr.left, SourceVarNode):
                    raise SemanticAnalysisBadLValue(expr=expr.left)
                return SourceAssignmentNode(
                    start_position=expr.start_position,
                    left=self.resolve_expression(expr.left, variable_map),
                    right=self.resolve_expression(expr.right, variable_map),
                )
            case SourceVarNode():
                if expr.identifier in variable_map:
                    return SourceVarNode(
                        start_position=expr.start_position,
                        identifier=variable_map[expr.identifier].name,
                    )
                else:
                    raise SemanticAnalysisUnknownVariable(var=expr)
            case SourceConstantIntNode():
                return expr
            case SourceUnaryExpressionNode():
                return SourceUnaryExpressionNode(
                    start_position=expr.start_position,
                    operator=expr.operator,
                    expression=self.resolve_expression(expr.expression, variable_map),
                )
            case SourceBinaryExpressionNode():
                return SourceBinaryExpressionNode(
                    start_position=expr.start_position,
                    operator=expr.operator,
                    left=self.resolve_expression(expr.left, variable_map),
                    right=self.resolve_expression(expr.right, variable_map),
                )
            case SourceTernaryExpressonNode():
                return SourceTernaryExpressonNode(
                    start_position=expr.start_position,
                    condition=self.resolve_expression(expr.condition, variable_map),
                    then=self.resolve_expression(expr.then, variable_map),
                    otherwise=self.resolve_expression(expr.otherwise, variable_map),
                )
            case _:
                raise ValueError(f"Not recognised: {expr}")

    def resolve_block(
        self, block: SourceBlockNode, variable_map: dict[str, VariableInfo]
    ) -> SourceBlockNode:
        assert isinstance(block, SourceBlockNode)

        resolved_items: list[SourceBlockItemNode] = []
        for item in block.items:
            nxt = self.resolve_blockitem(item, variable_map)
            resolved_items.append(nxt)

        return SourceBlockNode(start_position=block.start_position, items=resolved_items)

    def resolve_blockitem(
        self, bi: SourceBlockItemNode, variable_map: dict[str, VariableInfo]
    ) -> SourceBlockItemNode:

        match bi:
            case SourceDeclarationNode():
                return self.resolve_declaration(bi, variable_map)
            case _ if isinstance(bi, get_args(SourceStatementNode)):
                return self.resolve_statement(bi, variable_map)
            case _:
                raise ValueError(f"Unrecognised: {bi}")


def resolve_function(func: SourceFunctionNode) -> SourceFunctionNode:
    resolver = VariableResolver()
    variable_map: dict[str, VariableInfo] = {}
    updated_body = resolver.resolve_block(func.body, variable_map)
    result = SourceFunctionNode(
        start_position=func.start_position, identifier=func.identifier, body=updated_body
    )
    return result


def resolve_program(prog: SourceProgramNode) -> SourceProgramNode:
    updated_func = resolve_function(prog.value)
    result = SourceProgramNode(start_position=prog.start_position, value=updated_func)
    return result
