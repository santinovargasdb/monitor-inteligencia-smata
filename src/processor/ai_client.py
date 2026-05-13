
import json
import re
from typing import Dict, Any, List, Optional
from textblob import TextBlob
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from src.core.constants import (
    SMATA_CORE_TERMS, SMATA_EXCLUDE_TERMS, INDUSTRIAL_ECOSYSTEM
)

class AIClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.price_pattern = re.compile(r'(\$|USD|EUR|¥|JPY)\s?(\d{1,3}(,\d{3})*(\.\d+)?|\d+)', re.IGNORECASE)

    def process_news(self, title: str, content: str, original_lang: str = 'es', search_query: str = "") -> Dict[str, Any]:
        clean_title = self._clean_html(title)
        clean_content = self._clean_html(content)
        full_text = f"{clean_title}. {clean_content}"
        text_lower = full_text.lower()
        
        # 1. VALIDACIÓN NEGATIVA OBLIGATORIA (Descarte instantáneo - SMATA_EXCLUDE_TERMS)
        if any(kw.lower() in text_lower for kw in SMATA_EXCLUDE_TERMS):
            return {
                "category": "Irrelevante (Deportes/Social)",
                "relevance_score": -100.0,
                "summary": "Noticia descartada por contenido no industrial.",
                "is_strictly_smata": False,
                "reasons_filtered": ["Contiene términos de exclusión (deportes/espectáculos)."]
            }

        # 2. VALIDACIÓN DEL ECOSISTEMA INDUSTRIAL (SMATA_CORE_TERMS)
        mentions_core = any(term.lower() in text_lower for term in SMATA_CORE_TERMS)
        mentions_ecosystem = any(term.lower() in text_lower for term in INDUSTRIAL_ECOSYSTEM)
        
        # Si no menciona el ecosistema industrial, es irrelevante
        if not (mentions_core or mentions_ecosystem):
            return {
                "category": None,
                "relevance_score": -50.0,
                "summary": "Sin conexión detectable con el ecosistema automotriz.",
                "is_strictly_smata": False,
                "reasons_filtered": ["No menciona terminales ni términos técnicos industriales."]
            }

        # 3. Cálculo de Relevancia y Categorización
        relevance_score = self._calculate_relevance_industrial(text_lower)
        category = self._categorize_industrial(text_lower)
        
        raw_summary = self._generate_base_summary(full_text)
        summary = raw_summary
        
        if original_lang and original_lang != 'es' and original_lang != 'unknown':
            try:
                summary = GoogleTranslator(source='auto', target='es').translate(raw_summary)
                summary = f"[TRADUCIDO] {summary}"
            except:
                summary = f"[MOCK] {raw_summary}"
            
        return {
            "category": category,
            "relevance_score": relevance_score,
            "summary": summary,
            "is_strictly_smata": relevance_score > 0,
            "reasons_filtered": []
        }

    def _calculate_relevance_industrial(self, text: str) -> float:
        score = 0.0
        # Gremial/Paritarias (Máxima prioridad)
        if any(w in text for w in ["paritaria", "convenio", "conciliación", "smata", "gremio"]):
            score += 15.0
        # Producción/Estado de Planta
        if any(w in text for w in ["suspensión", "parada de planta", "insumos", "operarios", "planta"]):
            score += 10.0
        # Terminales Core
        if any(term.lower() in text for term in SMATA_CORE_TERMS):
            score += 5.0
        return round(score, 1)

    def _categorize_industrial(self, text: str) -> Optional[str]:
        if any(w in text for w in ["paritaria", "convenio", "gremio"]): return "Gremial / Paritarias"
        if any(w in text for w in ["suspensión", "planta", "operarios"]): return "Estado de Planta"
        if any(w in text for w in ["inversión", "fábrica", "producción"]): return "Producción e Inversión"
        if any(w in text for w in ["híbrido", "eléctrico", "reconversión"]): return "Tecnología / Reconversión"
        return "Noticia Industrial General"

    def _clean_html(self, text: str) -> str:
        if not text: return ""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ").strip()

    def _generate_base_summary(self, text: str) -> str:
        blob = TextBlob(text)
        sentences = blob.sentences
        if len(sentences) > 0:
            return " ".join([str(s) for s in sentences[:2]])[:500]
        return text[:300]

    def generate_situation_analysis(self, news_list: List[Dict]) -> str:
        if not news_list: return "No se detectaron noticias industriales relevantes."
        total = len(news_list)
        return f"Auditoría Industrial: Se procesaron {total} noticias bajo las nuevas reglas de exclusión SMATA."
