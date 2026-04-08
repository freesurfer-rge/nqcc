from typing import get_args

from nqcc.parser import (
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceBlockItemNode,
    SourceConstantIntNode,
    SourceDeclarationNode,
    SourceExpressionNode,
    SourceExpressionStatementNode,
    SourceFunctionNode,
    SourceIfStatementNode,
    SourceNullStatementNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceStatementNode,
    SourceUnaryExpressionNode,
    SourceVarNode,
)

from ._exceptions import (
    SemanticAnalysisBadLValue,
    SemanticAnalysisDuplicateDeclaration,
    SemanticAnalysisUnknownVariable,
)


class VariableResolver:
    def __init__(self) -> None:
        self._variable_map: dict[str, str] = {}
        self._counter = 0

    def resolve_declaration(self, decl: SourceDeclarationNode):
        assert isinstance(decl, SourceDeclarationNode)

        orig_name = decl.identifier.identifier
        if orig_name in self._variable_map:
            raise SemanticAnalysisDuplicateDeclaration(decl=decl)
        unique_name = f"{orig_name}.{self._counter}"
        self._counter += 1
        self._variable_map[orig_name] = unique_name
        nxt_init: SourceExpressionNode | None = None
        if decl.initial is not None:
            nxt_init = self.resolve_expression(decl.initial)

        nxt_var = SourceVarNode(
            start_position=decl.identifier.start_position, identifier=unique_name
        )
        return SourceDeclarationNode(
            start_position=decl.start_position, identifier=nxt_var, initial=nxt_init
        )

    def resolve_statement(self, stmt: SourceStatementNode) -> SourceStatementNode:
        sp = stmt.start_position
        match stmt:
            case SourceReturnNode():
                updated = self.resolve_expression(stmt.value)
                return SourceReturnNode(start_position=sp, value=updated)
            case SourceIfStatementNode():
                cond_update = self.resolve_expression(stmt.condition)
                then_update = self.resolve_statement(stmt.then)
                otherwise_update = None
                if stmt.otherwise:
                    otherwise_update = self.resolve_statement(stmt.otherwise)
                return SourceIfStatementNode(
                    start_position=sp,
                    condition=cond_update,
                    then=then_update,
                    otherwise=otherwise_update,
                )
            case SourceExpressionStatementNode():
                updated = self.resolve_expression(stmt.value)
                return SourceExpressionStatementNode(start_position=sp, value=updated)
            case SourceNullStatementNode():
                return SourceNullStatementNode(start_position=sp)
            case _:
                raise ValueError(f"Unrecognised: {stmt}")

    def resolve_expression(self, expr: SourceExpressionNode) -> SourceExpressionNode:
        match expr:
            case SourceAssignmentNode():
                if not isinstance(expr.left, SourceVarNode):
                    raise SemanticAnalysisBadLValue(expr=expr.left)
                return SourceAssignmentNode(
                    start_position=expr.start_position,
                    left=self.resolve_expression(expr.left),
                    right=self.resolve_expression(expr.right),
                )
            case SourceVarNode():
                if expr.identifier in self._variable_map:
                    return SourceVarNode(
                        start_position=expr.start_position,
                        identifier=self._variable_map[expr.identifier],
                    )
                else:
                    raise SemanticAnalysisUnknownVariable(var=expr)
            case SourceConstantIntNode():
                return expr
            case SourceUnaryExpressionNode():
                return SourceUnaryExpressionNode(
                    start_position=expr.start_position,
                    operator=expr.operator,
                    expression=self.resolve_expression(expr.expression),
                )
            case SourceBinaryExpressionNode():
                return SourceBinaryExpressionNode(
                    start_position=expr.start_position,
                    operator=expr.operator,
                    left=self.resolve_expression(expr.left),
                    right=self.resolve_expression(expr.right),
                )
            case _:
                raise ValueError(f"Not recognised: {expr}")

    def resolve_blockitem(self, bi: SourceBlockItemNode) -> SourceBlockItemNode:

        match bi:
            case SourceDeclarationNode():
                return self.resolve_declaration(bi)
            case _ if isinstance(bi, get_args(SourceStatementNode)):
                return self.resolve_statement(bi)
            case _:
                raise ValueError(f"Unrecognised: {bi}")


def resolve_function(func: SourceFunctionNode) -> SourceFunctionNode:
    resolver = VariableResolver()
    updated_body: list[SourceBlockItemNode] = []
    for bi in func.body:
        nxt = resolver.resolve_blockitem(bi)
        updated_body.append(nxt)

    result = SourceFunctionNode(
        start_position=func.start_position, identifier=func.identifier, body=updated_body
    )
    return result


def resolve_program(prog: SourceProgramNode) -> SourceProgramNode:
    updated_func = resolve_function(prog.value)
    result = SourceProgramNode(start_position=prog.start_position, value=updated_func)
    return result
