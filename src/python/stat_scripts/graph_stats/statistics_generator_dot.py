import re
import pandas
import json
from src.python.stat_scripts.graph_stats.interface_statistics_generator import IStatisticsGenerator
from src.python.util.util import Util


class StatisticsGeneratorDot(IStatisticsGenerator):
    @staticmethod
    def generate_statistics_pandas(data_files: list[str]) -> pandas.DataFrame:
        df = pandas.DataFrame(columns=IStatisticsGenerator.columns)
        pattern = re.compile(".weight=(\d+)")
        count = 0
        total_files = len(data_files)
        for dot_file in data_files:
            
            edges = 0
            distances = []
            with open(dot_file, 'r') as file:
                for row in file:
                    result = re.findall(pattern, row)
                    if len(result) > 0:
                        edges += 1
                        distances.append(int(result[0]))
            count_dists_greater_0 = 0
            dist_total = 0
            for distance in distances:
                dist_total += distance
                count_dists_greater_0 += 0 if distance == 0 else 1
            dirs = dot_file.split("/")
            dot_name = dirs[-1]
            th_worse, worse_path = Util.calc_worse_th_by_dot_file(dot_file,dot_name)

            dict_data = IStatisticsGenerator.generate_data_dict(dot_name.replace('.dot', ''),
                                                                edges,
                                                                None,
                                                                dist_total,
                                                                count_dists_greater_0,
                                                                dirs[-3],
                                                                dirs[-4],
                                                                dirs[-2],
                                                                th_worse
                                                                )
            df.loc[len(df)] = dict_data
            count+=1
            print(f'Generating Dataframe from traversal results: {count/total_files*100:.2f}%', end='\r',flush=True)

        return df

    # @staticmethod
    # def generate_statistics_iter(data_files: list[str]) -> pandas.DataFrame:
    #     df = pandas.DataFrame(columns=['Bench', 'Dist Total', 'Edges > 0', 'Total Executions', 'Max Iter', 'Arch Type'])
    #     pattern = re.compile(".weight=(\d+)")
    #     for dot_file in data_files:
    #         edges = 0
    #         distances = []
    #         with open(dot_file, 'r') as file:
    #             for row in file:
    #                 result = re.findall(pattern, row)
    #                 if len(result) > 0:
    #                     edges += 1
    #                     distances.append(int(result[0]))
    #         count_dists_greater_0 = 0
    #         dist_total = 0
    #         for distance in distances:
    #             dist_total += distance
    #             count_dists_greater_0 += 0 if distance == 0 else 1

    #         max_iter = re.findall('MI<\d+>', dot_file)[0]
    #         max_iter = max_iter.replace('MI<', '').replace('>', '')
    #         dirs = dot_file.split("/")
    #         bench = ''
    #         for letter in dirs[-1]:
    #             if letter == '.':
    #                 break
    #             bench += letter
    #         dict_data = {'Bench': bench, 'Dist Total': dist_total, 'Edges > 0': count_dists_greater_0,
    #                      'Arch Type': dirs[-3], 'Total Executions': dirs[-2], 'Max Iter': max_iter}

    #         df.loc[len(df)] =dict_data
    #     return df
