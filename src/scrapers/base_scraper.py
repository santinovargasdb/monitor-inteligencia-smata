
from abc import ABC, abstractmethod
from typing import List
from src.core.models import News

class BaseScraper(ABC):
    @abstractmethod
    def fetch(self, **kwargs) -> List[News]:
        """Obtiene una lista de noticias de la fuente."""
        pass
