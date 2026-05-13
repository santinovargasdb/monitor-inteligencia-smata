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
        # Mapeo completo institucional
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
        
        # 1. RSS Fijos (Prioridad)
        if country in FIXED_RSS_SOURCES:
            for source in FIXED_RSS_SOURCES[country]:
                news_list.extend(self._fetch_with_requests(source["url"], source["name"], country))

        # 2. Búsqueda Dinámica con Refuerzo Geo
        news_list.extend(self._fetch_dynamic(country, query, focus_mode))
        
        # 3. Filtrado de Ruido (Deportes/Farándula)
        cleaned_list = []
        for n in news_list:
            text = (n.title + " " + n.content).lower()
            if not any(kw.lower() in text for kw in STRICT_NEGATIVE_KEYWORDS):
                cleaned_list.append(n)
        
        return cleaned_list

    def _fetch_with_requests(self, url: str, name: str, country: str) -> List[News]:
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
        
        if focus_mode:
            intent = " (economy OR business OR industry OR automotive)"
            search_query = f"{query}{geo_tag}{intent}" if query else f"automotive industry{geo_tag}{intent}"
        else:
            search_query = f"{query}{geo_tag}" if query else f"automotive news{geo_tag}"
            
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://news.google.com/rss/search?q={encoded_query}+when:15d&hl={config['hl']}&gl={config['gl']}&ceid={config['ceid']}"
        
        return self._fetch_with_requests(url, "Google News", country)

    def _clean_text(self, html: str) -> str:
        if not html: return ""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")
        return re.sub(r'\s+', ' ', text).strip()
