import json
import os
import random
import traceback
from math import ceil, log2, sqrt
from pathlib import Path
from typing import List, Dict, Tuple, Any
import pygraphviz as pgv
import matplotlib.pyplot as plt
import pandas as pd

from src.cython.util.per_enum import ArchType
from src.cython.util.per_graph import PeRGraph


class Util:

    @staticmethod
    def func_unkey(text: str) -> List[str]:
        """
        Split the text into a list of words.

        :param text: The input text.
        :type text: str
        :return: A list of words.
        :rtype: list[str]
        """
        return text.split(" ")

    @staticmethod
    def write_file(file_name: str, data_to_write: list):
        with open(file_name, 'w') as f:
            f.writelines(f'{line}\n' for line in data_to_write)

    @staticmethod
    def func_key(val1: str, val2: str) -> str:
        """
        Concatenate two strings to form a key.

        :param val1: The first string.
        :type val1: str
        :param val2: The second string.
        :type val2: str
        :return: The concatenated key.
        :rtype: str
        """
        return val1 + " " + val2

    @staticmethod
    def get_graph_annotations(edges: List[List[str]], cycle: List[List[str]]) -> Dict[str, List[List[str]]]:
        """
        Generate graph annotations based on edges and cycles.

        :param edges: List of edges in the graph.
        :type edges: List[List[str]]
        :param cycle: List of cycles in the graph.
        :type cycle: List[List[str]]
        :return: Graph annotations.
        :rtype: Dict[str, List[List[str]]]
        """
        dic_cycle: Dict[str, List[List[str]]] = {}

        # Initialization dictionary
        for edge in edges:
            key: str = Util.func_key(edge[0], edge[1])
            dic_cycle[key] = []

        for elem_cycle_begin, elem_cycle_end in cycle:
            walk_key: List[str] = []
            found_start = False
            count = 0
            value1 = ''

            for edge in reversed(edges):
                if elem_cycle_begin == edge[1] and not found_start:
                    value1 = edge[0]
                    key = Util.func_key(value1, elem_cycle_begin)
                    walk_key.insert(0, key)
                    dic_cycle[key].append([elem_cycle_end, count])
                    count += 1
                    found_start = True

                elif found_start and (value1 == edge[1] or elem_cycle_end == edge[0]):
                    value1, value2 = edge[0], edge[1]
                    key = Util.func_key(value1, value2)
                    if value1 != elem_cycle_end and value2 != elem_cycle_end:
                        walk_key.insert(0, key)
                        dic_cycle[key].append([elem_cycle_end, count])
                        count += 1
                    else:
                        # Go back and update values
                        for k in range(count // 2):
                            dic_actual = dic_cycle[walk_key[k]]
                            for dic_key, (node, count) in enumerate(dic_actual):
                                if node == elem_cycle_end:
                                    dic_actual[dic_key][1] = k + 1
                        break  # to the next on the vector CYCLE
        return dic_cycle

    @staticmethod
    def get_db_statistics(dot_file: str, dot_name: str) -> Dict[str, any]:
        """
        Get statistics for a database.

        :param dot_file: Path to the DOT file.
        :type dot_file: str
        :param dot_name: Name of the DOT file.
        :type dot_name: str
        :return: Statistics dictionary.
        :rtype: dict
        """
        per_graph = PeRGraph(dot_file, dot_name)

        stat: Dict[str, any] = {
            'name': dot_name,
            'nodes': per_graph.n_nodes,
            'edges': per_graph.n_edges,
            'ideal_cost': per_graph.n_edges,
            'max_degree': 0,
            'avg_degree': 0,
            'g_hub': {},
            'top_k_hub': [],
            'percent_multicast': 0,
            'hist_degree': {}
        }

        max_degree = 0
        avg_degree = 0
        hub_sum = 0
        for node in per_graph.nodes:
            # finding the degrees of each node and calculating the average degree for the graph
            degree = per_graph.g.degree[node]
            max_degree = max(max_degree, degree)
            avg_degree += degree

            if degree > 4:
                print(per_graph.dot_name, node, degree)

            # creating the degree histogram
            stat['hist_degree'][degree] = stat['hist_degree'].get(degree, 0) + 1

            # finding the hub for the graph
            n_children = len(per_graph.g._succ[node])
            if n_children > 2:
                stat['g_hub'][node] = n_children
                hub_sum += 1

        avg_degree /= per_graph.n_nodes
        stat['max_degree'] = max_degree
        stat['avg_degree'] = avg_degree
        stat['percent_multicast'] = hub_sum / per_graph.n_nodes
        stat['hist_degree'] = dict(sorted(stat['hist_degree'].items()))

        top_k_hub = sorted(stat['g_hub'].items(),
                           key=lambda item: item[1], reverse=True)
        k = ceil(len(top_k_hub) * 0.2)
        stat['top_k_hub'] = top_k_hub[:k]

        return stat

    @staticmethod
    def dist_one_hop(a: List[int], b: List[int]) -> int:
        """
        Calculate the one-hop distance between two points.

        :param a: Coordinates of point A.
        :type a: List[int]
        :param b: Coordinates of point B.
        :type b: List[int]
        :return: The one-hop distance between A and B.
        :rtype: int
        """

        ia, ja = a
        ib, jb = b
        i = abs(ia - ib)
        j = abs(ja - jb)
        edge_distance = ceil(i / 2) + ceil(j / 2)
        return edge_distance

    @staticmethod
    def dist_manhattan(a: List[int], b: List[int]) -> int:
        """
        Calculate the Manhattan distance between two points.

        :param a: Coordinates of point A.
        :type a: List[int]
        :param b: Coordinates of point B.
        :type b: List[int]
        :return: The Manhattan distance between A and B.
        :rtype: int
        """
        ia, ja = a
        ib, jb = b
        edge_distance: int = abs(ia - ib) + abs(ja - jb)
        return edge_distance

    @staticmethod
    def calc_dist(a: List[int], b: List[int], arch_type: ArchType) -> int:
        """
        Calculate the distance between two points based on the architecture type.

        :param a: Coordinates of point A.
        :type a: List[int]
        :param b: Coordinates of point B.
        :type b: List[int]
        :param arch_type: The architecture type.
        :type arch_type: ArchType
        :return: The distance between A and B.
        :rtype: int
        """
        if arch_type == ArchType.MESH:
            return Util.dist_manhattan(a, b)
        elif arch_type == ArchType.ONE_HOP:
            return Util.dist_one_hop(a, b)

    @staticmethod
    def get_edges_distances(arch_type: ArchType, edges: list[list[int]], n2c: list[list[int]]) \
            -> tuple[dict, list]:
        """
        Get distances between edges based on the architecture type.

        :param arch_type: The architecture type.
        :type arch_type: ArchType
        :param edges: List of edges.
        :type edges: List[List[int]]
        :param n2c: List of node-to-cell mappings.
        :type n2c: List[List[int]]
        :return: A tuple containing a dictionary of edge distances and a list of edge distances.
        :rtype: Tuple[Dict[str, int], List[int]]
        """
        dic_edges_dist: Dict[str, int] = {}
        list_edges_dist: List[int] = []
        for edge in edges:
            n1, n2 = edge
            a = n2c[n1]
            b = n2c[n2]
            edge_distance = Util.calc_dist(a, b, arch_type)
            dic_edges_dist[f"{n1}_{n2}"] = edge_distance
            list_edges_dist.append(edge_distance)
        return dic_edges_dist, list_edges_dist

    @staticmethod
    def is_out_of_border_sqr(i: int, j: int, n_cells_sqrt: int) -> bool:
        """
        Check if the given coordinates are out of the border of a square grid.

        :param i: The row index.
        :type i: int
        :param j: The column index.
        :type j: int
        :param n_cells_sqrt: The square root of the number of cells in the grid.
        :type n_cells_sqrt: int
        :return: True if the coordinates are out of the border, False otherwise.
        :rtype: bool
        """
        return i > n_cells_sqrt - 1 or j > n_cells_sqrt - 1 or i < 0 or j < 0

    # FIXME - Function under development
    @staticmethod
    def get_router_boxplot_graph_from_dict(report_data: dict, graph_path: str, graph_name: str):
        """

        @param report_data:
        @type report_data:
        @param graph_path:
        @type graph_path:
        @param graph_name:
        @type graph_name:
        """
        data: dict = {}
        for router_reports_key in report_data.keys():
            report: dict = report_data[router_reports_key]
            for len_key in report.keys():
                if len_key in data.keys():
                    data[len_key].append(report[len_key])
                else:
                    data[len_key]: dict = [report[len_key]]
        max_len = 0
        for key in data.keys():
            if len(data[key]) > max_len:
                max_len = len(data[key])
        for key in data.keys():
            while len(data[key]) < max_len:
                data[key].append(0)
        data = dict(sorted(data.items()))
        try:

            # Set the figure size
            plt.rcParams["figure.figsize"] = [7.50, 3.50]
            plt.rcParams["figure.autolayout"] = True
            # Pandas dataframe
            pd_data = pd.DataFrame(data)
            # print(pd_data)
            # Plot the dataframe
            pd_data[list(pd_data.keys())].plot(kind='box', title='boxplot')
            # Display the plot
            # plt.show()
            plt.savefig('%s%s.svg' % (graph_path, graph_name), dpi='figure', format='svg')

        except Exception as e:
            print(e)
            traceback.print_exc()

    @staticmethod
    def save_json(path: str, file_name: str, data: Dict):
        """
        Save data as JSON to a file.

        :param path: The path to save the file.
        :type path: str
        :param file_name: The name of the file.
        :type file_name: str
        :param data: The data to save.
        :type data: dict
        """
        if path[-1] !='/':
            path = path + '/'
        with open(path + file_name + '.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def read_json(file: str) -> Dict:
        """
        Read JSON data from a file.

        :param file: The path to the JSON file.
        :type file: str
        :return: The loaded JSON data.
        :rtype: dict
        """
        with open(file) as p_file:
            content_dic = json.load(p_file)
        return content_dic

    @staticmethod
    def get_files_list_by_extension(path: str, file_extension: str) -> List[Tuple[str, str]]:
        """
        Get a list of files with a specific extension in a directory.

        :param path: The path to the directory.
        :type path: str
        :param file_extension: The file extension to filter.
        :type file_extension: str
        :return: A list of tuples containing the file path and file name.
        :rtype: List[Tuple[str, str]]
        """
        files_list_by_extension: List[Tuple[str, str]] = [
            (os.path.join(file_path, file_name), file_name)
            for file_path, _, filenames in os.walk(path)
            for file_name in filenames
            if os.path.splitext(file_name)[1] == file_extension
        ]
        return files_list_by_extension

    @staticmethod
    def get_cell_from_line_column(cell_line: int, cell_column: int, n_lines: int) -> int:
        """

        @param cell_line:
        @type cell_line:
        @param cell_column:
        @type cell_column:
        @param n_lines:
        @type n_lines:
        @return:
        @rtype:
        """

        return cell_line * n_lines + cell_column

    @staticmethod
    def format_distance_table(distance_table_raw: List[List], make_shuffle: bool) -> List[List[int]]:
        """
        Format the distance table and optionally shuffle the entries.

        :param distance_table_raw: The raw distance table.
        :type distance_table_raw: List[List[int]]
        :param make_shuffle: Flag indicating whether to shuffle the entries.
        :type make_shuffle: bool
        :return: The formatted distance table.
        :rtype: List[List[int]]
        """
        distance_table: List[List[int]] = []
        for dist in distance_table_raw:
            if make_shuffle:
                random.shuffle(dist)
            distance_table.extend(dist)
        return distance_table

    @staticmethod
    def get_one_hop_distances(cells_sqrt: int, make_shuffle: bool) -> List[List[int]]:
        """
        Get one-hop distances between cells in a square grid.

        :param cells_sqrt: The square root of the number of cells in the grid.
        :type cells_sqrt: int
        :param make_shuffle: Flag indicating whether to shuffle the distances.
        :type make_shuffle: bool
        :return: List of one-hop distances.
        :rtype: List[List[int]]
        """
        max_distance: int = 2 * ceil((cells_sqrt - 1) / 2)
        distance_table_raw: List[List[List[int]]] = [[] for _ in range(max_distance + 1)]
        for i in range(cells_sqrt):
            dist_i: int = ceil(i / 2)
            for j in range(cells_sqrt):
                dist_j: int = ceil(j / 2)
                dist: int = dist_i + dist_j
                if dist == 0:
                    continue
                distance_table_raw[dist - 1].append([i, j])
                if i == 0:
                    distance_table_raw[dist - 1].append([i, -j])
                elif j == 0:
                    distance_table_raw[dist - 1].append([-i, j])
                else:
                    distance_table_raw[dist - 1].extend([[i, -j], [-i, j], [-i, -j]])

        return Util.format_distance_table(distance_table_raw, make_shuffle)

    @staticmethod
    def get_mesh_distances(cells_sqrt: int, make_shuffle: bool) -> list[list[int]]:
        """

        @param cells_sqrt:
        @type cells_sqrt:
        @param make_shuffle:
        @type make_shuffle:
        @return:
        @rtype:
        """
        distance_table_raw: list[list] = [[] for _ in range((cells_sqrt - 1) * 2)]
        for i in range(cells_sqrt):
            for j in range(cells_sqrt):
                if j == i == 0:
                    continue
                dist: int = i + j
                if [i, j] not in distance_table_raw[dist - 1]:
                    distance_table_raw[dist - 1].append([i, j])
                if [i, -j] not in distance_table_raw[dist - 1]:
                    distance_table_raw[dist - 1].append([i, -j])
                if [-i, -j] not in distance_table_raw[dist - 1]:
                    distance_table_raw[dist - 1].append([-i, -j])
                if [-i, j] not in distance_table_raw[dist - 1]:
                    distance_table_raw[dist - 1].append([-i, j])
        mesh_distances: list[list[int]] = Util.format_distance_table(distance_table_raw, make_shuffle)
        return mesh_distances

    @staticmethod
    def get_distance_table(arch_type: ArchType, cells_sqrt: int, make_shuffle: bool) -> List[List[int]]:
        """
        Get distance table based on the architecture type.

        :param arch_type: The type of architecture (Mesh or One-Hop).
        :type arch_type: ArchType
        :param cells_sqrt: The square root of the number of cells in the grid.
        :type cells_sqrt: int
        :param make_shuffle: Flag indicating whether to shuffle the distances.
        :type make_shuffle: bool
        :return: List of distances.
        :rtype: List[List[int]]
        """
        if arch_type == ArchType.MESH:
            return Util.get_mesh_distances(cells_sqrt, make_shuffle)
        elif arch_type == ArchType.ONE_HOP:
            return Util.get_one_hop_distances(cells_sqrt, make_shuffle)
        else:
            raise ValueError("Architecture type not supported")

    @staticmethod
    def get_line_column_from_cell(cell: int, n_lines: int, n_columns: int) -> List[int]:
        """

        @param cell:
        @type cell:
        @param n_lines:
        @type n_lines:
        @param n_columns:
        @type n_columns:
        @return:
        @rtype:
        """
        line: int = cell // n_lines
        column: int = cell % n_columns
        return [line, column]

    @staticmethod
    def get_line_column_cell_sqrt(cell: int, cells_sqrt: int) -> List[int]:
        """

        @param cell:
        @type cell:
        @param cells_sqrt:
        @type cells_sqrt:
        @return:
        @rtype:
        """
        return Util.get_line_column_from_cell(cell, cells_sqrt, cells_sqrt)

    @staticmethod
    def get_line_column_list(cells: List[int], n_lines: int, n_columns: int) -> List[List[int]]:
        """"
        Converts a list of cell indices to a list of corresponding line-column pairs.

        Args:
            cells (List[int]): The list of cell indices.
            n_lines (int): The number of lines in the grid.
            n_columns (int): The number of columns in the grid.

        Returns:
            List[List[int]]: A list of line-column pairs corresponding to the input cell indices.
        """
        line_column_list: List[List[int]] = []
        for cell in cells:
            line_column_list.append(Util.get_line_column_from_cell(cell, n_lines, n_columns))
        return line_column_list

    @staticmethod
    def get_line_column_list_sqrt(cells: List[int], cells_sqrt: int) -> List[int]:
        """
        Retrieve a list of line-column pairs given a list of cell indices and the square root of the total cells.

        Args:
            cells (List[int]): List of cell indices.
            cells_sqrt (int): Square root of the total cells.

        Returns:
            List[int]: List of line-column pairs.
        """
        line_column_list_sqrt: List[int] = Util.get_line_column_list(cells, cells_sqrt, cells_sqrt)
        return line_column_list_sqrt

    @staticmethod
    def get_project_root() -> str:
        """
        Get the root path of the project.

        Returns:
            str: The root path of the project.
        """
        path: Path = Path(__file__).parent.parent.parent.parent
        return str(path)

    @staticmethod
    def create_exec_report(pipeline_base: Any, exec_num: int, total_pipeline_counter: int,
                           exec_counter: List[int], n2c: List[List[List[int]]]) -> Dict[str, Any]:
        """
        Create a report for the execution.

        Args:
            pipeline_base (Any): Pipeline base.
            exec_num (int): Execution number.
            total_pipeline_counter (int): Total pipeline counter.
            exec_counter (List[int]): Execution counter.
            n2c (List[List[List[int]]]): N2C.

        Returns:
            dict: Execution report.
        """
        exec_report: Dict[str, Any] = {
            'total_exec_clk': total_pipeline_counter
        }
        th_dict: Dict[str, Any] = {}
        for th in range(pipeline_base.n_threads):
            th_key = 'Exec_%d_TH_%d' % (exec_num, th)
            th_dict[th_key]: Dict[str, Any] = {}
            th_dict[th_key]['total_th_clk']: int = exec_counter[th]
            th_dict[th_key]['th_placement']: List[int] = n2c[th]
            edges_str: List[str] = pipeline_base.edges_raw
            edges_int: List = pipeline_base.get_edges_int(edges_str[th])
            dic_edges_dist, list_edges_dist = Util.get_edges_distances(pipeline_base.arch_type, edges_int, n2c[th])
            dic_edges_dist = dict(sorted(dic_edges_dist.items(), key=lambda x: x[1]))
            th_dict[th_key]['th_placement_distances']: Dict = dic_edges_dist
            dist_total = sum(list_edges_dist) - len(dic_edges_dist)
            th_dict[th_key]['th_dist_total']: int = dist_total
        exec_report['th_results'] = th_dict
        return exec_report

    @staticmethod
    def create_report(traversal: Any, algorithm: str, n_copies: int, reports: Dict) -> Dict[str, Any]:
        """
        Create a report.

        Args:
            traversal (Any): Traversal.
            algorithm (str): Algorithm.
            n_copies (int): Number of copies.
            reports (Dict): Reports.

        Returns:
            dict: Created report.
        """
        exec_report: Dict[str, Any] = {
            "graph_name": traversal.per_graph.dot_name,
            "algorithm": algorithm,
            "arch_type": traversal.arch_type.name,
            "total_edges": traversal.total_edges,
            "visited_edges": traversal.visited_edges,
            "n_copies": n_copies,
            "total_threads": traversal.n_threads * n_copies,
            "n_cells": traversal.per_graph.n_cells,
            "n_lines": traversal.n_lines,
            "n_columns": traversal.n_columns,
            "reports": reports,
            "nodes_dict": traversal.per_graph.nodes_to_idx
        }
        return exec_report

    @staticmethod
    def get_formatted_report(raw_report: Dict) -> Dict[str, Any]:
        """
        Get the formatted report.

        Args:
            raw_report (Dict): Raw report.

        Returns:
            dict: Formatted report.
        """
        exec_max_clk: int = -1
        exec_min_clk: int = -1
        exec_avg_clk: int = 0
        n_copies = raw_report['n_copies']
        th_max_clk: int = -1
        th_min_clk: int = -1
        th_avg_clk: int = 0
        # Total threads quantity
        total_threads: int = raw_report['total_threads']
        th_placement_distances: dict = {}

        best_dist = 999999
        best_thread = None
        # para debug
        best_placement = None
        # fim debug
        # generate data for reports
        for report_key in raw_report['reports'].keys():
            report: dict = raw_report['reports'][report_key]

            total_exec_clk: int = report['total_exec_clk']

            exec_avg_clk += total_exec_clk

            if exec_max_clk == -1:
                exec_max_clk = total_exec_clk
            else:
                if total_exec_clk > exec_max_clk:
                    exec_max_clk = total_exec_clk
            if exec_min_clk == -1:
                exec_min_clk = total_exec_clk
            else:
                if total_exec_clk < exec_min_clk:
                    exec_min_clk = total_exec_clk

            for th_key in report['th_results'].keys():
                th_results: dict = report['th_results'][th_key]
                th_placement_distances[th_key]: dict = th_results['th_placement_distances']

                total_th_clk: int = th_results['total_th_clk']

                th_avg_clk += total_th_clk

                if th_max_clk == -1:
                    th_max_clk = total_th_clk
                else:
                    if total_th_clk > th_max_clk:
                        th_max_clk = total_th_clk
                if th_min_clk == -1:
                    th_min_clk = total_th_clk
                else:
                    if total_th_clk < th_min_clk:
                        th_min_clk = total_th_clk

                dist_th = th_results['th_dist_total']
                if dist_th < best_dist:
                    best_dist = dist_th
                    best_thread = th_key
                    best_placement = th_results['th_placement']

        exec_avg_clk /= n_copies
        th_avg_clk /= total_threads
        # para debug
        sqr = int(sqrt(len(best_placement)))
        matrix = [[-1 for i in range(sqr)] for j in range(sqr)]
        for node, (a, b) in enumerate(best_placement):
            if a is not None:
                matrix[a][b] = node
        # fim debug
        formatted_report = raw_report.copy()
        del formatted_report['reports']
        del formatted_report['nodes_dict']
        formatted_report['best_thread'] = best_thread
        formatted_report['best_dist'] = best_dist
        formatted_report["exec_max_clk"]: int = exec_max_clk
        formatted_report["exec_min_clk"]: int = exec_min_clk
        formatted_report["exec_avg_clk"]: int = exec_avg_clk
        formatted_report["th_max_clk"]: int = th_max_clk
        formatted_report["th_min_clk"]: int = th_min_clk
        formatted_report["th_avg_clk"]: int = th_avg_clk
        # para debug
        formatted_report['best_placement'] = matrix
        # fim debug
        formatted_report["th_placement_distances"]: dict = th_placement_distances[best_thread]
        formatted_report['nodes_dict']: dict = raw_report['nodes_dict']

        return formatted_report

    @staticmethod
    def get_n_bits(n: int) -> int:
        """
        Get the number of bits needed to represent a number.

        Args:
            n (int): Input number.

        Returns:
            int: Number of bits needed.
        """
        if n < 2:
            return 1
        else:
            return int(ceil(log2(n)))

    @staticmethod
    def create_folder_if_not_exist(folder: str) -> None:
        """
        Create a folder if it does not exist.

        Args:
            folder (str): Folder path.
        """
        if not os.path.exists(folder):
            os.makedirs(folder)

    @staticmethod
    def clear_invalid_annotations(annotations: Dict[str, List[int]]) -> Dict[str, List[int]]:
        """
        Clear invalid annotations.

        Args:
            annotations (Dict[str, List[int]]): Annotations.

        Returns:
            Dict[str, List[int]]: Valid annotations.
        """
        placed_nodes = {None: True}
        for k, v in annotations.items():
            a, b = k.split()
            placed_nodes[a] = True
            placed_nodes[b] = True
            for (c, _) in (v.copy()):
                if placed_nodes.get(c) is None:
                    annotations[k].remove([c, _])

        return annotations

    def generate_images_by_dot_files(path_dot_files:str):
        dot_files = Util.get_files_list_by_extension(path_dot_files, ".dot")
        for dot_file,filename in dot_files:
            G = pgv.AGraph(dot_file)
            G.draw(path_dot_files+filename.replace('.dot','.png'),format='png',prog='dot')
    
    def generate_in_vertexes(vertexes:list[int],edges:list[tuple[int,int]]) -> dict:
        in_vertexes = {}
        for vertex in vertexes:
            in_vertexes[vertex] = []

        for (src,dst) in edges:
            in_vertexes[dst].append(src)
        return in_vertexes
    
    def generate_out_vertexes(vertexes:list[int],edges:list[tuple[int,int]])-> dict:
        out_vertexes = {}
        for vertex in vertexes:
            out_vertexes[vertex] = []
        for (src,dst) in edges:
            out_vertexes[src].append(dst)
        return out_vertexes
    
    def find_thread_with_best_placement(pipeline_base,n2c):
        best_thread = None
        best_dist = 999999
        def get_edges_distances(arch_type: ArchType, edges: list[list[int]], n2c: list[list[int]]) \
        -> tuple[dict, list]:
            dic_edges_dist: Dict[str, int] = {}
            list_edges_dist: List[int] = []
            for edge in edges:
                n1, n2 = edge
                a = n2c[n1]
                b = n2c[n2]
                assert a != [None,None], 'retirar se utilizar método X'
                if a!=[None,None] and b!= [None,None]:
                    edge_distance = Util.calc_dist(a, b, arch_type)
                    dic_edges_dist[f"{n1}_{n2}"] = edge_distance
                    list_edges_dist.append(edge_distance)
            return dic_edges_dist, list_edges_dist

        
        for th in range(pipeline_base.n_threads):
            edges_str: List[str] = pipeline_base.edges_raw
            edges_int: List = pipeline_base.get_edges_int(edges_str[th])
            dic_edges_dist, list_edges_dist = get_edges_distances(pipeline_base.arch_type, edges_int, n2c[th])
            dic_edges_dist = dict(sorted(dic_edges_dist.items(), key=lambda x: x[1]))
            dist_total = sum(list_edges_dist) - len(dic_edges_dist)
            if dist_total < best_dist:
                best_dist = dist_total
                best_thread = th
        return best_thread,best_dist