
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from langdetect import detect
from src.core.models import News
from src.processor.ai_client import AIClient

class NewsClassifier:
    def __init__(self):
        self.ai_client = AIClient()

    def filter_and_process(
        self, 
        news_list: List[News], 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        target_countries: Optional[List[str]] = None,
        target_types: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        focus_mode: bool = False
    ) -> Tuple[List[News], Dict[str, Any]]:
        processed_news = []
        seen_urls = set()
        debug_info = {
            "total_found": len(news_list),
            "filtered_by_date": 0,
            "filtered_by_ai": 0,
            "ai_reasons": {}
        }
        
        try:
            for item in news_list:
                if item.url in seen_urls:
                    continue
                seen_urls.add(item.url)

                # 1. Filtro por fecha
                item_date = item.date.date() if isinstance(item.date, datetime) else item.date
                s_date = start_date.date() if hasattr(start_date, 'date') else start_date
                e_date = end_date.date() if hasattr(end_date, 'date') else end_date

                if s_date and item_date < s_date:
                    debug_info["filtered_by_date"] += 1
                    continue
                if e_date and item_date > e_date:
                    debug_info["filtered_by_date"] += 1
                    continue
                
                # 2. Detección de Idioma
                try:
                    item.original_language = detect(f"{item.title} {item.content}")
                except:
                    item.original_language = 'unknown'

                # 3. Procesamiento con IA
                ai_data = self.ai_client.process_news(item.title, item.content, item.original_language, search_query=search_query)
                
                is_strictly_smata = ai_data.get("is_strictly_smata", False)
                item.category = ai_data.get("category")
                item.relevance_score = ai_data.get("relevance_score", 0.0)
                item.summary = ai_data.get("summary")

                if focus_mode:
                    if not is_strictly_smata:
                        debug_info["filtered_by_ai"] += 1
                        reasons = ai_data.get("reasons_filtered", [])
                        for r in reasons:
                            debug_info["ai_reasons"][r] = debug_info["ai_reasons"].get(r, 0) + 1
                        continue
                else:
                    if not is_strictly_smata:
                        item.category = "⚠️ Información General / No Industrial"
                        item.relevance_score = -5.0

                processed_news.append(item)
                
            processed_news.sort(key=lambda x: x.relevance_score, reverse=True)
            
        except Exception as e:
            # En caso de error crítico, devolver lo procesado hasta ahora o lista vacía, pero siempre la tupla
            return processed_news, debug_info
        
        return processed_news, debug_info
