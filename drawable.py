from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self._marked = False
        
    @abstractmethod
    def info(self) -> str:
        pass
    
    @abstractmethod
    def draw(self) -> None:
        pass
    
    @abstractmethod
    def check_collision(self, mouse) -> bool:
        pass
    
    def toggle_marked(self):
        self._marked = not self._marked