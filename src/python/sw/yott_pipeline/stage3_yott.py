class Stage3YOTT:
    def __init__(self, len_pipe, n2c):
        """

        @param len_pipe:
        @type len_pipe:
        @param n2c:
        @type n2c:
        """
        self.n2c = n2c
        self.thread_adj_indexes: list[int] = [0 for _ in range(len_pipe)]
        self.new_output: dict = {
            'thread_index': 0,
            'thread_valid': 0,
            'C_A': [0, 0],
            'B': 0,
            'Cs_C': [[0, 0], [0, 0], [0, 0]],
            'dist_CsB': [0, 0, 0],
            'adj_index': 0,
            'index_list_edge': 0
        }

        self.old_output: dict = self.new_output

    def compute(self, stage2, stage9):
        """

        @param stage2:
        @type stage2:
        @param stage6:
        @type stage6:
        """
        self.old_output = self.new_output.copy()

        out_stage9 = stage9.old_output
        old_thread_index = out_stage9['thread_index']

        if out_stage9['should_write']:
            old_b = out_stage9['B']
            old_c_s = out_stage9['C_S']
            self.n2c[old_thread_index][old_b] = old_c_s  # type:ignore
            self.thread_adj_indexes[old_thread_index] = 0
        elif out_stage9['thread_valid'] == 1:
            self.thread_adj_indexes[old_thread_index] += 1

        out_previous_stage = stage2.old_output
        thread_valid = out_previous_stage['thread_valid']
        thread_index = out_previous_stage['thread_index']
        a = out_previous_stage['A']
        cs = out_previous_stage['Cs']
        # Caso utilize mais anotacoes, em hardware sera necessario uma memoria para cada 2 leituras
        c_a = self.n2c[thread_index][a] if thread_valid == 1 else [0, 0]  # type:ignore
        cs_c = [self.n2c[thread_index][c] if c > -1 else [-1, -1] for c in cs]  # type:ignore

        adj_index = self.thread_adj_indexes[thread_index] if thread_valid else 0

        self.new_output = {
            'thread_index': thread_index,
            'thread_valid': thread_valid,
            'C_A': c_a,
            'B': out_previous_stage['B'],
            'Cs_C': cs_c,
            'dist_CsB': out_previous_stage['dist_CsB'],
            'adj_index': adj_index,
            'index_list_edge': out_previous_stage['index_list_edge']
        }
