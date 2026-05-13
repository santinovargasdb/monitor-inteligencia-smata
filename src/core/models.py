
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class News:
    title: str
    content: str
    url: str
    date: datetime
    source: str
    category: Optional[str] = None
    country: Optional[str] = None
    summary: Optional[str] = None
    language: Optional[str] = None
    original_language: Optional[str] = None
    relevance_score: float = 0.0

    @property
    def unique_id(self) -> str:
        return f"{self.url}_{self.date.strftime('%Y%m%d')}"

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "date": self.date.isoformat(),
            "source": self.source,
            "category": self.category,
            "country": self.country,
            "summary": self.summary,
            "language": self.language,
            "original_language": self.original_language,
            "relevance_score": self.relevance_score
        }
