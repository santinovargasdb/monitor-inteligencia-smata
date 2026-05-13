
# Inteligencia Global y Automotriz (SMATA) - CONSTANTES UNIFICADAS

# Términos Core Industriales (Cadena de Valor)
SMATA_CORE_TERMS = [
    "SMATA", "sindicato", "gremio", "paritaria", "convenio colectivo", "CCT", 
    "delegado", "comisión interna", "suspensión", "despido", "retiro voluntario", 
    "parada de planta", "falta de insumos", "autopartista", "terminal automotriz",
    "cadena de valor", "producción mecánica", "ensamble", "línea de producción",
    "turno rotativo", "escalas salariales", "ACARA", "VTV",
    "híbrido", "eléctrico", "reconversión industrial", "movilidad sustentable",
    "Toyota", "Ford", "Volkswagen", "VW", "Stellantis", "Fiat", "Peugeot", 
    "Renault", "Nissan", "Mercedes-Benz", "General Motors", "GM"
]

# Ecosistema Industrial Ampliado
INDUSTRIAL_ECOSYSTEM = SMATA_CORE_TERMS + [
    "operarios", "planta industrial", "inversión productiva", "neumáticos", "metalmecánica", "manufactura"
]

# LISTA NEGRA DE EXCLUSIÓN (SMATA_EXCLUDE_TERMS)
SMATA_EXCLUDE_TERMS = [
    "gol", "partido", "semifinalista", "torneo", "apertura", "clausura", "campeonato",
    "Gran Hermano", "eliminado", "nominado", "recital", "concierto", "farándula",
    "fútbol", "tenis", "rugby", "espectáculo", "música", "cine", "teatro"
]

# Compatibilidad con nombres anteriores
STRICT_NEGATIVE_KEYWORDS = SMATA_EXCLUDE_TERMS
EXCLUDED_TOPICS = SMATA_EXCLUDE_TERMS
AUTO_TERMINALS = ["Toyota", "Ford", "Volkswagen", "VW", "General Motors", "GM", "Stellantis", "Fiat", "Peugeot", "Renault", "Nissan", "Mercedes-Benz"]

# Configuración de Países y Fuentes
COUNTRIES = ["Argentina", "EE. UU.", "China", "Japón", "Alemania", "Corea del Sur", "Brasil", "México"]
AUTO_CATEGORIES = ["Gremial / Paritarias", "Estado de Planta", "Producción e Inversión", "Tecnología / Reconversión"]

BLACKLIST_URL_TERMS = ["used", "inventory", "buy", "shop", "listing", "concesionario", "dealer", "marketplace"]
INTENT_KEYWORDS = ["economy", "business", "manufacturing", "automotive industry", "labor union"]

FIXED_RSS_SOURCES = {
    "Argentina": [
        {"name": "Ámbito Economía", "url": "https://www.ambito.com/rss/economia.xml"},
        {"name": "Ámbito Negocios", "url": "https://www.ambito.com/rss/negocios.xml"},
        {"name": "Cronista Economía", "url": "https://www.cronista.com/rss/economia.xml"}
    ]
}

COUNTRY_SPECIFIC_DOMAINS = {
    "Japón": ["global.toyota", "japantimes.co.jp", "nikkei.com"],
    "EE. UU.": ["pressroom.toyota.com", "reuters.com", "bloomberg.com", "autonews.com"]
}
