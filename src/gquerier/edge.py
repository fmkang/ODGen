from __future__ import annotations
from typing import Any, Dict, Optional
from enum import Enum

from src.core.graph import Graph

class EdgeType(str, Enum): 
    FLOWS_TO = 'FLOWS_TO'
    PARENT_OF = 'PARENT_OF'
    OBJ_TO_AST = 'OBJ_TO_AST'
    OBJ_TO_PROP = 'OBJ_TO_PROP'
    CONTRIBUTES_TO = 'CONTRIBUTES_TO'
    AST_BINARY_OP = 'AST_BINARY_OP'
    LOOKUP = 'LOOKUP'


class EdgeQuerier(object): 
    
    def __init__(self, graph: Graph, f_nid: int, t_nid: int, eid: Optional[int] = None,maxdepth: int=10) -> None:
        self.__graph: Graph = graph
        self.__properties: Dict[str, Any] = self.__graph.get_edge_attr(f_nid, t_nid, eid)
        self.maxdepth: int = maxdepth

    def get_property(self, *by_possible_names: str) -> Optional[Any]: 
        for name in by_possible_names: 
            if name not in self.__properties: continue
            return self.__properties[name]
        return None
    
    @property
    def start(self) -> Optional[int]:
        start_str = str(self.get_property('start:START_ID', 'start'))
        return int(start_str) if start_str.isnumeric() else None 

    @property
    def end(self) -> Optional[int]: 
        end_str = str(self.get_property('end:END_ID', 'end'))
        return int(end_str) if end_str.isnumeric() else None 
    
    @property
    def var(self) -> Optional[str]: 
        return self.get_property('labels:label', 'labels')

    @property
    def taint_src(self) -> Optional[str]: 
        return self.get_property('taint_src')

    @property
    def taint_dst(self) -> Optional[str]: 
        return self.get_property('taint_dst')

    @property
    def type(self) -> Optional[str]: 
        return self.get_property('type:TYPE', 'type')