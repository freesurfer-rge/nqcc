from typing import Union, get_args

from pydantic import BaseModel

from nqcc.parser import (
    SourceBlockItemNode,
    SourceBlockNode,
    SourceConstantIntNode,
    SourceBinaryExpressionNode,
    SourceUnaryExpressionNode,
    SourceBreakNode,
    SourceCompoundNode,
    SourceContinueNode,
    SourceDoWhileNode,
    SourceForNode,
    SourceFunctionDeclarationNode,
    SourceIfStatementNode,
    SourceProgramNode,
    SourceStatementNode,
    SourceAssignmentNode,
    SourceTernaryExpressonNode,
    SourceWhileNode,
    SourceDeclarationNode,
    SourceVariableDeclarationNode,
    SourceExpressionNode,
    SourceFunctionCallNode,
    SourceVarNode,SourceReturnNode,SourceNullStatementNode
)


class VariableInt:
    pass

class VariableNotATypeForUnion:
    # This is so get_args(VariableType) works
    pass


VariableType = Union[VariableInt,VariableNotATypeForUnion]


class FunctionType(BaseModel):
    param_count: int
    defined: bool


SymbolType = Union[VariableType, FunctionType]


class SymbolTable:
    def __init__(self) -> None:
        self.symbol_table: dict[str, SymbolType] = {}

    def check_declaration(self, source_node: SourceDeclarationNode):
        match source_node:
            case SourceVariableDeclarationNode():
                self.check_variable_declaration(source_node)
            case SourceFunctionDeclarationNode():
                self.check_function_declaration(source_node)
            case _:
                raise ValueError(f"Unrecognised: {source_node}")

    def check_variable_declaration(self, source_node: SourceVariableDeclarationNode):
        assert isinstance(source_node, SourceVariableDeclarationNode)
        # We should have fully unique names by this point.....
        assert source_node.identifier.identifier not in self.symbol_table

        self.symbol_table[source_node.identifier.identifier] = VariableInt()
        if source_node.initial:
            self.check_expression(source_node.initial)

    def check_function_declaration(self, source_node: SourceFunctionDeclarationNode):
        assert isinstance(source_node, SourceFunctionDeclarationNode)

        has_body = source_node.body is not None
        already_defined = False

        if source_node.identifier in self.symbol_table:
            old_decl = self.symbol_table[source_node.identifier]
            assert isinstance(old_decl, FunctionType)
            if old_decl.param_count != len(source_node.params):
                raise ValueError(f"Incompatible function declarations: {source_node}")
            already_defined = old_decl.defined
            if already_defined and has_body:
                raise ValueError(f"Function defined more than once: {source_node}")

        new_symbol = FunctionType(
            param_count=len(source_node.params), defined=already_defined or has_body
        )
        self.symbol_table[source_node.identifier] = new_symbol

        if has_body:
            for p in source_node.params:
                self.symbol_table.add(p, VariableInt())
            self.check_block(source_node.body)

    def check_expression(self, source_node: SourceExpressionNode):
        assert isinstance(source_node, SourceExpressionNode)

        match source_node:
            case SourceFunctionCallNode():
                f_symbol = self.symbol_table[source_node.identifier]
                if not isinstance(f_symbol, FunctionType):
                    raise ValueError(f"Variable used as function name: {source_node}")
                assert isinstance(f_symbol, FunctionType)
                if f_symbol.param_count != len(source_node.args):
                    raise ValueError(f"Wrong arg count: {source_node}")
                for arg in source_node.args:
                    self.check_expression(arg)
            case SourceVarNode():
                v_symbol = self.symbol_table[source_node.identifier]
                if not isinstance(v_symbol, get_args(VariableType)):
                    raise ValueError(f"Function name used as variable: {source_node}")
            case SourceConstantIntNode():
                pass
            case SourceUnaryExpressionNode():
                self.check_expression(source_node.expression)
            case SourceBinaryExpressionNode():
                self.check_expression(source_node.left)
                self.check_expression(source_node.right)
            case SourceAssignmentNode():
                self.check_expression(source_node.left)
                self.check_expression(source_node.right)
            case SourceTernaryExpressonNode():
                self.check_expression(source_node.condition)
                self.check_expression(source_node.then)
                self.check_expression(source_node.otherwise)
            case _:
                raise ValueError(f"Unrecogised: {source_node}")

    def check_block(self, source_node: SourceBlockNode):
        assert isinstance(source_node, SourceBlockNode)

        for bi in source_node.items:
            self.check_blockitem(bi)

    def check_blockitem(self, source_node: SourceBlockItemNode):
        match source_node:
            case _ if isinstance(source_node, get_args(SourceDeclarationNode)):
                self.check_declaration(source_node)
            case _ if isinstance(source_node, get_args(SourceStatementNode)):
                self.check_statement(source_node)
            case _:
                raise ValueError(f"Unrecognised: {source_node}")

    def check_statement(self,source_node: SourceStatementNode):
        match source_node:
            case SourceNullStatementNode():
                pass
            case SourceReturnNode():
                self.check_expression(source_node.value)

    def check_program(self, source_node: SourceProgramNode):
        for f in source_node.functions:
            self.check_declaration(f)
