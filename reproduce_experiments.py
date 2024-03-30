import os
from src.python.sw.yott_pipeline.monte_carlo.yott_pipeline_mc0_sw import YOTTMC0Pipeline
from src.python.sw.yott_pipeline.monte_carlo.yott_pipeline_mc1_sw import YOTTMC1Pipeline
from src.python.sw.yott_pipeline.monte_carlo.yott_pipeline_mc import YOTTMCPipeline
from src.python.sw.yott_pipeline.yott_pipeline_sw import YOTTPipeline
from src.python.sw.yoto_pipeline.yoto_pipeline_sw import YotoPipelineSw
import sys
from src.python.util.per_enum import ArchType
from src.python.util.per_graph import PeRGraph
from src.python.util.util import Util
import time
mask = [1,0,0,0,0]
traversal = [YOTTPipeline, YOTTMCPipeline,YOTTMC0Pipeline,YOTTMC1Pipeline, YotoPipelineSw]
path_results = ["yott/yott_pipeline","yott/yott_pipeline","yott/yott_pipeline","yott/yott_pipeline","yoto/yoto_pipeline"]
methods = ["default","MC","MC0","MC1","default"]
limiars_str = ["-1","0.3","0.5|0.8|0.3","3|3|0.3","-1"]
run_parallel = False 
arch_types = [ArchType.MESH,ArchType.ONE_HOP]
root_path: str = Util.get_project_root()
dot_path_base = root_path + '/benchmarks/'
make_shuffle: bool = True
distance_table_bits: int = 4
copies = [1,10,100]
num_data = int(sys.argv[1])

start = time.time()
for i, method in enumerate(traversal):
    if not mask[i]:
        continue
    for arch_type in arch_types:
        len_pipe = method.len_pipeline
        total_executions = [len_pipe * copy for copy in copies]
        for total_execution in total_executions:
            print()
            print(method.__name__, arch_type, total_execution)
            print()
            threads_per_copy: int = len_pipe
            output_path_base = Util.get_project_root() + '/reports/sw/%s/t_%d/%s/' % (
                path_results[i], total_execution, arch_type.name)

            output_path = output_path_base

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            dots_list = Util.get_files_list_by_extension(dot_path_base, '.dot')
            reports: list[dict] = []

            num_annotations = [3] if method in [YOTTPipeline, YOTTMCPipeline,YOTTMC0Pipeline,YOTTMC1Pipeline] else [0]
            for num_annotation in num_annotations:
                for dot_path, dot_name in dots_list:
                    per_graph = PeRGraph(dot_path, dot_name)
                    print(per_graph.dot_name)
                    if method == YotoPipelineSw:
                        pipeline_method = YotoPipelineSw(per_graph, arch_type, distance_table_bits, make_shuffle,
                                                            len_pipe)
                    elif method == YOTTPipeline:
                        pipeline_method = YOTTPipeline(per_graph, arch_type, distance_table_bits, make_shuffle, num_annotation, len_pipe)
                    elif method == YOTTMCPipeline:
                        pipeline_method = YOTTMCPipeline(per_graph, arch_type, distance_table_bits, make_shuffle, 0.3, num_annotation, len_pipe)
                    elif method == YOTTMC0Pipeline:
                        pipeline_method = YOTTMC0Pipeline(per_graph, arch_type, distance_table_bits, make_shuffle,
                                                            [0.5, 0.8, 0.3], num_annotation, len_pipe)
                    elif method == YOTTMC1Pipeline:
                        pipeline_method = YOTTMC1Pipeline(per_graph, arch_type, distance_table_bits, make_shuffle,
                                                            [3, 3, 0.3], num_annotation, len_pipe)

                    if run_parallel:
                        raw_report: dict = pipeline_method.run_parallel(total_execution // threads_per_copy)
                    else:
                        raw_report: dict = pipeline_method.run_single(total_execution // threads_per_copy)
                    raw_report['num_annotations'] = num_annotation
                    raw_report['method'] = methods[i]
                    raw_report['limiar'] = limiars_str[i]

                    formatted_report = Util.get_formatted_report(raw_report,dot_path,num_data)
                    Util.save_json(output_path, dot_name.replace('.dot',
                                                                    '') + f'-NA<{num_annotation}>M<{methods[i]}={limiars_str[i]}>.dot',
                                    formatted_report)
                    reports.append(formatted_report)

end = time.time()

print(f'elapsed time = {end - start}')
