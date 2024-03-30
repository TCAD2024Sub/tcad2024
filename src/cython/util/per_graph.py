from collections import defaultdict
from typing import List, Tuple, Dict, Any

import pygraphviz as pgv
import networkx as nx
import random
from math import ceil, sqrt


class PeRGraph:

    def __init__(self, dot_path: str, dot_name: str):
        """
        Initializes the PeRGraph object.

        Parameters:
            dot_path (str): Path to the DOT file.
            dot_name (str): Name of the DOT file.
        """
        self.dot_path: str = dot_path
        self.dot_name: str = dot_name
        self.gv: pgv.AGraph = pgv.AGraph(self.dot_path, strict=False, directed=True)
        self.g: nx.DiGraph = nx.DiGraph(self.gv)
        self.nodes: List[str] = list(self.g.nodes)
        self.n_nodes: int = len(self.nodes)
        self.edges_str: List[Tuple[str, str]] = list(self.g.edges)
        self.n_edges: int = len(self.edges_str)
        self.nodes_to_idx: Dict[str, int] = {}
        self.neighbors: Dict[int, List[int]] = defaultdict(list)
        self.n_cells: int = 0
        self.n_cells_sqrt: int = 0
        self.get_dot_vars()

    def get_dot_vars(self):
        """
        Extracts variables from the DOT graph.
        """
        for i, node in enumerate(self.nodes):
            self.nodes_to_idx[node] = i

        for e in self.edges_str:
            idx_0 = self.nodes_to_idx[e[0]]
            idx_1 = self.nodes_to_idx[e[1]]
            self.neighbors[idx_0].append(idx_1)
            self.neighbors[idx_1].append(idx_0)

        self.n_cells_sqrt = ceil(sqrt(self.n_nodes))
        self.n_cells = pow(self.n_cells_sqrt, 2)

    # FIXME
    def get_edges_depth_first(self) -> list[list]:
        """_summary_
            Returns a list of edges according
            to the depth first algorithm

        Args:
            self (_type_): _description_

        Returns:
            _type_: _description_
            @return:
            @rtype:
        """
        temp_edges: list = list(self.g.edges)
        r_edges: list = []

        # finding the bottom node (with no successors)
        lower_node: str = ""
        for p in self.g._succ:
            if len(self.g._succ[p]) == 0:
                lower_node = p
                break

        # creating the edges list
        r: str = lower_node
        q: list = [r]
        working: bool = True
        while working:
            working = False
            for e in temp_edges:
                if e[1] == r:
                    r_edges.append([e[1], e[0]])
                    temp_edges.remove(e)
                    q.append(e[0])
                    r = e[0]
                    working = True
                    break
            if q and temp_edges and not working:
                q = q[:-1]
                if q:
                    r = q[-1]
                    working = True
                '''elif edges:
                        q.append(edges[0][0])
                        r = edges[0][0]
                        working = True'''
        return r_edges

    def get_edges_zigzag(self, make_shuffle: bool = True) -> tuple[list[list[str]], list[list[str]], list[list[Any]]]:
        """
        Returns a list of edges according to the zigzag algorithm.

        Args:
            make_shuffle (bool): Whether to shuffle the output list.

        Returns:
            Tuple containing three lists: edges_str, edges_raw, and convergence.
        """

        output_list = [[node, 'IN'] for node in self.g.nodes() if self.g.out_degree(node) == 0]

        if make_shuffle:
            random.shuffle(output_list)

        stack = output_list.copy()
        edges = []
        visited = set()
        convergence = []

        fan_in = {node: list(self.g.predecessors(node)) for node in self.g.nodes()}
        fan_out = {node: list(self.g.successors(node)) for node in self.g.nodes()}

        if make_shuffle:
            for node in self.g.nodes():
                random.shuffle(fan_in[node])
                random.shuffle(fan_out[node])

        while stack:
            a, direction = stack.pop(0)  # get the top1
            visited.add(a)

            if direction == 'IN':  # direction == 'IN'

                if fan_out[a]:  # Case 3
                    b = fan_out[a][-1]
                    stack.insert(0, [a, 'IN'])
                    stack[:0] = [[a, 'IN']] * len(fan_in[a])
                    stack.insert(0, [b, 'OUT'])
                    fan_out[a].remove(b)
                    fan_in[b].remove(a)
                    if b in visited:
                        convergence.append([a, b])
                    edges.append([a, b, 'OUT'])

                elif fan_in[a]:  # Case 2
                    b = fan_in[a][-1]
                    stack.insert(0, [a, 'IN'])
                    stack[:0] = [[b, 'IN']] * len(fan_in[a])
                    fan_in[a].remove(b)
                    fan_out[b].remove(a)
                    if b in visited:
                        convergence.append([a, b])
                    edges.append([a, b, 'IN'])

            else:  # direction == 'OUT'

                if fan_in[a]:  # Case 3
                    b = fan_in[a][0]
                    stack.insert(0, [a, 'OUT'])
                    stack[:0] = [[a, 'OUT']] * len(fan_out[a])
                    stack.insert(0, [b, 'IN'])
                    fan_in[a].remove(b)
                    fan_out[b].remove(a)
                    if b in visited:
                        convergence.append([a, b])
                    edges.append([a, b, 'IN'])

                elif fan_out[a]:  # Case 2
                    b = fan_out[a][0]
                    stack.insert(0, [a, 'OUT'])
                    stack[:0] = [[b, 'OUT']] * len(fan_out[a])
                    fan_out[a].remove(b)
                    fan_in[b].remove(a)
                    if b in visited:
                        convergence.append([a, b])
                    edges.append([a, b, 'OUT'])

        return self.clear_edges(edges), self.clear_edges(edges, False), convergence

    @staticmethod
    def clear_edges(edges: List[List[str]], remove_placed_edges: bool = True) -> List[List[str]]:
        """
        Removes duplicate edges from the list.

        Args:
            edges (List[List[str]]): List of edges.
            remove_placed_edges (bool): Whether to remove placed edges.

        Returns:
            List[List[str]]: List of unique edges.
        """
        dic = set()
        dic.add(edges[0][0])
        new_edges = []
        for edge in edges:
            n1, n2 = edge[:2]
            if n2 not in dic or not remove_placed_edges:
                dic.add(n2)
                new_edges.append([n1, n2])
        return new_edges
