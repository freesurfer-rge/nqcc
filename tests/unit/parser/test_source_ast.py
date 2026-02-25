from nqcc.parser import SourceConstantIntNode, SourceReturnNode


def test_smoke():
    n1 = SourceConstantIntNode(start_position=1, value=2)
    n2 = SourceReturnNode(start_position=2, value=n1)

    SourceConstantIntNode.last_tokens = "Hello"
    assert SourceReturnNode.last_tokens == "Hello"
