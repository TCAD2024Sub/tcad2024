from src.python.util.per_enum import ArchType
from src.python.util.util import Util


class Stage4YOTT:
    def __init__(self, arch_type: ArchType, dimension_arch, distance_table_bits, make_shuffle) -> None:
        """

        @param dimension_arch:
        @type dimension_arch:
        @param len_pipeline:
        @type len_pipeline:
        @param distance_table_bits:
        @type distance_table_bits:
        @param make_shuffle:
        @type make_shuffle:
        """
        self.dimension_arch: int = dimension_arch
        self.distance_table: list[list] = [Util.get_distance_table(arch_type, self.dimension_arch, make_shuffle) for
                                           _ in range(pow(2, distance_table_bits))]
        self.new_output: dict = {
            'thread_index': 0,
            'thread_valid': 0,
            'B': 0,
            'C_S': [0, 1],
            'Cs_C': [[0, 0], [0, 0], [0, 0]],
            'C_A': [0, 0],
            'dist_CsB': [0, 0, 0],
        }
        self.old_output: dict = self.new_output

    def compute(self, stage3):
        """

        @param stage3:
        @type stage3:
        """
        self.old_output = self.new_output.copy()

        out_previous_stage = stage3.old_output
        thread_index = out_previous_stage['thread_index']
        index_list_edge = out_previous_stage['index_list_edge']

        adj_index = out_previous_stage['adj_index']
        c_a = out_previous_stage['C_A']
        i, j = self.distance_table[index_list_edge][adj_index]
        c_s = [c_a[0] + i, c_a[1] + j]
        self.new_output = {
            'thread_index': thread_index,
            'thread_valid': out_previous_stage['thread_valid'],
            'B': out_previous_stage['B'],
            'C_S': c_s,
            'C_A': c_a,
            'Cs_C': out_previous_stage['Cs_C'],
            'dist_CsB': out_previous_stage['dist_CsB'],
        }
