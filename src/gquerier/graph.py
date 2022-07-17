from collections import deque
from typing import Callable, Generator, Iterator, Optional, Tuple
from src.core.logger import loggers
from src.core.graph import Graph
from .edge import EdgeQuerier, EdgeType
from .node import NodeQuerier, NodeType

NodeCondition = Callable[[NodeQuerier], bool]
EdgeNodeCondition = Callable[[EdgeQuerier, NodeQuerier], bool]
NodesQueryResult = Generator[NodeQuerier, None, None]

class GraphQuerier(object): 

    def __init__(self, target: Graph, maxdepth: int=10) -> None:
        self.__graph: Graph = target
        self.__maxdepth: int = maxdepth

    @property
    def graph(self) -> Graph: 
        return self.__graph

    def node(self, whose_id_is: str) -> Optional[NodeQuerier]:
        try: 
            return NodeQuerier(self.__graph, str(whose_id_is))
        except Exception as e: 
            loggers.instance.error_logger.info(f'{GraphQuerier} ERROR: access node {whose_id_is} {str(e)}')
            return None

    def find_node(self, whose_satisifies: NodeCondition) -> Optional[NodeQuerier]: 
        all_nodes = self.find_all_nodes(whose_satisifies)
        try: return next(all_nodes)
        except StopIteration: return None

    def find_all_nodes(self, whose_satisifies: NodeCondition) -> NodesQueryResult: 
        for nid in self.graph.graph.nodes: 
            if whose_satisifies(self.node(nid)): yield self.node(nid)
        return None

    def next(self, of: NodeQuerier, condition: EdgeNodeCondition = lambda e,n:True) -> NodesQueryResult: 
        next_nids = ((data[1], data[2]) for data in self.__graph.get_out_edges(of.id, data=False))
        next_e_n_list = ((
            EdgeQuerier(self.__graph, of.id, tid, eid, self.__maxdepth), 
            NodeQuerier(self.__graph, tid, self.__maxdepth)
        ) for tid, eid in next_nids)
        return (node for edge, node in next_e_n_list if condition(edge, node))
        
    def prev(self, of: NodeQuerier, condition: EdgeNodeCondition = lambda e,n:True) -> Iterator[NodeQuerier]: 
        prev_nids = ((data[0], data[2]) for data in self.__graph.get_in_edges(of.id, data=False))
        prev_e_n_list = ((
            EdgeQuerier(self.__graph, fid, of.id, eid, self.__maxdepth), 
            NodeQuerier(self.__graph, fid, self.__maxdepth)
        ) for fid, eid in prev_nids)
        return (node for edge, node in prev_e_n_list if condition(edge, node))

    def branch_flow_start(self, if_elem: NodeQuerier) -> Optional[NodeQuerier]:
        try: 
            stmt_list = next(self.ast_children(if_elem, lambda _,n: n.type == NodeType.AST_STMT_LIST))
            return next(self.ast_children(stmt_list))
        except Exception as e: 
            loggers.instance.error_logger.info(f'{GraphQuerier} ERROR: search branch {if_elem} {str(e)}')
            return None
        

    def ast_children(self, of: NodeQuerier, extra:EdgeNodeCondition = lambda e,n:True) -> NodesQueryResult: 
        '''
        return the next nodes connected with the input one.
        The edge type between them is PARENT_OF 
        '''
        condition = lambda e, n: extra(e,n) and (e.type == EdgeType.PARENT_OF)
        return self.next(of, condition)

    def flow_from(self, node: NodeQuerier, extra: EdgeNodeCondition = lambda e,n:True) -> NodesQueryResult: 
        '''
        return the next nodes connected with the input one.
        The edge type between them is FLOW_TO 
        '''
        condition = lambda e, n: extra(e,n) and (e.type == EdgeType.FLOWS_TO)
        return self.next(of=node, condition=condition)

    def flow_to(self, node: NodeQuerier, extra: EdgeNodeCondition = lambda e,n:True) -> NodesQueryResult:
        '''
        return the previous nodes connected with the input one.
        The edge type between them is FLOW_TO 
        '''
        condition = lambda e, n: extra(e,n) and (e.type == EdgeType.FLOWS_TO)
        return self.prev(of=node, condition=condition)

    def bfs_nodes(self, src: NodeQuerier, condition: EdgeNodeCondition = lambda e,n:True) -> NodesQueryResult: 
        if src is None: return 
        visited_nodes, nodes_queue = set(), deque([src, None])
        visted_condition = lambda e, n: condition(e, n) and n.id not in visited_nodes
        depth = self.__maxdepth
        while depth != 0 and len(nodes_queue) > 1: 
            cur = nodes_queue.popleft()
            if cur == None: 
                nodes_queue.append(None)
                depth -= 1
            elif cur.id not in visited_nodes:
                visited_nodes.add(cur.id)
                n_nodes = list(self.next(cur, visted_condition))
                nodes_queue.extend(n_nodes)
                if src != cur: yield cur

    def bfs_flow_from(self, src: NodeQuerier, extra: EdgeNodeCondition = lambda e,n:True) -> NodesQueryResult: 
        return self.bfs_nodes(src, lambda e, n: e.type == EdgeType.FLOWS_TO and extra(e, n))
