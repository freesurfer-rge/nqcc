import pytest

from nqcc.parser import (
    SourceBlockNode,
    SourceConstantIntNode,
    SourceFunctionDeclarationNode,
    SourceReturnNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    TokenTape,
    parse_declaration,
)
from nqcc.semantic_analysis import (
    IdentifierResolver,
    SemanticAnalysisDuplicateDeclaration,
)


class TestVariableDeclarations:
    def test_smoke_no_init(self):
        target = IdentifierResolver()
        identifier_map = {}

        decl = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
            storage_class=None,
        )

        updated = target.resolve_declaration(decl, identifier_map)
        assert isinstance(updated, SourceVariableDeclarationNode)
        assert updated.start_position == 10
        assert updated.identifier == SourceVarNode(start_position=11, identifier="a.0")
        assert updated.initial is None
        assert len(identifier_map) == 1

    def test_decl_with_init(self):
        target = IdentifierResolver()
        identifier_map = {}

        program_str = "int a = 1;"

        token_tape = TokenTape.from_c_source(program_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceVariableDeclarationNode)

        result = target.resolve_declaration(decl, identifier_map)
        assert isinstance(result, SourceVariableDeclarationNode)
        assert result.start_position == 0
        assert result.identifier == SourceVarNode(start_position=4, identifier="a.0")
        assert isinstance(result.initial, SourceConstantIntNode)
        assert result.initial.value == 1
        assert len(identifier_map) == 1

    def test_two_decl(self):
        target = IdentifierResolver()

        decl0 = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
            storage_class=None,
        )

        identifier_map = {}
        updated0 = target.resolve_declaration(decl0, identifier_map)
        assert isinstance(updated0, SourceVariableDeclarationNode)
        assert updated0.start_position == 10
        assert updated0.identifier == SourceVarNode(start_position=11, identifier="a.0")
        assert updated0.initial is None

        decl1 = SourceVariableDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="b"),
            initial=None,
            storage_class=None,
        )

        updated1 = target.resolve_declaration(decl1, identifier_map)
        assert isinstance(updated1, SourceVariableDeclarationNode)
        assert updated1.start_position == 12
        assert updated1.identifier == SourceVarNode(start_position=13, identifier="b.1")
        assert updated1.initial is None

    def test_duplicate_name(self):
        target = IdentifierResolver()
        identifier_map = {}

        decl0 = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
            storage_class=None,
        )
        _ = target.resolve_declaration(decl0, identifier_map)

        decl1 = SourceVariableDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="a"),
            initial=None,
            storage_class=None,
        )

        with pytest.raises(SemanticAnalysisDuplicateDeclaration) as saduperr:
            _ = target.resolve_declaration(decl1, identifier_map)
        assert saduperr.value.decl == decl1
        assert saduperr.value.message == "Duplicate declaration of 'a' at 12"


class TestFunctionDeclarations:
    def test_noargs_nobody(self):
        target = IdentifierResolver()
        identifier_map = {}

        decl = SourceFunctionDeclarationNode(
            start_position=123,
            identifier="some_func",
            params=[],
            body=None,
            storage_class=None,
        )

        result = target.resolve_declaration(decl, identifier_map)
        assert result.start_position == decl.start_position
        assert result.identifier == decl.identifier
        assert len(result.params) == 0
        assert result.body is None

        assert "some_func" in identifier_map
        assert identifier_map["some_func"].name == "some_func"
        assert identifier_map["some_func"].from_current_scope
        assert identifier_map["some_func"].has_linkage

    def test_arg_nobody(self):
        target = IdentifierResolver()
        identifier_map = {}

        decl = SourceFunctionDeclarationNode(
            start_position=123,
            identifier="some_func",
            params=["a"],
            body=None,
            storage_class=None,
        )

        result = target.resolve_declaration(decl, identifier_map)
        assert result.start_position == decl.start_position
        assert result.identifier == decl.identifier
        assert len(result.params) == 1
        assert result.params[0] == "a.arg.0"
        assert result.body is None

        assert "some_func" in identifier_map
        assert identifier_map["some_func"].name == "some_func"
        assert identifier_map["some_func"].from_current_scope
        assert identifier_map["some_func"].has_linkage

    def test_arg_body(self):
        target = IdentifierResolver()
        identifier_map = {}

        c_str = """int some_func(int a) { return a; }"""

        token_tape = TokenTape.from_c_source(c_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceFunctionDeclarationNode)

        result = target.resolve_declaration(decl, identifier_map)
        assert result.start_position == decl.start_position
        assert result.identifier == decl.identifier
        assert len(result.params) == 1
        assert result.params[0] == "a.arg.0"
        assert isinstance(result.body, SourceBlockNode)
        assert len(result.body.items) == 1
        ret_node = result.body.items[0]
        assert isinstance(ret_node, SourceReturnNode)
        assert ret_node.value == SourceVarNode(start_position=30, identifier="a.arg.0")

        assert "some_func" in identifier_map
        assert identifier_map["some_func"].name == "some_func"
        assert identifier_map["some_func"].from_current_scope
        assert identifier_map["some_func"].has_linkage

    def test_twoarg_nobody(self):
        target = IdentifierResolver()
        identifier_map = {}

        c_str = """int some_func(int a, int b);"""

        token_tape = TokenTape.from_c_source(c_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceFunctionDeclarationNode)

        result = target.resolve_declaration(decl, identifier_map)
        assert result.start_position == decl.start_position
        assert result.identifier == decl.identifier
        assert len(result.params) == 2
        assert result.params[0] == "a.arg.0"
        assert result.params[1] == "b.arg.1"
        assert result.body is None

    def test_param_unique_names(self):
        target = IdentifierResolver()
        identifier_map = {}

        c_str = """int some_func(int a, int a);"""

        token_tape = TokenTape.from_c_source(c_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceFunctionDeclarationNode)

        with pytest.raises(ValueError, match="parameter a already defined"):
            _ = target.resolve_declaration(decl, identifier_map)

    def test_param_redeclared_in_body(self):
        target = IdentifierResolver()
        identifier_map = {}

        c_str = """int some_func(int a) { int a = 0; return 2;}"""

        token_tape = TokenTape.from_c_source(c_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceFunctionDeclarationNode)

        with pytest.raises(ValueError, match="Duplicate declaration of 'a'"):
            _ = target.resolve_declaration(decl, identifier_map)
