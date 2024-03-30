from abc import ABC
import pandas


class IStatisticsGenerator(ABC):
    columns = ['Benchmark', 'N Edges', 'Visited Edges', 'Total Distance', 'Edges > 0', 'Arch Type', 'Algorithm',
               'Total Executions',"Throughput"]

    @staticmethod
    def generate_statistics_pandas(data_files: list[str]) -> pandas.DataFrame:
        pass

    @staticmethod
    def generate_data_dict(bench: str, n_edges: int, visited_edges: int, dist_total: int, edges_greater_0: int,
                           arch_type: str, algorithm: str, total_executions: int,th:float):
        return {IStatisticsGenerator.columns[0]: bench,
                IStatisticsGenerator.columns[1]: n_edges,
                IStatisticsGenerator.columns[2]: visited_edges,
                IStatisticsGenerator.columns[3]: dist_total,
                IStatisticsGenerator.columns[4]: edges_greater_0,
                IStatisticsGenerator.columns[5]: arch_type,
                IStatisticsGenerator.columns[6]: algorithm,
                IStatisticsGenerator.columns[7]: total_executions,
                IStatisticsGenerator.columns[8]: th
                }

    # @staticmethod
    # def write_df_to_csv(df: pandas.DataFrame, output_file_path: str, output_file_name: str):
    #     arch_types = df['Arch Type'].unique()
    #     # num_archs = len(arch_types)
    #     algorithms = (df['Algorithm'].unique())
    #     # num_algorithms = len(algorithms)
    #     total_executions_algorithms = (
    #         [sorted(df[df['Algorithm'] == algorithm]['Total Executions'].unique().tolist()) for algorithm in
    #          algorithms])

    #     assert (len(total_executions_algorithms) != 0)

    #     num_exec_per_algorithm = len(total_executions_algorithms[0])
    #     final_filter = []

    #     initial_filter = []
    #     for i, algorithm in enumerate(algorithms):
    #         filter = df[(df['Algorithm'] == algorithm)]
    #         for total_exec in total_executions_algorithms[i]:
    #             initial_filter.append(filter[filter['Total Executions'] == total_exec])

    #     final_filter = []

    #     for arch_type in arch_types:
    #         for filter in initial_filter:
    #             final_filter.append(filter[filter['Arch Type'] == arch_type])

    #     common_columns = ['Bench', 'N Edges', 'Visited Edges']
    #     head = ",,,"
    #     for i in range(num_exec_per_algorithm):
    #         cur_index = i
    #         arch_type = final_filter[i]['Arch Type'].unique().tolist()[0]
    #         algorithm = final_filter[i]['Algorithm'].unique().tolist()[0]
    #         total_execution = final_filter[i]['Total Executions'].unique().tolist()[0]

    #         head += f'{algorithm} - {total_execution} - {arch_type},,'
    #         final_filter[i] = final_filter[i].drop(['Arch Type', 'Algorithm', 'Total Executions'], axis=1)

    #         if i == 0:
    #             new_df = final_filter[i]
    #         else:
    #             new_df = new_df.merge(final_filter[i], on=common_columns,suffixes=('x', 'y'))
    #         while cur_index + num_exec_per_algorithm < len(final_filter):
    #             arch_type = final_filter[cur_index + num_exec_per_algorithm]['Arch Type'].unique().tolist()[0]
    #             algorithm = final_filter[cur_index + num_exec_per_algorithm]['Algorithm'].unique().tolist()[0]
    #             total_execution = \
    #                 final_filter[cur_index + num_exec_per_algorithm]['Total Executions'].unique().tolist()[0]
    #             head += f'{algorithm} - {total_execution} - {arch_type},, '
    #             final_filter[cur_index + num_exec_per_algorithm] = final_filter[
    #                 cur_index + num_exec_per_algorithm].drop(['Arch Type', 'Algorithm', 'Total Executions'], axis=1)

    #             new_df = new_df.merge(final_filter[cur_index + num_exec_per_algorithm], on=common_columns,suffixes=('x', 'y','z','w','k','p','j'))
    #             cur_index += num_exec_per_algorithm
    #     filename = output_file_path + output_file_name
    #     head += '\n'
    #     with open(filename, 'w') as file:
    #         file.write(head)
    #     new_df.to_csv(filename, mode='a', index=False)
