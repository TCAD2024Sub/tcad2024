from src.python.sw.yoto_pipeline.yoto_pipeline_sw import YotoPipelineSw
from src.python.sw.yott_pipeline.yott_pipeline_sw import YOTTPipeline
from src.python.util.per_enum import ArchType
from src.python.util.per_graph import PeRGraph
from src.python.util.util import Util
import sys

def place(dot_path:str,dot_filename:str, pipeline_method: str, num_copies: int, arch_type: str, output_path:str,num_data:int):
    if arch_type == "MESH":
        architecture = ArchType.MESH
    elif arch_type == "ONE-HOP":
        architecture = ArchType.ONE_HOP
    else:
        raise ValueError('You should provide MESH or ONE-HOP as the arch_type.')
    
    distance_table_bits = 4
    per_graph = PeRGraph(dot_path, dot_filename)

    if pipeline_method == "YOTO":
        pipeline = YotoPipelineSw(per_graph, architecture, distance_table_bits, True,6)
        factor= 6
    elif pipeline_method == "YOTT":
        pipeline = YOTTPipeline(per_graph, architecture, distance_table_bits, True, 3, 10)
        factor = 10
    else:
        raise ValueError('You should provide YOTO or YOTT as pipeline_method.')    
    
    print('-'*60)
    print(f'Initializing placement for {dot_filename}')
    print(f'Method: {pipeline_method} - Architecture Type: {arch_type} - Number of Executions: {factor*num_copies}')
    print(f'Number of data for simulation: {num_data}')
    print()
    raw_report: dict = pipeline.run_single(num_copies)
    formatted_report = Util.get_formatted_report(raw_report, dot_path, num_data)
    best_placement = formatted_report['results']['best_placement']
    best_throughput = formatted_report['results']['best_throughput']

    dist = best_placement['dist']
    throughput = best_placement['throughput']

    print('Placement with the lowest cost:\n')
    for row in best_placement['placement']:
        print(row)
    print(f'\nTotal distance = {dist} - Throughput = {throughput:.2f}')
    
    print()
    dist = best_throughput['dist']
    throughput = best_throughput['throughput']
    print(f'Placement with the best throughput:\n')
    for row in best_throughput['placement']:
        print(row)

    print(f'\nTotal distance = {dist} - Throughput = {throughput:.2f}')
    
    filename = dot_filename.replace('.dot','')
    Util.save_json(output_path,filename ,formatted_report)
    print(f'\nThe placement information can be viewed at: {output_path}{filename}.json')
    print('-'*60)

if __name__ == '__main__':
    args = args = sys.argv[1:]
    dot_path = args[0]
    dot_filename = args[1]
    pipeline_method = args[2]
    num_copies = int(args[3])
    arch_type = args[4]
    output_path = args[5]
    num_data = int(args[6])

    place(dot_path,dot_filename,pipeline_method,num_copies,arch_type,output_path,num_data) 