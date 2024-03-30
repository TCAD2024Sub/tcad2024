# cython: language_level=3
import os
import time

import cython
import multiprocessing as mp

from src.python.sw.sa_pipeline.stage0_sa import Stage0SA
from src.python.sw.sa_pipeline.stage10_sa import Stage10SA
from src.python.sw.sa_pipeline.stage1_sa import Stage1SA
from src.python.sw.sa_pipeline.stage2_sa import Stage2SA
from src.python.sw.sa_pipeline.stage3_sa import Stage3SA
from src.python.sw.sa_pipeline.stage4_sa import Stage4SA
from src.python.sw.sa_pipeline.stage5_sa import Stage5SA
from src.python.sw.sa_pipeline.stage6_sa import Stage6SA
from src.python.sw.sa_pipeline.stage7_sa import Stage7SA
from src.python.sw.sa_pipeline.stage8_sa import Stage8SA
from src.python.sw.sa_pipeline.stage9_sa import Stage9SA
from src.python.util.per_enum import ArchType
from src.python.util.per_graph import PeRGraph
from src.python.util.piplinebase import PiplineBase
from src.python.util.util import Util


class SAPipeline(PiplineBase):
    len_pipeline = 6

    def __init__(self, per_graph: PeRGraph, arch_type: ArchType, distance_table_bits: cython.int,
                 make_shuffle: cython.bint, n_threads: cython.int = 1):
        self.len_pipeline: int = 10
        super().__init__(per_graph, arch_type, distance_table_bits, make_shuffle, self.len_pipeline, n_threads, )

    def run_parallel(self, n_copies: cython.int = 1) -> dict:
        """
                Run the pipeline in parallel.

                Args:
                    n_copies (int): Number of pipeline copies to execute in parallel. Default is 1.

                Returns:
                    dict: Pipeline execution report.
        """
        max_jobs: cython.int = mp.cpu_count()
        exec_times: cython.int = 1000
        max_counter: cython.int = pow(self.per_graph.n_cells, 2) * exec_times
        manager = mp.Manager()
        dic_man = manager.dict()
        reports: dict = {}
        jobs_alive: list = []
        for exec_num in range(n_copies):

            p = mp.Process(target=self.exec_pipeline, args=(exec_num, max_counter, dic_man))
            p.start()
            jobs_alive.append(p)

            while len(jobs_alive) >= max_jobs:
                jobs_alive: list = [job for job in jobs_alive if job.is_alive()]
                time.sleep(1)
        while len(jobs_alive) > 0:
            jobs_alive: list = [job for job in jobs_alive if job.is_alive()]
            time.sleep(1)
        for k in dic_man.keys():
            exec_num, exec_counter, n2c = dic_man[k]
            exec_key: str = 'exec_%d' % exec_num
            reports[exec_key] = Util.create_exec_report(self, exec_num, max_counter,
                                                        [exec_counter for _ in range(self.n_threads)],
                                                        n2c
                                                        )
        report: dict = Util.create_report(self, "SA_PIPELINE", n_copies, reports)
        print()
        return report

    def run_single(self, n_copies: cython.int = 1) -> dict:
        exec_times: cython.int = 1000
        max_counter: cython.int = pow(self.per_graph.n_cells, 2) * exec_times
        dic_man: dict = {}
        reports: dict = {}
        for exec_num in range(n_copies):
            self.exec_pipeline(exec_num, max_counter, dic_man)

        for k in dic_man.keys():
            exec_num, exec_counter, n2c = dic_man[k]
            exec_key: str = 'exec_%d' % exec_num
            reports[exec_key] = Util.create_exec_report(self, exec_num, max_counter,
                                                        [exec_counter for _ in range(self.n_threads)],
                                                        n2c
                                                        )

        report: dict = Util.create_report(self, "SA_PIPELINE", n_copies, reports)
        print()
        return report

    def exec_pipeline(self, exec_key: cython.int, max_counter: cython.int, dic_man):
        pid = os.getpid()
        print(f'thread: {pid} starting')
        n2c, c2n = self.init_sa_placement_tables()

        st0: Stage0SA = Stage0SA(self.per_graph.n_cells, self.n_threads)
        st1: Stage1SA = Stage1SA(c2n, self.n_threads)
        st2: Stage2SA = Stage2SA(self.per_graph.neighbors)
        st3: Stage3SA = Stage3SA(n2c, self.n_threads)
        st4: Stage4SA = Stage4SA(self.arch_type, self.n_lines, self.n_columns)
        st5: Stage5SA = Stage5SA(self.arch_type, self.n_lines, self.n_columns)
        st6: Stage6SA = Stage6SA()
        st7: Stage7SA = Stage7SA()
        st8: Stage8SA = Stage8SA()
        st9: Stage9SA = Stage9SA()
        st10: Stage10SA = Stage10SA()
        counter: cython.int = 0

        while counter < max_counter:
            st0.compute()
            st1.compute(st0.old_output, st9.old_output, st1.old_output['wb'])
            st2.compute(st1.old_output)
            st3.compute(st2.old_output, st3.old_output['wb'])
            st4.compute(st3.old_output)
            st5.compute(st4.old_output)
            st6.compute(st5.old_output)
            st7.compute(st6.old_output)
            st8.compute(st7.old_output)
            st9.compute(st8.old_output)
            st10.compute(st9.old_output)

            counter += 1
        for th_idx in range(self.n_threads):
            for n_idx in range(len(n2c[th_idx])):
                if n2c[th_idx][n_idx] != -1:
                    n2c[th_idx][n_idx] = Util.get_line_column_from_cell(n2c[th_idx][n_idx], self.n_lines,
                                                                        self.n_columns)
                else:
                    n2c[th_idx][n_idx] = [-1, -1]
        dic_man[pid] = [exec_key, st0.exec_counter, n2c]
        print(f'thread: {pid} ending')
