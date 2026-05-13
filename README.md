# Sistema Inteligente de Noticias (Argentina)

Este sistema modular en Python permite extraer, procesar y generar informes inteligentes de noticias argentinas. Utiliza una arquitectura desacoplada para facilitar la escalabilidad.

## Estructura del Proyecto

- `src/core/`: Definiciones fundamentales (modelos y constantes).
- `src/scrapers/`: Módulos de extracción de datos (soporta RSS).
- `src/processor/`: Inteligencia artificial para categorización, detección de zona y resumen.
- `src/reporter/`: Generación de informes profesionales en Markdown.
- `main.py`: Punto de entrada que orquesta el flujo completo.

## Requisitos

- Python 3.8+
- Dependencias: `feedparser`

Instalación:
```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar el sistema completo con los filtros configurados en `main.py`:

```bash
python main.py
```

El sistema generará un archivo `reporte_noticias.md` con el análisis de situación y el detalle de las noticias filtradas.

## Interfaz Web (Streamlit)

Para usar la aplicación de forma visual en tu navegador, ejecuta:

```bash
streamlit run app.py
```


## Cómo agregar nuevas fuentes

1. **RSS Directo**: Simplemente agrega la URL a la lista `sources` en `main.py`.
2. **Scraper Personalizado**: 
   - Crea un nuevo archivo en `src/scrapers/`.
   - Hereda de `BaseScraper`.
   - Implementa el método `fetch()` devolviendo una lista de objetos `News`.
   - Regístralo en `main.py`.

## Configuración de IA

El módulo `src/processor/ai_client.py` utiliza **TextBlob** para NLP y **deep-translator** para traducciones automáticas.
- **Categorización**: Basada en relevancia semántica (SMATA).
- **Traducción**: Las noticias internacionales (Japón, China, EE. UU.) se traducen automáticamente al español.
- **Resumen**: Genera resúmenes ejecutivos en texto plano, libres de HTML.


Para escalar a modelos más potentes (como GPT-4), puedes reemplazar la lógica interna del `AIClient` con llamadas a APIs externas.

