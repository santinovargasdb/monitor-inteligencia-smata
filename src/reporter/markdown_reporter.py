
from typing import List
from datetime import datetime
from src.core.models import News
from src.processor.ai_client import AIClient

class MarkdownReporter:
    def __init__(self):
        self.ai_client = AIClient()

    def generate(self, news_list: List[News], output_path: str):
        # 1. Agrupar por categoría
        grouped = {}
        for news in news_list:
            cat = news.category or "Sin Categoría"
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(news)

        # 2. Generar análisis de situación global
        news_dicts = [n.to_dict() for n in news_list]
        situation_analysis = self.ai_client.generate_situation_analysis(news_dicts)

        # 3. Construir Markdown
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Informe de Inteligencia de Noticias\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## Análisis de Situación\n")
            f.write(f"{situation_analysis}\n\n")
            
            for category, items in grouped.items():
                f.write(f"## Categoría: {category}\n")
                for item in items:
                    f.write(f"### {item.title}\n")
                    f.write(f"**Fuente:** {item.source} | **Zona:** {item.zone} | **Fecha:** {item.date.strftime('%Y-%m-%d')}\n\n")
                    f.write(f"> {item.summary}\n\n")
                    f.write(f"[Leer original]({item.url})\n\n")
                    f.write("---\n\n")
        
        print(f"Reporte generado exitosamente en: {output_path}")
