import feedparser
import urllib.parse
import re
import requests
from datetime import datetime
from time import mktime
from typing import List
from bs4 import BeautifulSoup
from src.core.models import News
from src.scrapers.base_scraper import BaseScraper
from src.core.constants import (
    COUNTRY_SPECIFIC_DOMAINS, FIXED_RSS_SOURCES, BLACKLIST_URL_TERMS, 
    STRICT_NEGATIVE_KEYWORDS
)

class DynamicScraper(BaseScraper):
    def __init__(self):
        self.country_map = {
            "Argentina": {"gl": "AR", "hl": "es-419", "ceid": "AR:es-419", "geo": "Argentina"},
            "EE. UU.": {"gl": "US", "hl": "en-US", "ceid": "US:en", "geo": "USA"},
            "Japón": {"gl": "JP", "hl": "ja", "ceid": "JP:ja", "geo": "Japan"},
            "Brasil": {"gl": "BR", "hl": "pt-BR", "ceid": "BR:pt-419", "geo": "Brazil"},
            "México": {"gl": "MX", "hl": "es-419", "ceid": "MX:es-419", "geo": "Mexico"}
        }

    def fetch(self, country: str, query: str = "", **kwargs) -> List[News]:
        focus_mode = kwargs.get("focus_mode", False)
        news_list = []
        
        # 1. RSS Fijos (Inmunes a la IP)
        if country in FIXED_RSS_SOURCES:
            for source in FIXED_RSS_SOURCES[country]:
                news_list.extend(self._fetch_rss(source["url"], source["name"], country))

        # 2. Búsqueda Dinámica con Identidad de Navegador
        news_list.extend(self._fetch_dynamic(country, query, focus_mode))
        
        # 3. Filtrado
        cleaned_list = []
        for n in news_list:
            if not any(kw.lower() in (n.title + n.content).lower() for kw in STRICT_NEGATIVE_KEYWORDS):
                cleaned_list.append(n)
        
        return cleaned_list

    def _fetch_rss(self, url: str, name: str, country: str) -> List[News]:
        # Usamos un User-Agent para que el servidor no sea bloqueado
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(resp.content)
            results = []
            for entry in feed.entries:
                results.append(News(
                    title=self._clean_text(entry.title),
                    content=self._clean_text(entry.get('summary', entry.get('description', ''))),
                    url=entry.link,
                    date=datetime.now(),
                    source=name,
                    country=country
                ))
            return results
        except:
            return []

    def _fetch_dynamic(self, country: str, query: str, focus_mode: bool) -> List[News]:
        config = self.country_map.get(country, {"gl": "US", "hl": "en", "ceid": "US:en", "geo": ""})
        geo_tag = f" {config['geo']}" if config['geo'] else ""
        
        search_query = f"{query}{geo_tag}" if query else f"automotive industry{geo_tag}"
        if focus_mode:
            search_query += " (economy OR business OR industry)"
            
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://news.google.com/rss/search?q={encoded_query}+when:15d&hl={config['hl']}&gl={config['gl']}&ceid={config['ceid']}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(resp.content)
            results = []
            for entry in feed.entries:
                results.append(News(
                    title=self._clean_text(entry.title),
                    content="", # Evitamos exceso de data para no ser bloqueados
                    url=entry.link,
                    date=datetime.now(),
                    source=entry.source.get('title', 'Google News'),
                    country=country
                ))
            return results
        except:
            return []

    def _clean_text(self, html: str) -> str:
        if not html: return ""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ").strip()
