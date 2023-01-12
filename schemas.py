from pydantic import BaseModel
from typing import Union, List


class AttributesBase(BaseModel):
    label: Union[str, None] = None
    x: Union[float, None] = None
    y: Union[float, None] = None
    size: Union[int, None] = 5
    color: Union[str, None] = None


class AttributesNode(AttributesBase):
    label: str
    text: Union[str, None] = None
    

class AttributesEdge(AttributesBase):
    size: int

    
class NodeBase(BaseModel):
    key: str
    attributes: AttributesNode

    
class EdgeBase(BaseModel):
    key: str
    source: str
    target: str
    attributes: AttributesEdge

    
class ResultBase(BaseModel):
    nodes: Union[List[NodeBase], List] = []
    edges: Union[List[EdgeBase], List] = []
