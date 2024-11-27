from abc import abstractmethod


class OutputDevice:
    pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def is_connected_and_running(self) -> bool:
        pass