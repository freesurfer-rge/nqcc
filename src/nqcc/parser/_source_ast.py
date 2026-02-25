import abc
import string
from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field

class SourceASTNode(BaseModel, abc.ABC):
    type: str
    start_position: int


class SourceExpressionNode(SourceASTNode):
    pass

class SourceConstantIntNode(SourceExpressionNode):
    type: Literal["SourceConstantIntNode"] = "SourceConstantIntNode"
    value: int

class SourceStatementNode(SourceASTNode):
    pass

class SourceReturnNode(SourceStatementNode):
    type: Literal["SourceReturnNode"] = "SourceReturnNode"
    value: SourceExpressionNode

class SourceFunctionDefinitionNode(SourceASTNode):
    pass

class SourceFunctionNode(SourceFunctionDefinitionNode):
    type: Literal["SourceFunctionNode"] = "SourceFunctionNode"
    identifier: str
    body: SourceStatementNode

class SourceProgramDefinitionNode(SourceASTNode):
    pass

class SourceProgramNode(SourceProgramDefinitionNode):
    type: Literal["SourceProgramNode"] = "SourceProgramNode"
    value: SourceFunctionDefinitionNode