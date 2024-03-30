from math import log2, sqrt, ceil
from random import choice
from src.python.stat_scripts.graph_generator.placement import Placement
from src.python.stat_scripts.graph_generator.router import Router


class GraphGenerator:
    @staticmethod
    def generate_random_dag_graph(num_vertexes: int, adj_list: list[tuple[int, int]]):
        vertexes = [i for i in range(num_vertexes)]
        dim_arch = int(ceil(sqrt(num_vertexes)))

        pes = [(i, j) for i in range(dim_arch) for j in range(dim_arch)]

        placement_n2c, placement_c2n = Placement.random_placement(vertexes, pes)

        vertex = choice(list(placement_n2c.keys()))

        routing = Router.create_dag_by_pe(placement_c2n, placement_n2c[vertex], adj_list)

        dfg_edges = []
        for (a, b) in routing:
            dfg_edges.append((placement_c2n[a], placement_c2n[b]))

        return vertexes, dfg_edges, placement_c2n

    @staticmethod
    def generate_random_tree_graph(num_vertexes: int, adj_list: list[tuple[int, int]]):
        vertexes = [i for i in range(num_vertexes)]
        dim_arch = int(ceil(sqrt(num_vertexes)))

        pes = [(i, j) for i in range(dim_arch) for j in range(dim_arch)]

        placement_n2c, placement_c2n = Placement.random_placement(vertexes, pes)

        vertex = choice(list(placement_n2c.keys()))

        routing = Router.create_tree_by_pe(placement_c2n, placement_n2c[vertex], adj_list)

        dfg_edges = []
        for (a, b) in routing:
            dfg_edges.append((placement_c2n[a], placement_c2n[b]))

        return vertexes, dfg_edges, placement_c2n

    @staticmethod
    def generate_binary_tree(height):
        num_nodes = 2 ** height - 1
        vertexes = [0 for _ in range(num_nodes)]
        dfg_edges = []
        count = 0
        fifo = [0]

        while len(fifo) != 0:
            cur_node = fifo.pop(0)
            dfg_edges.append((cur_node, count + 1))
            dfg_edges.append((cur_node, count + 2))
            count += 2
            if log2(count) < height:
                fifo.append(count - 1)
                fifo.append(count)

        return vertexes, dfg_edges

    # @staticmethod
    # def generate_random_tree_min_dist_one(num_vertexes:int,adj_list:list[tuple[int,int]]):
    #     def any_out_of_border(pe, square_pes,len_pes):
    #         for adj in square_pes:
    #             adj_pe = (pe[0]+adj[0],pe[1]+adj[1])
    #             if Util.is_out_of_border_sqr(adj_pe[0],adj_pe[1],math.sqrt(len_pes)):
    #                 return True
    #         return False

    #     def all_square_pes_contains_node(placement_c2n,pe,square_pes):
    #         for adj in square_pes:
    #             adj_pe = (pe[0]+adj[0],pe[1]+adj[1])
    #             if placement_c2n[adj_pe] == None:
    #                 return False
    #         return True

    #     square1 = [(0,1),(1,1),(1,0)]
    #     square2 = [(-1,0),(-1,1),(0,1)]
    #     square3 = [(1,0),(1,-1),(0,-1)]
    #     square4 = [(0,-1), (-1,-1),(-1,0)]
    #     squares = [square1,square2,square3,square4]

    #     vertexes, dfg_edges, placement_c2n = GraphGenerator.generate_random_tree_graph(num_vertexes,adj_list)
    #     pe = choice(placement_c2n.keys())
    #     square = choice(squares)

    # while not all_square_pes_contains_node(placement_c2n,pe,square) or any_out_of_border(pe,square,
    # len(placement_c2n)): pe = choice(placement_c2n.keys()) square = choice(squares)
