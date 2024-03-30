import math
import random
from src.python.util.util import Util
from math import sqrt


class Router:
    @staticmethod
    def create_dag_by_pe(placement_c2n: dict[int, int],
                         pe_id: int, adj_list: list[tuple[int, int]]):

        assert placement_c2n[pe_id] is not None, "There must be a node placed in this PE"

        fila = [pe_id]
        len_pes = len(placement_c2n)
        visited_pes = {pe_id: True}
        pes_allocated_in_fifo = {pe_id: True}
        father = {pe_id: None}

        routing = []
        while len(fila) > 0:
            cur_pe = fila.pop(0)
            visited_pes[cur_pe] = True
            # print(cur_pe)

            for neighbor in [(cur_pe[0] + a, cur_pe[1] + b) for (a, b) in adj_list]:
                if not Util.is_out_of_border_sqr(neighbor[0], neighbor[1], sqrt(len_pes)):
                    if placement_c2n[neighbor] is not None and visited_pes.get(neighbor) is None:
                        if father.get(neighbor) is None:
                            routing.append((cur_pe, neighbor))
                            father[neighbor] = cur_pe
                        else:
                            prob = random.random()
                            if prob <= 0.3:
                                routing.append((cur_pe, neighbor))
                            elif prob <= 0.6:
                                routing.append((cur_pe, neighbor))
                                routing.remove((father[neighbor], neighbor))
                                father[neighbor] = cur_pe

                        if pes_allocated_in_fifo.get(neighbor) is None:
                            fila.append(neighbor)
                            pes_allocated_in_fifo[neighbor] = True

        return routing

    @staticmethod
    def create_tree_by_pe(placement_c2n: dict[int, int],
                          pe_id: int, adj_list: list[tuple[int, int]]):

        assert placement_c2n[pe_id] is not None, "There must be a node placed in this PE"

        fila = [pe_id]
        len_pes = len(placement_c2n)
        visited_pes = {pe_id: True}
        pes_allocated_in_fifo = {pe_id: True}
        father = {pe_id: None}

        routing = []
        while len(fila) > 0:
            cur_pe = fila.pop(0)
            visited_pes[cur_pe] = True

            for neighbor in [(cur_pe[0] + a, cur_pe[1] + b) for (a, b) in adj_list]:
                if not Util.is_out_of_border_sqr(neighbor[0], neighbor[1], math.sqrt(len_pes)):
                    if placement_c2n[neighbor] is not None and visited_pes.get(neighbor) is None:
                        if father.get(neighbor) is None:
                            routing.append((cur_pe, neighbor))
                            father[neighbor] = cur_pe
                        else:
                            if random.random() <= 0.5:
                                routing.append((cur_pe, neighbor))
                                routing.remove((father[neighbor], neighbor))
                                father[neighbor] = cur_pe

                        if pes_allocated_in_fifo.get(neighbor) is None:
                            fila.append(neighbor)
                            pes_allocated_in_fifo[neighbor] = True

        return routing
