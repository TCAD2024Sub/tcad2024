class Stage1YOTT:
    def __init__(self, len_pipe: int, num_threads, len_edges) -> None:
        """

        @param len_pipe:
        @type len_pipe:
        @param num_threads:
        @type num_threads:
        @param len_edges:
        @type len_edges:
        """
        self.edges_indexes = [0 for _ in range(len_pipe)]
        self.len_edges = len_edges
        self.len_pipe = len_pipe
        self.threads_done = [0 if thread_index < num_threads else 1 for thread_index in range(len_pipe)]

        self.done: bool = False

        self.new_output = {
            'thread_index': 0,
            'edge_index': 0,
            'thread_valid': 0
        }

        self.old_output: dict = self.new_output

    def compute(self, stage0):
        """

        @param stage0:
        @type stage0:
        """
        self.old_output = self.new_output.copy()
        out_previous_stage: dict = stage0.old_output

        thread_index = out_previous_stage['thread_index']
        should_write = out_previous_stage['should_write']
        thread_valid = out_previous_stage['thread_valid']

        edge_index = self.edges_indexes[thread_index] + should_write
        self.edges_indexes[thread_index] = edge_index

        thread_done = 1 if edge_index == self.len_edges else 0

        self.threads_done[thread_index] = thread_done

        self.done = sum(self.threads_done) == self.len_pipe
        if thread_done == 1:
            thread_valid = 0
            edge_index = 0

        self.new_output = {
            'thread_index': thread_index,
            'edge_index': edge_index,
            'thread_valid': thread_valid
        }
