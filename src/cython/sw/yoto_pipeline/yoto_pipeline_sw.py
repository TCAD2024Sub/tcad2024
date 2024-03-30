from src.cython.util.per_graph import PeRGraph
from src.cython.util.per_enum import ArchType
from src.cython.util.piplinebase import PiplineBase
from src.cython.sw.yoto_pipeline.stage0_yoto import Stage0YOTO
from src.cython.sw.yoto_pipeline.stage1_yoto import Stage1YOTO
from src.cython.sw.yoto_pipeline.stage2_yoto import Stage2YOTO
from src.cython.sw.yoto_pipeline.stage3_yoto import Stage3YOTO
from src.cython.sw.yoto_pipeline.stage4_yoto import Stage4YOTO
from src.cython.util.util import Util
import multiprocessing as mp
import os
import time


class YotoPipelineSwOpt(PiplineBase):
    len_pipeline = 6

    def __init__(self, per_graph: PeRGraph, arch_type: ArchType, distance_table_bits: int, make_shuffle: bool,
                 n_threads: int = 1):
        self.len_pipeline: int = 6
        super().__init__(per_graph, arch_type, distance_table_bits, make_shuffle, self.len_pipeline, n_threads, )

    def run_parallel(self, n_copies: int = 1) -> dict:
        max_jobs: int = mp.cpu_count()
        manager = mp.Manager()
        dic_man = manager.dict()
        reports: dict = {}
        jobs_alive: list = []

        for exec_num in range(n_copies):
            p = mp.Process(target=self.exec_pipeline, args=(exec_num, dic_man))
            p.start()
            jobs_alive.append(p)

            while len(jobs_alive) >= max_jobs:
                jobs_alive: list = [job for job in jobs_alive if job.is_alive()]
                time.sleep(1)
        while len(jobs_alive) > 0:
            jobs_alive: list = [job for job in jobs_alive if job.is_alive()]
            time.sleep(1)
        for k in dic_man.keys():
            exec_num, total_pipeline_counter, exec_counter, n2c = dic_man[k]
            exec_key: str = 'exec_%d' % exec_num
            reports[exec_key] = Util.create_exec_report(self, exec_num, total_pipeline_counter, exec_counter, n2c)
        report: dict = Util.create_report(self, "YOTO", n_copies, reports)
        # print()
        return report

    def run_single(self, n_copies: int = 1) -> dict:
        dic_man = {}
        reports: dict = {}

        for exec_num in range(n_copies):
            self.exec_pipeline(exec_num, dic_man)
            for k in dic_man.keys():
                exec_num, total_pipeline_counter, exec_counter, n2c = dic_man[k]
                exec_key: str = 'exec_%d' % exec_num
                reports[exec_key] = Util.create_exec_report(self, exec_num, total_pipeline_counter, exec_counter, n2c)
        report: dict = Util.create_report(self, "YOTO", n_copies, reports)
        # print()
        return report

    def exec_pipeline(self, exec_key: int, dic_man):
        pid = os.getpid()
        # print(f'thread: {pid} starting')

        first_nodes: list = [self.edges_int[i][0][0] for i in range(self.len_pipeline)]
        n2c, c2n = self.init_traversal_placement_tables(first_nodes)

        st0_edge_sel: Stage0YOTO = Stage0YOTO(self.n_threads, self.visited_edges, self.len_pipeline)
        st1_edges: Stage1YOTO = Stage1YOTO(self.edges_int, self.distance_table_bits, self.visited_edges)
        st2_n2c: Stage2YOTO = Stage2YOTO(n2c, self.n_lines, self.len_pipeline)
        st3_dist: Stage3YOTO = Stage3YOTO(self.arch_type, self.n_lines, self.distance_table_bits, self.make_shuffle)
        st4_c2n: Stage4YOTO = Stage4YOTO(c2n, self.n_lines)

        counter = 0
        while not st0_edge_sel.done:
            st0_edge_sel.compute(st0_edge_sel.old_output, st4_c2n.old_output)
            st1_edges.compute(st0_edge_sel.old_output)
            st2_n2c.compute(st1_edges.old_output, st4_c2n.old_output)
            st3_dist.compute(st2_n2c.old_output)
            st4_c2n.compute(st3_dist.old_output, st4_c2n.old_output)
            counter += 1

        dic_man[pid] = [exec_key, st0_edge_sel.total_pipeline_counter, st0_edge_sel.exec_counter, n2c]
        # print(f'thread: {pid} ending')
