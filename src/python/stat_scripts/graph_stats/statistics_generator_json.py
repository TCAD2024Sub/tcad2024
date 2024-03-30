from src.python.stat_scripts.graph_stats.interface_statistics_generator import IStatisticsGenerator
import pandas
import json
import re


class StatisticsGeneratorJSON(IStatisticsGenerator):
    @staticmethod
    def generate_statistics_pandas(data_files: list[str]) -> pandas.DataFrame:
        df = pandas.DataFrame(columns=IStatisticsGenerator.columns)
        total_files = len(data_files)
        count = 0 
        for json_file in data_files:
            with open(json_file, 'r') as file:
                json_data = json.load(file)

                results = json_data['results']
                th_results = results['best_throughput']
                placement_results = results['best_placement']

                count_dists_greater_0_placement = 0
                count_dists_greater_0_th = 0

                for distance in placement_results['th_placement_distances'].values():
                    count_dists_greater_0_placement += 0 if distance == 1 else 1
                
                for distance in th_results['th_placement_distances'].values():
                    count_dists_greater_0_th += 0 if distance == 1 else 1


                num_annotation = re.findall('NA<\d>', json_file)[0]
                num_annotation = num_annotation.replace('NA<', '').replace('>', '')
                dict_data_placement = IStatisticsGenerator.generate_data_dict(json_data['graph_name'].replace('.dot', ''),
                                                                    json_data['total_edges'],
                                                                    json_data['visited_edges'],
                                                                    placement_results['dist'],
                                                                    count_dists_greater_0_placement,
                                                                    json_data['arch_type'],
                                                                    json_data['algorithm'],
                                                                    json_data['total_threads'],
                                                                    placement_results['throughput']
                                                                    )
                dict_data_throughput = IStatisticsGenerator.generate_data_dict(json_data['graph_name'].replace('.dot', ''),
                                                                    json_data['total_edges'],
                                                                    json_data['visited_edges'],
                                                                    th_results['dist'],
                                                                    count_dists_greater_0_th,
                                                                    json_data['arch_type'],
                                                                    json_data['algorithm'],
                                                                    json_data['total_threads'],
                                                                    th_results['throughput']
                                                                    )
                
                
                df.loc[len(df)] = dict_data_placement
                df.loc[len(df)] = dict_data_throughput
            count += 1
            print(f'Generating DataFrame with our placement results: {count/total_files*100:.2f}%', end='\r',flush=True)
        print(''*40+'\n')
        return df
