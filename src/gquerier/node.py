from __future__ import annotations
from typing import Any, Tuple, Dict, List, Optional
from enum import Enum

from src.core.graph import Graph

NameSpace = Tuple[Tuple[int, int], Tuple[int, int]]

class NodeType(str, Enum): 
    AST_CALL = 'AST_CALL'
    AST_ASSIGN = 'AST_ASSIGN'
    AST_BINARY_OP = 'AST_BINARY_OP'
    AST_IF = 'AST_IF'
    AST_IF_ELEM = 'AST_IF_ELEM'
    AST_STMT_LIST = 'AST_STMT_LIST'
    AST_FUNC_DECL = 'AST_FUNC_DECL'
    BASE_SCOPE = 'BASE_SCOPE'

class NodeQuerier(object):  
    
    def __init__(self, graph: Graph, nid: str,  maxdepth: int=10) -> None:
        self.__nid: str = str(nid)
        self.__graph: Graph = graph
        self.__properties: Dict[str, Any] = self.__graph.get_node_attr(self.__nid)
        self.maxdepth: int = maxdepth

    def get_property(self, *by_possible_names: str) -> Optional[Any]: 
        for name in by_possible_names: 
            if name not in self.__properties: continue
            return self.__properties[name]
        return None
    
    @property
    def nextworkx_core(self) -> Dict[str, Any]: 
        return self.__properties
    
    @property
    def id(self) -> str: return self.__nid

    @property
    def code(self) -> Optional[str]: 
        return self.get_property('code')
    
    @property
    def label(self) -> Optional[str]: 
        return self.get_property('labels:label', 'labels')
    
    @property
    def flags(self) -> List[str]: 
        flags_str = self.get_property('flags:string[]', 'flags')
        return str(flags_str).split(' ') if flags_str is not None else []
    
    @property
    def line_num(self) -> Optional[int]: 
        linenum_str = str(self.get_property('lineno:int', 'lineno'))
        return int(linenum_str) if linenum_str.isnumeric() else None
    
    @property
    def children_num(self) -> Optional[int]: 
        num_str = str(self.get_property('childnum:int', 'childnum'))
        return int(num_str) if num_str.isnumeric() else None

    @property
    def func_id(self) -> Optional[int]: 
        fid_str = str(self.get_property('funcid:int', 'funcid'))
        return int(fid_str) if fid_str.isnumeric() else None
    
    @property
    def class_name(self) -> Optional[str]: 
        return self.get_property('classname')

    @property
    def namespace(self) -> Optional[NameSpace]: 
        ns_str = self.get_property('namespace')
        if ns_str is None: return None
        ns_list = ns_str.split(':')
        if len(ns_list) != 4: return None
        ns_list = [int(n_str) if n_str.isnumeric() else 0 for n_str in ns_list]
        return ((ns_list[0], ns_list[1]), (ns_list[2],ns_list[3]))
        
    @property
    def name(self) -> Optional[str]: return self.get_property('name')

    @property
    def end_num(self) -> Optional[int]:
        end_str = str(self.get_property('endlineno:int', 'endlineno'))
        return int(end_str) if end_str.isnumeric() else None

    @property
    def comment(self) -> Optional[str]: 
        return self.get_property('doccomment')

    @property 
    def type(self) -> Optional[str]: return self.get_property('type')
