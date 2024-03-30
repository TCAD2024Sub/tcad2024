import math

from src.python.util.util import Util


class Stage7YOTT:
    def __init__(self, tam_grid: int, len_pipe: int, c2n: list[list[list]]):
        """

        @param tam_grid:
        @type tam_grid:
        @param len_pipe:
        @type len_pipe:
        @param c2n:
        @type c2n:
        """
        self.tam_grid: int = tam_grid
        self.c2n: list[list[list]] = c2n
        self.new_output: dict = {
            'thread_index': 0,
            'thread_valid': 0,
            'B': 0,
            'cost': 0,
            'C_S': [0, 0],
            'cel_free': 0,
            'dist_ca_cs': 0
        }

        self.old_output: dict = self.new_output

    def compute(self, stage6, stage9):
        """

        @param stage5:
        @type stage5:
        @param stage0:
        @type stage0:
        """
        out_stage9 = stage9.old_output
        old_thread_index = out_stage9['thread_index']
        if out_stage9['should_write']:
            old_c_s = out_stage9['C_S']
            self.c2n[old_thread_index][old_c_s[0]][old_c_s[1]] = out_stage9['B']

        self.old_output: dict = self.new_output.copy()

        out_previous_stage: dict = stage6.old_output

        thread_index = out_previous_stage['thread_index']
        c_s = out_previous_stage['C_S']
        dist_ca_cs = out_previous_stage['dist_CA_CS']

        out_of_border = Util.is_out_of_border_sqr(c_s[0], c_s[1], self.tam_grid)

        cel_free = self.c2n[thread_index][c_s[0]][c_s[1]] == None if not out_of_border else False

        self.new_output = {
            'thread_index': out_previous_stage['thread_index'],
            'thread_valid': out_previous_stage['thread_valid'],
            'B': out_previous_stage['B'],
            'cost': out_previous_stage['cost'],
            'C_S': c_s,
            'cel_free': cel_free,
            'dist_ca_cs': dist_ca_cs
        }
