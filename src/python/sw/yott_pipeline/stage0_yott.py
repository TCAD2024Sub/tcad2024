from src.python.sw.yott_pipeline.IFIFO import IFIFO


class Stage0YOTT:
    def __init__(self, fifo: IFIFO, len_pipeline):
        """

        @param fifo:
        @type fifo:
        @param len_pipeline:
        @type len_pipeline:
        """
        self.fifo = fifo
        self.total_pipeline_counter = 0
        self.exec_counter: list[int] = [0 for _ in range(len_pipeline)]
        self.new_output: dict = {'thread_index': 0,
                                 'should_write': 0,
                                 'thread_valid': 0}
        self.old_output: dict = self.new_output

    def compute(self):
        """

        """
        self.old_output = self.new_output.copy()

        thread_valid = 1 if not self.fifo.is_empty() else 0
        thread_index, should_write = (0, 0) if thread_valid == 0 else self.fifo.get()  # type:ignore

        self.new_output = {'thread_index': thread_index,
                           'should_write': should_write,
                           'thread_valid': thread_valid}

        self.exec_counter[thread_index] += thread_valid
        self.total_pipeline_counter += 1
