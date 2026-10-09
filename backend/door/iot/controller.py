from abc import ABC, abstractmethod


class IoTController(ABC):
    @abstractmethod
    def unlock(self, duration: int = 5) -> dict: ...

    @abstractmethod
    def lock(self) -> dict: ...

    @abstractmethod
    def status(self) -> dict: ...
