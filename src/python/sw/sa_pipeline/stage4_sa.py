# cython: language_level=3
import cython

from src.python.util.per_enum import ArchType
from src.python.util.util import Util


class Stage4SA:
    """
    Fourth Pipe from SA_Verilog. This pipe is responsible to find the manhandle
    distances for each combination between cellA and cellB with their
    respective neighbors cells before swap.
    """

    def __init__(self, arch_type: ArchType, n_lines: cython.int, n_columns: cython.int):
        """
        @param n_lines:
        @param n_columns:

        """
        self.arch_type: ArchType = arch_type
        self.n_lines: cython.int = n_lines
        self.n_columns: cython.int = n_columns
        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'cell_a': 0,
            'cell_b': 0,
            'cva': [-1, -1, -1, -1],
            'cvb': [-1, -1, -1, -1],
            'dvac': [0, 0, 0, 0],
            'dvbc': [0, 0, 0, 0]
        }
        self.old_output: dict = self.new_output.copy()

    def compute(self, st3_input: dict):
        """

        @param st3_input:
        """
        # moving forward the ready outputs
        self.old_output = self.new_output.copy()

        st3_th_idx: cython.int = st3_input['th_idx']
        st3_th_valid: cython.bint = st3_input['th_valid']
        st3_cell_a: cython.int = st3_input['cell_a']
        st3_cell_b: cython.int = st3_input['cell_b']
        st3_cva: list = st3_input['cva']
        st3_cvb: list = st3_input['cvb']

        # fixme only for debugging
        # if st3_th_idx == 0:
        #    z = 1

        dvac: list[cython.int] = [0, 0, 0, 0]
        dvbc: list[cython.int] = [0, 0, 0, 0]

        ca: cython.int = st3_input['cell_a']
        cb: cython.int = st3_input['cell_b']
        cva: list[cython.int] = st3_input['cva']
        cvb: list[cython.int] = st3_input['cvb']

        for i in range(len(cva)):
            if cva[i] != -1:
                if self.arch_type == ArchType.ONE_HOP:
                    dvac[i] = Util.dist_one_hop(
                        Util.get_line_column_from_cell(ca, self.n_lines, self.n_columns),
                        Util.get_line_column_from_cell(cva[i], self.n_lines, self.n_columns)
                    )
                elif self.arch_type == ArchType.MESH:
                    dvac[i] = Util.dist_manhattan(
                        Util.get_line_column_from_cell(ca, self.n_lines, self.n_columns),
                        Util.get_line_column_from_cell(cva[i], self.n_lines, self.n_columns)
                    )

        for i in range(len(cvb)):
            if cvb[i] != -1:
                if self.arch_type == ArchType.ONE_HOP:
                    dvbc[i] = Util.dist_one_hop(
                        Util.get_line_column_from_cell(cb, self.n_lines, self.n_columns),
                        Util.get_line_column_from_cell(cvb[i], self.n_lines, self.n_columns)
                    )
                elif self.arch_type == ArchType.MESH:
                    dvbc[i] = Util.dist_manhattan(
                        Util.get_line_column_from_cell(cb, self.n_lines, self.n_columns),
                        Util.get_line_column_from_cell(cvb[i], self.n_lines, self.n_columns)
                    )

        self.new_output: dict = {
            'th_idx': st3_th_idx,
            'th_valid': st3_th_valid,
            'cell_a': st3_cell_a,
            'cell_b': st3_cell_b,
            'cva': st3_cva,
            'cvb': st3_cvb,
            'dvac': dvac,
            'dvbc': dvbc
        }
