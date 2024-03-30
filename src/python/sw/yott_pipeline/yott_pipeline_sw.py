import os
import time
import multiprocessing as mp
from src.python.util.per_graph import PeRGraph
from src.python.sw.yott_pipeline.FIFOQueue import FIFOQueue
from src.python.sw.yott_pipeline.stage0_yott import Stage0YOTT
from src.python.sw.yott_pipeline.stage1_yott import Stage1YOTT
from src.python.sw.yott_pipeline.stage2_yott import Stage2YOTT
from src.python.sw.yott_pipeline.stage3_yott import Stage3YOTT
from src.python.sw.yott_pipeline.stage4_yott import Stage4YOTT
from src.python.sw.yott_pipeline.stage5_yott import Stage5YOTT
from src.python.sw.yott_pipeline.stage6_yott import Stage6YOTT
from src.python.sw.yott_pipeline.stage7_yott import Stage7YOTT
from src.python.sw.yott_pipeline.stage8_yott import Stage8YOTT
from src.python.sw.yott_pipeline.stage9_yott import Stage9YOTT
from src.python.util.piplinebase import PiplineBase
from src.python.util.util import Util


class YOTTPipeline(PiplineBase):
    len_pipeline = 10

    def __init__(self, per_graph: PeRGraph, arch_type, distance_table_bits, make_shuffle, num_annotations: int = 3,
                 num_threads: int = None, ):
        num_threads = self.len_pipeline if num_threads is None else num_threads
        self.num_annotations = num_annotations
        super().__init__(per_graph, arch_type, distance_table_bits, make_shuffle, self.len_pipeline, num_threads)
        self.len_edges = len(self.edges_int[0])

    def run_parallel(self, n_copies: int = 1) -> dict:
        max_jobs: int = mp.cpu_count() - 2
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
        report: dict = Util.create_report(self, "YOTT", n_copies, reports)
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
        report: dict = Util.create_report(self, "YOTT", n_copies, reports)
        return report

    def exec_pipeline(self, exec_key: int, dic_man):
        pid = os.getpid()
        # print(f'thread: {pid} starting')

        first_nodes: list = [self.edges_int[i][0][0] for i in range(self.len_pipeline)]
        n2c, c2n = self.init_traversal_placement_tables(first_nodes)

        for i, th_annot in enumerate(self.annotations.copy()):
            self.annotations[i] = Util.clear_invalid_annotations(th_annot)

        stage0 = Stage0YOTT(FIFOQueue(self.n_threads), self.len_pipeline)
        stage1 = Stage1YOTT(self.len_pipeline, self.n_threads, self.len_edges)
        stage2 = Stage2YOTT(self.edges_int, self.per_graph, self.annotations, self.n_threads,
                            self.distance_table_bits)
        stage3 = Stage3YOTT(self.len_pipeline, n2c)
        stage4 = Stage4YOTT(self.arch_type, self.n_lines, self.distance_table_bits, self.make_shuffle)
        stage5 = Stage5YOTT(self.arch_type)
        stage6 = Stage6YOTT(self.arch_type)
        stage7 = Stage7YOTT(self.n_lines, self.len_pipeline, c2n)
        stage8 = Stage8YOTT()
        stage9 = Stage9YOTT(self.len_pipeline)

        counter = 0
        while not stage1.done:
            # print(stage6.old_output_stage3)
            stage0.compute()
            # print(stage0.new_output)
            # print()
            # print(stage0.old_output)
            stage1.compute(stage0)
            # print(stage1.new_output)
            # print()
            # print(stage1.old_output)
            stage2.compute(stage1, self.num_annotations)
            # print(stage2.new_output)
            # print()
            # print(stage2.old_output)
            stage3.compute(stage2, stage9)
            # print(stage3.new_output)
            # print()
            # print(stage3.old_output)
            # print(stage6.C2N)
            stage4.compute(stage3)
            # print(stage4.new_output)
            # print()
            # print(stage4.old_output)
            stage5.compute(stage4)
            # print(stage5.new_output)
            # print()
            # print(stage5.old_output)
            stage6.compute(stage5, self.num_annotations)
            # print(stage6.new_output_stage3)
            # print()
            # print(stage5.old_output)
            stage7.compute(stage6, stage9)
            # print(stage6.new_output_stage3)
            # print()
            stage8.compute(stage7)
            # print(stage6.new_output_stage3)
            # print()
            stage9.compute(stage8, stage0)
            # print(stage6.new_output_stage3)
            # print()

            # input()
            counter += 1
        # self.print_grid(stage7.c2n)

        dic_man[pid] = [exec_key, stage0.total_pipeline_counter, stage0.exec_counter, n2c]
        # print(f'thread: {pid} ending')

    @staticmethod
    def print_grid(c2n):
        for idx_thread, thread in enumerate(c2n):
            print(f'thread{idx_thread}')
            for row in thread:
                print(row)
            print()
