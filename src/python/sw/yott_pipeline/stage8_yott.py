import math

from src.python.util.util import Util


class Stage8YOTT:
    def __init__(self):
        """

        @param tam_grid:
        @type tam_grid:
        @param len_pipe:
        @type len_pipe:
        @param c2n:
        @type c2n:
        """

        self.new_output: dict = {
            'should_write': 0,
            'thread_index': 0,
            'thread_valid': 0,
            'B': 0,
            'C_S': [0, 0],
            'cost': 0,
            'save_cel': 0,
            'dist_ca_cs': 0,
        }
        self.old_output: dict = self.new_output

    def compute(self, stage7):
        """
        @param stage5:
        @type stage5:
        @param stage0:
        @type stage0:
        """

        self.old_output: dict = self.new_output.copy()

        out_previous_stage: dict = stage7.old_output
        cost = out_previous_stage['cost']
        dist_ca_cs = out_previous_stage['dist_ca_cs']
        cel_free = out_previous_stage['cel_free']

        should_write = cel_free and ((dist_ca_cs < 3 and cost == 0) or (dist_ca_cs >= 3))

        save_cel = cel_free and dist_ca_cs < 3 and not should_write

        self.new_output = {
            'should_write': should_write,
            'thread_index': out_previous_stage['thread_index'],
            'thread_valid': out_previous_stage['thread_valid'],
            'B': out_previous_stage['B'],
            'cost': cost,
            'C_S': out_previous_stage['C_S'],
            'save_cel': save_cel,
            'dist_ca_cs': dist_ca_cs,
        }
