import math


class Stage9YOTT:
    def __init__(self, len_pipe: int, ):
        """

        @param tam_grid:
        @type tam_grid:
        @param len_pipe:
        @type len_pipe:
        @param c2n:
        @type c2n:
        """
        self.threads_current_adj_dists: list = [1 for _ in range(len_pipe)]
        self.threads_free_cel: list[list] = [[None, math.inf] for _ in range(len_pipe)]
        self.new_output: dict = {
            'should_write': 0,
            'thread_index': 0,
            'thread_valid': 0,
            'B': 0,
            'C_S': [0, 0],

        }
        self.old_output: dict = self.new_output

    def compute(self, stage8, stage0):
        """
        @param stage5:
        @type stage5:
        @param stage0:
        @type stage0:
        """
        self.old_output: dict = self.new_output.copy()

        out_previous_stage: dict = stage8.old_output

        thread_index = out_previous_stage['thread_index']
        cost = out_previous_stage['cost']
        c_s = out_previous_stage['C_S']
        should_write = out_previous_stage['should_write']
        save_cel = out_previous_stage['save_cel']
        dist_ca_cs = out_previous_stage['dist_ca_cs']
        thread_valid = out_previous_stage['thread_valid']

        was_there_change = dist_ca_cs != self.threads_current_adj_dists[thread_index]

        if save_cel and cost < self.threads_free_cel[thread_index][1]:
            self.threads_free_cel[thread_index] = [c_s, cost]

        if was_there_change:
            self.threads_current_adj_dists[thread_index] = dist_ca_cs
            if self.threads_free_cel[thread_index][0] is not None:
                c_s = self.threads_free_cel[thread_index][0]
                should_write = 1

        should_write = should_write and thread_valid

        if should_write:
            self.threads_current_adj_dists[thread_index] = 1
            self.threads_free_cel[thread_index] = [None, math.inf]  # type:ignore

        if thread_valid:
            stage0.fifo.put(thread_index, should_write)
       
        self.new_output = {
            'should_write': should_write,
            'thread_index': thread_index,
            'thread_valid': thread_valid,
            'B': out_previous_stage['B'],
            'C_S': c_s
        }
