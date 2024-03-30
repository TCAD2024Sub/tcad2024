from typing import Tuple

import networkx as nx
from queue import Queue
from src.python.util.per_graph import PeRGraph


# from src.python.util.util import Util

class Node:
    def __init__(self, name: str):
        self.name: str = name
        self.in_queues: list[Queue] = []
        self.out_queues: list[Queue] = []

    def get_n_in_queues(self) -> int:
        if self.in_queues:
            return len(self.in_queues)
        return 0

    def create_in_queue(self):
        self.in_queues.append(Queue(1))

    def set_out_queue(self, queue: Queue):
        self.out_queues.append(queue)

    def compute(self):
        # verify if inputs are ready to give data:
        for in_queue in self.in_queues:
            if in_queue.empty():
                return
        # verify if outputs are ready to receive data:
        for out_queue in self.out_queues:
            if not out_queue.empty():
                return
        # sum all inputs
        exec_data = 0
        for in_queue in self.in_queues:
            exec_data += in_queue.get()
            # enqueue all outputs
        for out_queue in self.out_queues:
            out_queue.put(exec_data)


class InputNode(Node):
    def __init__(self, name: str, n_data: int):
        super().__init__(name)
        self.exec_data: int = 0

    def compute(self):
        # verify if outputs are ready to receive data:
        for out_queue in self.out_queues:
            if not out_queue.empty():
                return

        for out_queue in self.out_queues:
            out_queue.put(self.exec_data)
        self.exec_data += 1


class OutputNode(Node):
    def __init__(self, name: str):
        super().__init__(name)
        self.data: list = []

    def compute(self):
        # verify if inputs are ready to give data:
        for in_queue in self.in_queues:
            if in_queue.empty():
                return
                # sum all inputs
        exec_data = 0
        for in_queue in self.in_queues:
            exec_data += in_queue.get()
        self.data.append(exec_data)


class DfSimulSw:
    def __init__(self, per_graph: PeRGraph, n_data: int = 5000):
        self.per_graph: PeRGraph = per_graph
        self.n_data: int = n_data
        self.g_with_regs: nx.DiGraph = self.add_regs()
        self.input_nodes: list[InputNode] = []
        self.output_nodes: list[OutputNode] = []
        self.dataflow: list[list[Node]] = self.create_dataflow()
        self.dataflow.reverse()

    def run_simulation(self) -> list:
        df_done = False
        exec_counter = 0

        while not df_done:
            df_done = True
            for stage in self.dataflow:
                for node in stage:
                    node_name = node.name
                    node.compute()
            for output_node in self.output_nodes:
                len_output: int = len(output_node.data)
                if len_output < self.n_data:
                    df_done = False
                    break
            exec_counter += 1
        th: list = []
        for output_node in self.output_nodes:
            th.append([output_node.name, len(output_node.data) / exec_counter * 100])
        return th

    def add_regs(self) -> nx.DiGraph:
        df: nx.DiGraph = self.per_graph.g.copy()
        n_df: nx.DiGraph = df.copy()
        for edge in df.edges():
            if 'weight' not in df.edges[edge].keys():
                df.edges[edge]['weight'] = 0
            if int(df.edges[edge]['weight']) > 0:
                # df.edges[edge]['label'] = df.edges[edge]['weight']
                src = edge[0]
                dst = edge[1]
                # port = int(df.edges[edge]['port'])
                for r in range(int(df.edges[edge]['weight'])):
                    idx = '%s_%s' % edge + '_%d' % r
                    n_df.add_node(idx)
                    n_df.add_edge(src, idx)
                    nx.set_edge_attributes(n_df, {(src, idx): {'weight': 0}})
                    src = idx
                n_df.add_edge(src, dst)
                nx.set_edge_attributes(n_df, {(src, dst): {'weight': 0}})
                n_df.remove_edge(edge[0], edge[1])
        return n_df

    def find_nodes_level(self) -> tuple[dict, int]:
        g = self.g_with_regs
        level: int = 0
        queue: Queue = Queue()
        nodes_level: dict = {}
        for node in g.nodes:
            # node_name: str = str.lower(node)
            node_in_size: int = g.in_degree(node)
            if node_in_size == 0:
                queue.put([node, 0])
            else:
                continue
            while queue.qsize() > 0:
                n, l = queue.get()
                if n not in nodes_level.keys():
                    nodes_level[n] = l
                nodes_level[n] = max(l, nodes_level[n])
                level = max(level, l)
                try:
                    for succ in g._succ[n].keys():
                        # succ_name: str = str.lower(succ)
                        queue.put([succ, l + 1])
                except Exception as e:
                    a = 1
        return nodes_level, level + 1

    def create_dataflow(self) -> list[list[Node]]:
        nodes_levels, levels = self.find_nodes_level()
        g = self.g_with_regs
        dataflow: list[list[Node]] = [[] for _ in range(levels)]
        dfg_dic = {}
        visited: set = set()
        queue: Queue = Queue()
        for ini_node in g.nodes:
            # ini_node_name: str = str.lower(ini_node)
            if ini_node not in visited:
                queue.put(ini_node)
            while queue.qsize() > 0:
                no = queue.get()
                # try:
                level = nodes_levels[no]
                # except:
                    # a=1
                node_in_size: int = g.in_degree(no)
                node_out_size: int = g.out_degree(no)
                if no not in visited:
                    node: Node = self.node_factory(no, node_in_size, node_out_size)
                    dfg_dic[no] = node
                    dataflow[level].append(node)
                    visited.add(no)
                node: Node = dfg_dic[no]
                for succ in g._succ[no].keys():
                    # succ_name: str = str.lower(succ)
                    succ_in_size: int = g.in_degree(succ)
                    succ_out_size: int = g.out_degree(succ)
                    level = nodes_levels[succ]
                    if succ not in visited:
                        queue.put(succ)
                        succ_node: Node = self.node_factory(succ, succ_in_size, succ_out_size)
                        dfg_dic[succ] = succ_node
                        dataflow[level].append(succ_node)
                        visited.add(succ)
                    succ_node: Node = dfg_dic[succ]
                    succ_node.create_in_queue()
                    node.set_out_queue(succ_node.in_queues[-1])

        return dataflow

    def node_factory(self, name: str, n_inputs: int, n_outputs: int) -> Node:
        if n_inputs == 0:
            node: InputNode = InputNode(name, self.n_data)
            self.input_nodes.append(node)
            return node
        elif n_outputs == 0:
            node: OutputNode = OutputNode(name)
            self.output_nodes.append(node)
            return node
        else:
            return Node(name)

    # TODO implementar
    # Comentei pra resolver mais rápido o erro de import circular
    # def write_output_result(self, rslt: str):
    #     lines = rslt.split('\n')

    #     th = 0.0

    #     for line in lines:
    #         if 'throughput' in line:
    #             th = float(line.split(':')[2].replace(' ', '').replace('%', ''))
    #             break

    #     simul_result = {
    #         'benchmark': self.per_graph.dot_name,
    #         'throughput': th
    #     }
    # Util.save_json(self.result_path, self.result_file, simul_result)
