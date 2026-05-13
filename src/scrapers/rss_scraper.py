
import feedparser
import urllib.parse
import re
from datetime import datetime
from time import mktime
from typing import List
from bs4 import BeautifulSoup
from src.core.models import News
from src.scrapers.base_scraper import BaseScraper
from src.core.constants import (
    COUNTRY_SPECIFIC_DOMAINS, FIXED_RSS_SOURCES, BLACKLIST_URL_TERMS, 
    INTENT_KEYWORDS, AUTO_TERMINALS, STRICT_NEGATIVE_KEYWORDS
)

class DynamicScraper(BaseScraper):
    def __init__(self):
        self.country_map = {
            "Argentina": {"gl": "AR", "hl": "es-419", "ceid": "AR:es-419"},
            "EE. UU.": {"gl": "US", "hl": "en-US", "ceid": "US:en"},
            "China": {"gl": "CN", "hl": "zh-CN", "ceid": "CN:zh-Hans"},
            "Japón": {"gl": "JP", "hl": "ja", "ceid": "JP:ja"},
            "Alemania": {"gl": "DE", "hl": "de", "ceid": "DE:de"},
            "Corea del Sur": {"gl": "KR", "hl": "ko", "ceid": "KR:ko"},
            "Brasil": {"gl": "BR", "hl": "pt-BR", "ceid": "BR:pt-419"},
            "México": {"gl": "MX", "hl": "es-419", "ceid": "MX:es-419"}
        }

    def fetch(self, country: str, query: str = "", **kwargs) -> List[News]:
        focus_mode = kwargs.get("focus_mode", False)
        news_list = []
        
        # 1. RSS Fijos (Secciones de Economía/Negocios)
        if country in FIXED_RSS_SOURCES:
            for source in FIXED_RSS_SOURCES[country]:
                news_list.extend(self._fetch_rss(source["url"], source["name"], country))

        # 2. Búsqueda Dinámica
        news_list.extend(self._fetch_dynamic(country, query, focus_mode))
        
        # 3. FILTRADO AGRESIVO INMEDIATO (Eliminar deportes/chismes antes de que lleguen a la IA)
        cleaned_list = []
        for n in news_list:
            if self._is_blacklisted(n.url): continue
            if self._has_negative_keywords(n.title + " " + n.content): continue
            cleaned_list.append(n)
        
        return cleaned_list

    def _is_blacklisted(self, url: str) -> bool:
        url_lower = url.lower()
        return any(term in url_lower for term in BLACKLIST_URL_TERMS)

    def _has_negative_keywords(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in STRICT_NEGATIVE_KEYWORDS)

    def _fetch_rss(self, url: str, name: str, country: str) -> List[News]:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries:
            results.append(News(
                title=self._clean_text(entry.title),
                content=self._clean_text(entry.get('summary', entry.get('description', ''))),
                url=entry.link,
                date=self._parse_date(entry),
                source=name,
                country=country
            ))
        return results

    def _fetch_dynamic(self, country: str, query: str, focus_mode: bool) -> List[News]:
        config = self.country_map.get(country, {"gl": "US", "hl": "en", "ceid": "US:en"})
        
        # Refuerzo de intención para evitar secciones de deportes/sociedad
        if focus_mode:
            intent = " (economy OR business OR industry OR automotive)"
            search_query = f"{query}{intent}" if query else f"automotive industry{intent}"
        else:
            search_query = query if query else "automotive news"
            
        domains = COUNTRY_SPECIFIC_DOMAINS.get(country, []) + COUNTRY_SPECIFIC_DOMAINS.get("Global", [])
        if domains:
            site_filter = " OR ".join([f"site:{d}" for d in domains])
            search_query = f"({search_query}) AND ({site_filter} OR news)"
            
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://news.google.com/rss/search?q={encoded_query}+when:15d&hl={config['hl']}&gl={config['gl']}&ceid={config['ceid']}"
        
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries:
            results.append(News(
                title=self._clean_text(entry.title),
                content=self._clean_text(entry.get('summary', '')),
                url=entry.link,
                date=self._parse_date(entry),
                source=entry.source.get('title', 'Google News'),
                country=country
            ))
        return results

    def _parse_date(self, entry) -> datetime:
        if hasattr(entry, 'published_parsed'):
            return datetime.fromtimestamp(mktime(entry.published_parsed))
        return datetime.now()

    def _clean_text(self, html: str) -> str:
        if not html: return ""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")
        return re.sub(r'\s+', ' ', text).strip()
