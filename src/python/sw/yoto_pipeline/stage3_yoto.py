from src.python.util.per_enum import ArchType
from src.python.util.util import Util


class Stage3YOTO(object):
    """
    This class is responsible give one possible neighbor cell of 'a'.
    """

    def __init__(self, arch_type: ArchType, n_cells_sqrt: int, distance_table_bits: int, make_shuffle: bool):
        self.arch_type = arch_type
        self.n_cells_sqrt: int = n_cells_sqrt
        self.distance_table_bits: int = distance_table_bits
        self.n_distance_tables = pow(2, self.distance_table_bits)
        self.make_shuffle = make_shuffle
        self.distance_table: list[list[list]] = [
            Util.get_distance_table(self.arch_type, self.n_cells_sqrt, self.make_shuffle) for _ in
            range(self.n_distance_tables)]

        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'ib': 0,
            'jb': 0,
            'dist_counter': 0,
            'b': 0,
        }

        self.old_output: dict = self.new_output.copy()

    def compute(self, st2_input: dict):
        # Move forward the output
        self.old_output = self.new_output.copy()

        # process the new output
        st2_th_idx: int = st2_input['th_idx']
        st2_th_valid: bool = st2_input['th_valid']
        st2_ia: int = st2_input['ia']
        st2_ja: int = st2_input['ja']
        st2_dist_table_line: int = st2_input['dist_table_line']
        st2_dist_counter: int = st2_input['dist_counter']
        st2_b: int = st2_input['b']

        add_i, add_j = self.distance_table[st2_dist_table_line][st2_dist_counter]

        ib: int = st2_ia + add_i
        jb: int = st2_ja + add_j

        if st2_b == 10:
            z=1

        self.new_output = {
            'th_idx': st2_th_idx,
            'th_valid': st2_th_valid,
            'ib': ib,
            'jb': jb,
            'dist_counter': st2_dist_counter,
            'b': st2_b,
        }
