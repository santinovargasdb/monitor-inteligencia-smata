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
        # Mapeo reforzado para evitar sesgos de IP del servidor
        self.country_map = {
            "Argentina": {"gl": "AR", "hl": "es-419", "ceid": "AR:es-419", "geo": "Argentina"},
            "EE. UU.": {"gl": "US", "hl": "en-US", "ceid": "US:en", "geo": "USA"},
            "China": {"gl": "CN", "hl": "zh-CN", "ceid": "CN:zh-Hans", "geo": "China"},
            "Japón": {"gl": "JP", "hl": "ja", "ceid": "JP:ja", "geo": "Japan"},
            "Alemania": {"gl": "DE", "hl": "de", "ceid": "DE:de", "geo": "Germany"},
            "Corea del Sur": {"gl": "KR", "hl": "ko", "ceid": "KR:ko", "geo": "Korea"},
            "Brasil": {"gl": "BR", "hl": "pt-BR", "ceid": "BR:pt-419", "geo": "Brazil"},
            "México": {"gl": "MX", "hl": "es-419", "ceid": "MX:es-419", "geo": "Mexico"}
        }

    def fetch(self, country: str, query: str = "", **kwargs) -> List[News]:
        focus_mode = kwargs.get("focus_mode", False)
        news_list = []
        
        # 1. RSS Fijos (Son inmunes a la IP, siempre traen lo mismo)
        if country in FIXED_RSS_SOURCES:
            for source in FIXED_RSS_SOURCES[country]:
                news_list.extend(self._fetch_rss(source["url"], source["name"], country))

        # 2. Búsqueda Dinámica Reforzada
        news_list.extend(self._fetch_dynamic(country, query, focus_mode))
        
        # 3. Filtrado Agresivo
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
        config = self.country_map.get(country, {"gl": "US", "hl": "en", "ceid": "US:en", "geo": ""})
        
        # Refuerzo Geográfico: Si estamos en la nube, añadimos el nombre del país al query
        geo_tag = f" {config['geo']}" if config['geo'] else ""
        
        if focus_mode:
            intent = " (economy OR business OR industry OR automotive)"
            search_query = f"{query}{geo_tag}{intent}" if query else f"automotive industry{geo_tag}{intent}"
        else:
            search_query = f"{query}{geo_tag}" if query else f"automotive news{geo_tag}"
            
        domains = COUNTRY_SPECIFIC_DOMAINS.get(country, [])
        if domains:
            site_filter = " OR ".join([f"site:{d}" for d in domains])
            search_query = f"({search_query}) AND ({site_filter} OR news)"
            
        encoded_query = urllib.parse.quote(search_query)
        # Añadimos parámetros explícitos para forzar la región a pesar de la IP del servidor
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
        return soup.get_text(separator=" ").strip()
