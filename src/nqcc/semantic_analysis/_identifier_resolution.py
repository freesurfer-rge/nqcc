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
    SourceProgramNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceTernaryExpressonNode,
    SourceUnaryExpressionNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    SourceWhileNode,
)

from ._exceptions import (
    SemanticAnalysisBadLValue,
    SemanticAnalysisDuplicateDeclaration,
    SemanticAnalysisUnknownIdentifier,
)


class IdentifierInfo(BaseModel):
    name: str
    from_current_scope: bool
    has_linkage: bool


def make_inner_identifier_map(outer_map: dict[str, IdentifierInfo]) -> dict[str, IdentifierInfo]:
    result: dict[str, IdentifierInfo] = {}
    for k, v in outer_map.items():
        nxt = IdentifierInfo(name=v.name, from_current_scope=False, has_linkage=v.has_linkage)
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
            case SourceFunctionDeclarationNode():
                return self.resolve_function_declaration(decl, identifier_map)
            case _:
                raise ValueError(f"Unrecognised declaration: {decl}")

    def resolve_function_declaration(
        self, decl: SourceFunctionDeclarationNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceFunctionDeclarationNode:
        assert isinstance(decl, SourceFunctionDeclarationNode)

        if decl.identifier in identifier_map:
            prev_entry = identifier_map[decl.identifier]
            if prev_entry.from_current_scope and (not prev_entry.has_linkage):
                raise SemanticAnalysisDuplicateDeclaration(decl=decl)

        identifier_map[decl.identifier] = IdentifierInfo(
            name=decl.identifier, from_current_scope=True, has_linkage=True
        )

        inner_map = make_inner_identifier_map(identifier_map)

        new_params: list[str] = self.resolve_function_params(decl.params, inner_map)

        new_body = None
        if decl.body is not None:
            new_body = self.resolve_block(decl.body, inner_map)

        return SourceFunctionDeclarationNode(
            start_position=decl.start_position,
            identifier=decl.identifier,
            params=new_params,
            body=new_body,
            storage_class=decl.storage_class,
        )

    def resolve_variable_declaration(
        self, decl: SourceVariableDeclarationNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceVariableDeclarationNode:
        assert isinstance(decl, SourceVariableDeclarationNode)

        orig_name = decl.identifier.identifier
        if orig_name in identifier_map and identifier_map[orig_name].from_current_scope:
            raise SemanticAnalysisDuplicateDeclaration(decl=decl)
        unique_name = f"{orig_name}.{self._counter}"
        self._counter += 1
        identifier_map[orig_name] = IdentifierInfo(
            name=unique_name, from_current_scope=True, has_linkage=False
        )
        nxt_init: SourceExpressionNode | None = None
        if decl.initial is not None:
            nxt_init = self.resolve_expression(decl.initial, identifier_map)

        nxt_var = SourceVarNode(
            start_position=decl.identifier.start_position, identifier=unique_name
        )
        return SourceVariableDeclarationNode(
            start_position=decl.start_position,
            identifier=nxt_var,
            initial=nxt_init,
            storage_class=decl.storage_class,
        )

    def resolve_function_params(
        self, params: list[str], identifier_map: dict[str, IdentifierInfo]
    ) -> list[str]:
        result = []

        for p in params:
            if p in identifier_map and identifier_map[p].from_current_scope:
                # Probably should have better exception
                raise ValueError(f"parameter {p} already defined")

            unique_name = f"{p}.arg.{self._counter}"
            self._counter += 1

            identifier_map[p] = IdentifierInfo(
                name=unique_name, from_current_scope=True, has_linkage=False
            )
            result.append(unique_name)
        return result

    def resolve_for_init(
        self, init: SourceForInitNode, identifier_map: dict[str, IdentifierInfo]
    ) -> SourceForInitNode:
        assert isinstance(init, get_args(SourceForInitNode))
        sp = init.start_position
        match init:
            case SourceInitDeclNode():
                updated_decl = self.resolve_variable_declaration(init.decl, identifier_map)
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

    def resolve_expression(  # noqa:C901
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
                    raise SemanticAnalysisUnknownIdentifier(var=expr)
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

                    new_args: list[SourceExpressionNode] = []
                    for arg in expr.args:
                        nxt = self.resolve_expression(arg, identifier_map)
                        new_args.append(nxt)

                    return SourceFunctionCallNode(
                        start_position=expr.start_position, identifier=new_name, args=new_args
                    )
                else:
                    raise SemanticAnalysisUnknownIdentifier(var=expr)
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
            case SourceFunctionDeclarationNode():
                if bi.body is not None:
                    raise ValueError("Cannot nest function definitions")
                return self.resolve_declaration(bi, identifier_map)
            case _ if isinstance(bi, get_args(SourceStatementNode)):
                return self.resolve_statement(bi, identifier_map)
            case _:
                raise ValueError(f"Unrecognised: {bi}")


def resolve_program(prog: SourceProgramNode) -> SourceProgramNode:
    resolver = IdentifierResolver()
    identifier_map: dict[str, IdentifierInfo] = {}
    updated_funcs = []
    for f in prog.declarations:
        updated = resolver.resolve_declaration(f, identifier_map)
        assert isinstance(updated, SourceFunctionDeclarationNode)
        updated_funcs.append(updated)
    result = SourceProgramNode(start_position=prog.start_position, declarations=updated_funcs)
    return result
