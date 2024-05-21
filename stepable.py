from abc import ABC, abstractmethod

class Stepable(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        
    @abstractmethod
    def step(self) -> None:
        pass