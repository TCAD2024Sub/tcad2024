# cython: language_level=3
import cython

from src.python.util.per_enum import ArchType
from src.python.util.util import Util


class Stage5SA:
    """
    Fifth Pipe from SA_Verilog. This pipe is responsible to find the manhandle
    distances for each combination between cellA and cellB with their
    respective neighbors cells after swap and execute the first 2-2 additions
    for the distances found in the left pipe.
    """

    def __init__(self, arch_type: ArchType, n_lines: cython.int, n_columns: cython.int):
        """

        """
        self.arch_type: ArchType = arch_type
        self.n_lines: cython.int = n_lines
        self.n_columns: cython.int = n_columns
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'dvac': [0, 0],
            'dvbc': [0, 0],
            'dvas': [0, 0, 0, 0],
            'dvbs': [0, 0, 0, 0]
        }
        self.old_output: dict = self.new_output.copy()

    def compute(self, st4_input: dict):
        """

        @param st4_input:
        """
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        st4_th_idx: cython.int = st4_input['th_idx']
        st4_th_valid: cython.bint = st4_input['th_valid']

        st4_cbs: cython.int = st4_input['cell_a']
        st4_cas: cython.int = st4_input['cell_b']
        st4_cva: list[cython.int] = st4_input['cva']
        st4_cvb: list[cython.int] = st4_input['cvb']
        st4_dvac: list[cython.int] = st4_input['dvac']
        st4_dvbc: list[cython.int] = st4_input['dvbc']

        # fixme only for debugging
        # if st4_th_idx == 0:
        #    z = 1

        dvac: list[cython.int] = [st4_dvac[0] + st4_dvac[1], st4_dvac[2] + st4_dvac[3]]
        dvbc: list[cython.int] = [st4_dvbc[0] + st4_dvbc[1], st4_dvbc[2] + st4_dvbc[3]]

        dvas: list[cython.int] = [0, 0, 0, 0]
        dvbs: list[cython.int] = [0, 0, 0, 0]

        for i in range(len(st4_cva)):
            if st4_cva[i] != -1:
                if self.arch_type == ArchType.ONE_HOP:
                    if st4_cas == st4_cva[i]:
                        dvas[i] = Util.dist_one_hop(
                            Util.get_line_column_from_cell(st4_cas, self.n_lines, self.n_columns),
                            Util.get_line_column_from_cell(st4_cbs, self.n_lines, self.n_columns)
                        )
                    else:
                        dvas[i] = Util.dist_one_hop(
                            Util.get_line_column_from_cell(st4_cas, self.n_lines, self.n_columns),
                            Util.get_line_column_from_cell(st4_cva[i], self.n_lines, self.n_columns)
                        )
                if self.arch_type == ArchType.MESH:
                    if st4_cas == st4_cva[i]:
                        dvas[i] = Util.dist_manhattan(
                            Util.get_line_column_from_cell(st4_cas, self.n_lines, self.n_columns),
                            Util.get_line_column_from_cell(st4_cbs, self.n_lines, self.n_columns)
                        )
                    else:
                        dvas[i] = Util.dist_manhattan(
                            Util.get_line_column_from_cell(st4_cas, self.n_lines, self.n_columns),
                            Util.get_line_column_from_cell(st4_cva[i], self.n_lines, self.n_columns)
                        )

        for i in range(len(st4_cvb)):
            if st4_cvb[i] != -1:
                if self.arch_type == ArchType.ONE_HOP:
                    if st4_cbs == st4_cvb[i]:
                        dvbs[i] = Util.dist_one_hop(
                            Util.get_line_column_from_cell(st4_cbs, self.n_lines, self.n_columns),
                            Util.get_line_column_from_cell(st4_cas, self.n_lines, self.n_columns)
                        )
                    else:
                        dvbs[i] = Util.dist_one_hop(
                            Util.get_line_column_from_cell(st4_cbs, self.n_lines, self.n_columns),
                            Util.get_line_column_from_cell(st4_cvb[i], self.n_lines, self.n_columns)
                        )
                elif self.arch_type == ArchType.MESH:
                    if st4_cbs == st4_cvb[i]:
                        dvbs[i] = Util.dist_manhattan(
                            Util.get_line_column_from_cell(st4_cbs, self.n_lines, self.n_columns),
                            Util.get_line_column_from_cell(st4_cas, self.n_lines, self.n_columns)
                        )
                    else:
                        dvbs[i] = Util.dist_manhattan(
                            Util.get_line_column_from_cell(st4_cbs, self.n_lines, self.n_columns),
                            Util.get_line_column_from_cell(st4_cvb[i], self.n_lines, self.n_columns)
                        )

        self.new_output: dict = {
            'th_idx': st4_th_idx,
            'th_valid': st4_th_valid,
            'dvac': dvac,
            'dvbc': dvbc,
            'dvas': dvas,
            'dvbs': dvbs
        }
