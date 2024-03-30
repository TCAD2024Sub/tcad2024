from src.python.util.util import Util

root_path: str = Util.get_project_root()
base_path: str = root_path + "/results/sw/"
report_files: list = Util.get_files_list_by_extension(base_path, '.json')
exec_stats: dict = {}
for report_file, file_name in report_files:
    json_dict: dict = Util.read_json(report_file)
    graph_name: str = json_dict["graph_name"]
    n_threads: int = json_dict["n_threads"]
    if graph_name not in exec_stats.keys():
        exec_stats[graph_name] = {
            'total_edges': json_dict["total_edges"],
            'visited_edges': json_dict["visited_edges"],
            'best_exec': {}
        }
    if n_threads not in exec_stats[graph_name]['best_exec'].keys():
        exec_stats[graph_name]['best_exec'][n_threads] = {
            'best_th': None,
            'min_total_dist': None,
            'edges_gt0': None
        }
    for th_key in json_dict['th_placement_distances'].keys():
        for edge_key in json_dict['th_placement_distances'][th_key]:
            dist: int = json_dict['th_placement_distances'][th_key]
        # todo
        # total_dist +=
    a = 1
