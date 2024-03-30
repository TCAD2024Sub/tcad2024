from abc import ABC, abstractmethod


class IFIFO(ABC):
    @abstractmethod
    def put(self, thread_index, should_write):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def init_fifo(self, num_threads):
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass
