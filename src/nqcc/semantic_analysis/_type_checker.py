from typing import Literal, Union, get_args

from pydantic import BaseModel, Field

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


class InitialValueBase(BaseModel):
    initial_value_type: str


class Tentative(InitialValueBase):
    initial_value_type: Literal["Tentative"]


class Initial(InitialValueBase):
    initial_value_type: Literal["Initial"]
    value: int


class NoInitialiser(InitialValueBase):
    initial_value_type: Literal["NoInitialiser"]


InitialValue = Union[Tentative, Initial, NoInitialiser]


class SymbolEntry(BaseModel):
    entry_type: str


class LocalVariableType(SymbolEntry):
    entry_type: Literal["LocalVariableType"] = "LocalVariableType"
    variable_type: str


class StaticVariableType(SymbolEntry):
    entry_type: Literal["StaticVariableType"] = "StaticVariableType"
    variable_type: str
    initial_value: InitialValue
    is_global: bool


class FunctionType(BaseModel):
    entry_type: Literal["FunctionType"] = "FunctionType"
    param_count: int
    defined: bool
    is_global: bool


SymbolType = Union[LocalVariableType, StaticVariableType, FunctionType]


class SymbolTable(BaseModel):
    symbol_table: dict[str, SymbolType] = Field(default_factory=dict)

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

        self.symbol_table[source_node.identifier.identifier] = LocalVariableType(
            variable_type="int"
        )
        if source_node.initial:
            self.check_expression(source_node.initial)

    def check_function_declaration(self, source_node: SourceFunctionDeclarationNode):
        assert isinstance(source_node, SourceFunctionDeclarationNode)

        has_body = source_node.body is not None
        already_defined = False
        function_is_global = True
        if source_node.storage_class and source_node.storage_class.storage_type == "Static":
            function_is_global = False

        if source_node.identifier in self.symbol_table:
            old_decl = self.symbol_table[source_node.identifier]
            assert isinstance(old_decl, FunctionType)
            if old_decl.param_count != len(source_node.params):
                raise ValueError(f"Incompatible function declarations: {source_node}")
            already_defined = old_decl.defined
            if already_defined and has_body:
                raise ValueError(f"Function defined more than once: {source_node}")

            if (
                old_decl.is_global
                and source_node.storage_class
                and source_node.storage_class.storage_type == "Static"
            ):
                raise ValueError(f"Static function declaration follows non-static: {source_node}")

            function_is_global = old_decl.is_global

        new_symbol = FunctionType(
            param_count=len(source_node.params),
            defined=already_defined or has_body,
            is_global=function_is_global,
        )
        self.symbol_table[source_node.identifier] = new_symbol

        if source_node.body is not None:
            for p in source_node.params:
                self.symbol_table[p] = LocalVariableType(variable_type="int")
            self.check_block(source_node.body)

    def check_expression(self, source_node: SourceExpressionNode):  # noqa: C901
        assert isinstance(source_node, get_args(SourceExpressionNode))

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
                if not isinstance(v_symbol, (LocalVariableType, StaticVariableType)):
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

    def check_statement(self, source_node: SourceStatementNode):  # noqa: C901
        match source_node:
            case SourceNullStatementNode():
                pass
            case SourceReturnNode():
                self.check_expression(source_node.value)
            case SourceExpressionStatementNode():
                self.check_expression(source_node.value)
            case SourceIfStatementNode():
                self.check_expression(source_node.condition)
                self.check_statement(source_node.then)
                if source_node.otherwise:
                    self.check_statement(source_node.otherwise)
            case SourceCompoundNode():
                self.check_block(source_node.block)
            case SourceWhileNode():
                self.check_expression(source_node.condition)
                self.check_statement(source_node.body)
            case SourceDoWhileNode():
                self.check_expression(source_node.condition)
                self.check_statement(source_node.body)
            case SourceForNode():
                self.check_forinit(source_node.init)
                if source_node.condition:
                    self.check_expression(source_node.condition)
                if source_node.post:
                    self.check_expression(source_node.post)
                self.check_statement(source_node.body)
            case SourceBreakNode() | SourceContinueNode():
                pass
            case _:
                raise ValueError(f"Unrecognised: {source_node}")

    def check_forinit(self, source_node: SourceForInitNode):
        match source_node:
            case SourceInitDeclNode():
                self.check_variable_declaration(source_node.decl)
            case SourceInitExpressionNode():
                if source_node.expression:
                    self.check_expression(source_node.expression)

    def check_program(self, source_node: SourceProgramNode):
        for f in source_node.declarations:
            self.check_declaration(f)
