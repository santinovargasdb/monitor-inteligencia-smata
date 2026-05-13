
from datetime import datetime, timedelta
from src.scrapers.rss_scraper import RSSScraper
from src.processor.classifier import NewsClassifier
from src.reporter.markdown_reporter import MarkdownReporter

def main():
    # 1. Configuración de fuentes
    sources = [
        {"name": "La Nación", "url": "https://www.lanacion.com.ar/arc/outboundfeeds/rss/"},
        {"name": "Clarín", "url": "https://www.clarin.com/rss/"},
        {"name": "Infobae", "url": "https://www.infobae.com/rss/"}
    ]

    # 2. Inicializar componentes
    scrapers = [RSSScraper(s["name"], s["url"]) for s in sources]
    classifier = NewsClassifier()
    reporter = MarkdownReporter()

    # 3. Obtener noticias
    print("Iniciando recolección de noticias...")
    all_news = []
    for scraper in scrapers:
        try:
            all_news.extend(scraper.fetch())
        except Exception as e:
            print(f"Error en scraper {scraper.name}: {e}")

    # 4. Definir filtros (Ejemplo: Últimas 24 horas, Mendoza y Buenos Aires, Economía y Política)
    start_date = datetime.now() - timedelta(days=1)
    target_zones = ["Mendoza", "Buenos Aires", "CABA", "Argentina"]
    target_types = ["Economía", "Política"]

    print(f"Procesando y filtrando {len(all_news)} noticias...")
    filtered_news = classifier.filter_and_process(
        all_news,
        start_date=start_date,
        target_zones=target_zones,
        target_types=target_types
    )

    # 5. Generar reporte
    if filtered_news:
        output_file = "reporte_noticias.md"
        reporter.generate(filtered_news, output_file)
    else:
        print("No se encontraron noticias que coincidan con los filtros.")

if __name__ == "__main__":
    main()
