class Stage1YOTO(object):
    """
    This class is responsible give the edges for each thread.
    """

    def __init__(self, edges: list[list[list]], distance_table_bits: int, n_edges: int):
        """

        @param edges:
        @type edges:
        @param distance_table_bits:
        @type distance_table_bits:
        @param n_edges:
        @type n_edges:
        """
        self.edges: list[list[list]] = edges
        self.n_edges: int = n_edges
        self.distance_table_bits: int = distance_table_bits
        self.dist_table_mask: int = pow(2, distance_table_bits) - 1

        self.new_output: dict = {
            'th_idx': 0,
            'th_valid': False,
            'dist_table_line': 0,
            'a': 0,
            'b': 0,
        }

        self.old_output: dict = self.new_output.copy()

    def compute(self, st0_input: dict):
        """

        @param st0_input:
        @type st0_input:
        """
        # Move forward the output
        self.old_output = self.new_output.copy()

        # process the new output
        st0_th_idx: int = st0_input['th_idx']
        st0_th_valid: bool = st0_input['th_valid']
        st0_edge_n: int = st0_input['edg_n']

        edge_n_valid: bool = st0_edge_n < self.n_edges
        dist_table_line: int = (st0_th_idx ^ st0_edge_n) & self.dist_table_mask

        a, b = self.edges[st0_th_idx][st0_edge_n] if edge_n_valid else (0, 0)
        if b == 10:
            z=1

        self.new_output = {
            'th_idx': st0_th_idx,
            'th_valid': st0_th_valid and edge_n_valid,
            'dist_table_line': dist_table_line,
            'a': a,
            'b': b,
        }
