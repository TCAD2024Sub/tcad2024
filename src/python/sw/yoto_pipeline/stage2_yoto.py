class Stage2YOTO(object):
    """
    This class is responsible give the 'a' node's cell and line and column.
    """

    def __init__(self, n2c: list[list[list]], n_cells_sqrt: int, len_pipeline: int):
        """

        @param n2c:
        @type n2c:
        @param n_cells_sqrt:
        @type n_cells_sqrt:
        @param len_pipeline:
        @type len_pipeline:
        """
        self.len_pipeline: int = len_pipeline
        self.n_cells_sqrt: int = n_cells_sqrt
        self.n2c: list[list[list]] = n2c
        self.th_dist_table_counter: list[int] = [0 for _ in range(self.len_pipeline)]

        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'ia': 0,
            'ja': 0,
            'dist_table_line': 0,
            'dist_counter': 0,
            'b': 0,
        }

        self.old_output: dict = self.new_output.copy()

    def compute(self, st1_input: dict, st4_input: dict):
        """

        @param st1_input:
        @type st1_input:
        @param st4_input:
        @type st4_input:
        """
        # Move forward the output
        self.old_output = self.new_output.copy()

        # return update
        st4_th_idx: int = st4_input['th_idx']
        st4_th_valid = st4_input['th_valid']
        st4_place: bool = st4_input['place']
        st4_dist_counter: int = st4_input['dist_counter']
        st4_ib: int = st4_input['ib']
        st4_jb: int = st4_input['jb']
        st4_b: int = st4_input['b']
        if st4_place:
            self.n2c[st4_th_idx][st4_b][0] = st4_ib
            self.n2c[st4_th_idx][st4_b][1] = st4_jb
            self.th_dist_table_counter[st4_th_idx] = 0
        elif st4_th_valid:
            self.th_dist_table_counter[st4_th_idx] = st4_dist_counter + 1

        # process the new output
        st1_th_idx: int = st1_input['th_idx']
        st1_th_valid: bool = st1_input['th_valid']
        st1_dist_table_line: bool = st1_input['dist_table_line']
        st1_a: int = st1_input['a']
        st1_b: int = st1_input['b']

        ia: int = self.n2c[st1_th_idx][st1_a][0] if self.n2c[st1_th_idx][st1_a][0] is not None else 0
        ja: int = self.n2c[st1_th_idx][st1_a][1] if self.n2c[st1_th_idx][st1_a][1] is not None else 0
        dist_counter = self.th_dist_table_counter[st1_th_idx]

        if st1_b == 10:
            z=1

        self.new_output = {
            'th_idx': st1_th_idx,
            'th_valid': st1_th_valid,
            'ia': ia,
            'ja': ja,
            'dist_table_line': st1_dist_table_line,
            'dist_counter': dist_counter,
            'b': st1_b,
        }
