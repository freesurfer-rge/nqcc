import pytest

from nqcc.parser import (
    SourceBlockNode,
    SourceConstantIntNode,
    SourceFunctionDeclarationNode,
    SourceReturnNode,
    SourceStorageType,
    SourceVariableDeclarationNode,
    SourceVarNode,
    TokenTape,
    parse_declaration,
)
from nqcc.semantic_analysis import (
    IdentifierResolver,
    SemanticAnalysisDuplicateDeclaration,
    IdentifierInfo,
)


class TestVariableDeclarations:
    @pytest.mark.parametrize("at_file_scope", [False, True])
    def test_smoke_no_init(self, at_file_scope: bool):
        target = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        decl = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
            storage_class=None,
        )

        updated = target.resolve_declaration(decl, identifier_map, at_file_scope=at_file_scope)
        assert isinstance(updated, SourceVariableDeclarationNode)
        assert updated.start_position == 10
        expected_identifier = "a" if at_file_scope else "a.0"
        assert updated.identifier == SourceVarNode(
            start_position=11, identifier=expected_identifier
        )
        assert updated.initial is None
        assert len(identifier_map) == 1
        var_id = identifier_map["a"]
        assert var_id.name == expected_identifier
        assert var_id.from_current_scope
        assert var_id.has_linkage == at_file_scope

    @pytest.mark.parametrize("at_file_scope", [False, True])
    def test_decl_with_init(self, at_file_scope: bool):
        target = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        program_str = "int a = 1;"

        token_tape = TokenTape.from_c_source(program_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceVariableDeclarationNode)

        result = target.resolve_declaration(decl, identifier_map, at_file_scope=at_file_scope)
        assert isinstance(result, SourceVariableDeclarationNode)
        assert result.start_position == 0
        expected_identifier = "a" if at_file_scope else "a.0"
        assert result.identifier == SourceVarNode(start_position=4, identifier=expected_identifier)
        assert isinstance(result.initial, SourceConstantIntNode)
        assert result.initial.value == 1
        assert len(identifier_map) == 1

    @pytest.mark.parametrize("at_file_scope", [False, True])
    def test_two_decl(self, at_file_scope: bool):
        target = IdentifierResolver()

        decl0 = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
            storage_class=None,
        )

        identifier_map: dict[str, IdentifierInfo] = {}
        updated0 = target.resolve_declaration(decl0, identifier_map, at_file_scope=at_file_scope)
        assert isinstance(updated0, SourceVariableDeclarationNode)
        assert updated0.start_position == 10
        expected_identifier = "a" if at_file_scope else "a.0"
        assert updated0.identifier == SourceVarNode(
            start_position=11, identifier=expected_identifier
        )
        assert updated0.initial is None

        decl1 = SourceVariableDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="b"),
            initial=None,
            storage_class=None,
        )

        updated1 = target.resolve_declaration(decl1, identifier_map, at_file_scope=at_file_scope)
        assert isinstance(updated1, SourceVariableDeclarationNode)
        assert updated1.start_position == 12
        expected_identifier = "b" if at_file_scope else "b.1"
        assert updated1.identifier == SourceVarNode(
            start_position=13, identifier=expected_identifier
        )
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
        _ = target.resolve_declaration(decl0, identifier_map, at_file_scope=False)

        decl1 = SourceVariableDeclarationNode(
            start_position=12,
            identifier=SourceVarNode(start_position=13, identifier="a"),
            initial=None,
            storage_class=None,
        )

        with pytest.raises(SemanticAnalysisDuplicateDeclaration) as saduperr:
            _ = target.resolve_declaration(decl1, identifier_map, at_file_scope=False)
        assert saduperr.value.decl == decl1
        assert saduperr.value.message == "Duplicate declaration of 'a' at 12"

    def test_extern_decl(self) -> None:
        target = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        decl = SourceVariableDeclarationNode(
            start_position=10,
            identifier=SourceVarNode(start_position=11, identifier="a"),
            initial=None,
            storage_class=SourceStorageType(storage_type="Extern"),
        )
        updated = target.resolve_declaration(decl, identifier_map, at_file_scope=False)
        assert updated == decl
        assert len(identifier_map) == 1
        var_id = identifier_map["a"]
        assert var_id.name == "a"
        assert var_id.from_current_scope
        assert var_id.has_linkage


class TestFunctionDeclarations:
    def test_noargs_nobody(self) -> None:
        target = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        decl = SourceFunctionDeclarationNode(
            start_position=123,
            identifier="some_func",
            params=[],
            body=None,
            storage_class=None,
        )

        result = target.resolve_declaration(decl, identifier_map, at_file_scope=False)
        assert isinstance(result, SourceFunctionDeclarationNode)
        assert result.start_position == decl.start_position
        assert result.identifier == decl.identifier
        assert len(result.params) == 0
        assert result.body is None

        assert "some_func" in identifier_map
        assert identifier_map["some_func"].name == "some_func"
        assert identifier_map["some_func"].from_current_scope
        assert identifier_map["some_func"].has_linkage

    @pytest.mark.parametrize("at_file_scope", [False, True])
    def test_arg_nobody(self, at_file_scope: bool):
        target = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        decl = SourceFunctionDeclarationNode(
            start_position=123,
            identifier="some_func",
            params=["a"],
            body=None,
            storage_class=None,
        )

        result = target.resolve_declaration(decl, identifier_map, at_file_scope=at_file_scope)
        assert isinstance(result, SourceFunctionDeclarationNode)
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

        result = target.resolve_declaration(decl, identifier_map, at_file_scope=True)
        assert isinstance(result, SourceFunctionDeclarationNode)
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

    @pytest.mark.parametrize("at_file_scope", [False, True])
    def test_twoarg_nobody(self, at_file_scope: bool):
        target = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        c_str = """int some_func(int a, int b);"""

        token_tape = TokenTape.from_c_source(c_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceFunctionDeclarationNode)

        result = target.resolve_declaration(decl, identifier_map, at_file_scope=at_file_scope)
        assert isinstance(result, SourceFunctionDeclarationNode)
        assert result.start_position == decl.start_position
        assert result.identifier == decl.identifier
        assert len(result.params) == 2
        assert result.params[0] == "a.arg.0"
        assert result.params[1] == "b.arg.1"
        assert result.body is None

    @pytest.mark.parametrize("at_file_scope", [False, True])
    def test_param_unique_names(self, at_file_scope: bool):
        target = IdentifierResolver()
        identifier_map: dict[str, IdentifierInfo] = {}

        c_str = """int some_func(int a, int a);"""

        token_tape = TokenTape.from_c_source(c_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceFunctionDeclarationNode)

        with pytest.raises(ValueError, match="parameter a already defined"):
            _ = target.resolve_declaration(decl, identifier_map, at_file_scope=at_file_scope)

    def test_param_redeclared_in_body(self):
        target = IdentifierResolver()
        identifier_map = {}

        c_str = """int some_func(int a) { int a = 0; return 2;}"""

        token_tape = TokenTape.from_c_source(c_str)
        decl = parse_declaration(token_tape)
        assert isinstance(decl, SourceFunctionDeclarationNode)

        with pytest.raises(ValueError, match="Duplicate declaration of 'a'"):
            _ = target.resolve_declaration(decl, identifier_map, at_file_scope=True)
