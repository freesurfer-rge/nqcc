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
    SourceDoWhileNode,
    SourceExpressionNode,
    SourceExpressionStatementNode,
    SourceForInitNode,
    SourceForNode,
    SourceFunctionDeclarationNode,
    SourceIfStatementNode,
    SourceInitDeclNode,
    SourceInitExpressionNode,
    SourceNullStatementNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceTernaryExpressonNode,
    SourceUnaryExpressionNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    SourceWhileNode,
    SourceFunctionCallNode,
    SourceDeclarationNode,
)

from ._exceptions import (
    SemanticAnalysisBadLValue,
    SemanticAnalysisDuplicateDeclaration,
    SemanticAnalysisUnknownVariable,
)


class IdentifierInfo(BaseModel):
    name: str
    defined_in_block: bool
    has_linkage: bool


def make_inner_identifier_map(outer_map: dict[str, IdentifierInfo]) -> dict[str, IdentifierInfo]:
    result: dict[str, IdentifierInfo] = {}
    for k, v in outer_map.items():
        nxt = IdentifierInfo(name=v.name, defined_in_block=False, has_linkage=v.has_linkage)
        result[k] = nxt
    return result


class IdentifierResolver:
    def __init__(self) -> None:
        self._counter = 0

    def resolve_declaration(
        self, decl: SourceDeclarationNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceDeclarationNode:
        match decl:
            case SourceVariableDeclarationNode():
                return self.resolve_variable_declaration(decl, identifier_map)
            case _:
                raise ValueError(f"Unrecognised declaration: {decl}")

    def resolve_variable_declaration(
        self, decl: SourceVariableDeclarationNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceVariableDeclarationNode:
        assert isinstance(decl, SourceVariableDeclarationNode)

        orig_name = decl.identifier.identifier
        if orig_name in identifier_map and identifier_map[orig_name].defined_in_block:
            raise SemanticAnalysisDuplicateDeclaration(decl=decl)
        unique_name = f"{orig_name}.{self._counter}"
        self._counter += 1
        identifier_map[orig_name] = IdentifierInfo(
            name=unique_name, defined_in_block=True, has_linkage=False
        )
        nxt_init: SourceExpressionNode | None = None
        if decl.initial is not None:
            nxt_init = self.resolve_expression(decl.initial, identifier_map)

        nxt_var = SourceVarNode(
            start_position=decl.identifier.start_position, identifier=unique_name
        )
        return SourceVariableDeclarationNode(
            start_position=decl.start_position, identifier=nxt_var, initial=nxt_init
        )

    def resolve_for_init(
        self, init: SourceForInitNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceForInitNode:
        assert isinstance(init, get_args(SourceForInitNode))
        sp = init.start_position
        match init:
            case SourceInitDeclNode():
                updated_decl = self.resolve_declaration(init.decl, identifier_map)
                return SourceInitDeclNode(start_position=sp, decl=updated_decl)
            case SourceInitExpressionNode():
                updated_exp = self.resolve_optional_expression(init.expression, identifier_map)
                return SourceInitExpressionNode(start_position=sp, expression=updated_exp)
            case _:
                raise ValueError(f"Unrecognised: {init}")

    def resolve_statement(
        self, stmt: SourceStatementNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceStatementNode:
        sp = stmt.start_position
        match stmt:
            case SourceReturnNode():
                updated = self.resolve_expression(stmt.value, identifier_map)
                return SourceReturnNode(start_position=sp, value=updated)
            case SourceIfStatementNode():
                cond_update = self.resolve_expression(stmt.condition, identifier_map)
                then_update = self.resolve_statement(stmt.then, identifier_map)
                otherwise_update = None
                if stmt.otherwise:
                    otherwise_update = self.resolve_statement(stmt.otherwise, identifier_map)
                return SourceIfStatementNode(
                    start_position=sp,
                    condition=cond_update,
                    then=then_update,
                    otherwise=otherwise_update,
                )
            case SourceExpressionStatementNode():
                updated = self.resolve_expression(stmt.value, identifier_map)
                return SourceExpressionStatementNode(start_position=sp, value=updated)
            case SourceNullStatementNode() | SourceContinueNode() | SourceBreakNode():
                return stmt
            case SourceCompoundNode():
                inner_map = make_inner_identifier_map(identifier_map)
                resolved_block = self.resolve_block(stmt.block, inner_map)
                return SourceCompoundNode(start_position=sp, block=resolved_block)
            case SourceWhileNode():
                updated_cond = self.resolve_expression(stmt.condition, identifier_map)
                updated_body = self.resolve_statement(stmt.body, identifier_map)
                return SourceWhileNode(start_position=sp, condition=updated_cond, body=updated_body)
            case SourceDoWhileNode():
                updated_cond = self.resolve_expression(stmt.condition, identifier_map)
                updated_body = self.resolve_statement(stmt.body, identifier_map)
                return SourceDoWhileNode(
                    start_position=sp, condition=updated_cond, body=updated_body
                )
            case SourceForNode():
                inner_map = make_inner_identifier_map(identifier_map)
                init = self.resolve_for_init(stmt.init, inner_map)
                cond = self.resolve_optional_expression(stmt.condition, inner_map)
                post = self.resolve_optional_expression(stmt.post, inner_map)
                body = self.resolve_statement(stmt.body, inner_map)
                return SourceForNode(
                    start_position=sp, init=init, condition=cond, post=post, body=body
                )
            case _:
                raise ValueError(f"Unrecognised: {stmt}")

    def resolve_optional_expression(
        self, expr: SourceExpressionNode | None, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceExpressionNode | None:
        if expr is None:
            return None
        return self.resolve_expression(expr, identifier_map)

    def resolve_expression(
        self, expr: SourceExpressionNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceExpressionNode:
        match expr:
            case SourceAssignmentNode():
                if not isinstance(expr.left, SourceVarNode):
                    raise SemanticAnalysisBadLValue(expr=expr.left)
                return SourceAssignmentNode(
                    start_position=expr.start_position,
                    left=self.resolve_expression(expr.left, identifier_map),
                    right=self.resolve_expression(expr.right, identifier_map),
                )
            case SourceVarNode():
                if expr.identifier in identifier_map:
                    return SourceVarNode(
                        start_position=expr.start_position,
                        identifier=identifier_map[expr.identifier].name,
                    )
                else:
                    raise SemanticAnalysisUnknownVariable(var=expr)
            case SourceConstantIntNode():
                return expr
            case SourceUnaryExpressionNode():
                return SourceUnaryExpressionNode(
                    start_position=expr.start_position,
                    operator=expr.operator,
                    expression=self.resolve_expression(expr.expression, identifier_map),
                )
            case SourceBinaryExpressionNode():
                return SourceBinaryExpressionNode(
                    start_position=expr.start_position,
                    operator=expr.operator,
                    left=self.resolve_expression(expr.left, identifier_map),
                    right=self.resolve_expression(expr.right, identifier_map),
                )
            case SourceTernaryExpressonNode():
                return SourceTernaryExpressonNode(
                    start_position=expr.start_position,
                    condition=self.resolve_expression(expr.condition, identifier_map),
                    then=self.resolve_expression(expr.then, identifier_map),
                    otherwise=self.resolve_expression(expr.otherwise, identifier_map),
                )
            case SourceFunctionCallNode():
                if expr.identifier in identifier_map:
                    new_name = identifier_map[expr.identifier].name
                    new_args = []

                    return SourceFunctionCallNode(
                        start_position=expr.start_position, identifier=new_name, args=new_args
                    )
                else:
                    raise SemanticAnalysisUnknownVariable(var=expr)
            case _:
                raise ValueError(f"Not recognised: {expr}")

    def resolve_block(
        self, block: SourceBlockNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceBlockNode:
        assert isinstance(block, SourceBlockNode)

        resolved_items: list[SourceBlockItemNode] = []
        for item in block.items:
            nxt = self.resolve_blockitem(item, identifier_map)
            resolved_items.append(nxt)

        return SourceBlockNode(start_position=block.start_position, items=resolved_items)

    def resolve_blockitem(
        self, bi: SourceBlockItemNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceBlockItemNode:

        match bi:
            case SourceVariableDeclarationNode():
                return self.resolve_declaration(bi, identifier_map)
            case _ if isinstance(bi, get_args(SourceStatementNode)):
                return self.resolve_statement(bi, identifier_map)
            case _:
                raise ValueError(f"Unrecognised: {bi}")


def resolve_function(func: SourceFunctionDeclarationNode) -> SourceFunctionDeclarationNode:
    resolver = IdentifierResolver()
    identifier_map: dict[str, IdentifierInfo] = {}
    assert func.body is not None, "Missing function body"
    updated_body = resolver.resolve_block(func.body, identifier_map)
    result = SourceFunctionDeclarationNode(
        start_position=func.start_position,
        identifier=func.identifier,
        body=updated_body,
        params=func.params,
    )
    return result


def resolve_program(prog: SourceProgramNode) -> SourceProgramNode:
    updated_funcs = []
    for f in prog.functions:
        updated = resolve_function(f)
        updated_funcs.append(updated)
    result = SourceProgramNode(start_position=prog.start_position, functions=updated_funcs)
    return result
