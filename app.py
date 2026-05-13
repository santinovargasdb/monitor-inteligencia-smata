
import streamlit as st
from datetime import datetime, timedelta
from src.scrapers.rss_scraper import DynamicScraper
from src.processor.classifier import NewsClassifier
from src.core.constants import COUNTRIES, AUTO_CATEGORIES

# Configuración de página institucional
st.set_page_config(
    page_title="SMATA - Inteligencia de Planta", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS Institucional
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-title { color: #00843D; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f0f2f6; color: #262730; text-align: center; padding: 10px; font-size: 0.8rem; border-top: 1px solid #e0e0e0; z-index: 999; }
    </style>
    """, unsafe_allow_html=True)

# --- Barra Lateral ---
with st.sidebar:
    st.markdown("<h2 style='color: #00843D; text-align: center; border-bottom: 2px solid #00843D; padding-bottom: 10px;'>SMATA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>Inteligencia Sindical</p>", unsafe_allow_html=True)
    st.divider()
    
    st.header("Control de Inteligencia")
    
    focus_mode = st.toggle(
        "Modo Estricto SMATA", 
        value=True, 
        help="Solo muestra noticias de terminales, paritarias y estado de planta."
    )

    search_query = st.text_input(
        "Búsqueda Técnica",
        placeholder="Ej: Toyota, Paritarias",
        value=""
    )

    today = datetime.now()
    date_range = st.date_input(
        "Ventana de Monitoreo",
        value=(today - timedelta(days=7), today),
        max_value=today
    )

    selected_countries = st.multiselect(
        "Polos Industriales",
        options=COUNTRIES,
        default=["Argentina", "Japón", "EE. UU."]
    )

# --- Contenido Principal ---
st.markdown("<h1 class='main-title'>Inteligencia de Planta y Cadena de Valor</h1>", unsafe_allow_html=True)

if st.sidebar.button("Iniciar Auditoría de Noticias", use_container_width=True):
    scraper = DynamicScraper()
    classifier = NewsClassifier()
    
    all_raw_news = []
    
    progress_bar = st.progress(0, text="Auditoría en curso...")
    for i, country in enumerate(selected_countries):
        with st.status(f"Auditando fuentes en {country}...", expanded=False):
            try:
                # El scraper usa **kwargs para aceptar focus_mode sin errores
                news_found = scraper.fetch(country, query=search_query, focus_mode=focus_mode)
                all_raw_news.extend(news_found)
                st.write(f"Procesadas {len(news_found)} fuentes.")
            except Exception as e:
                # Si un país falla, mostramos aviso y seguimos
                st.warning(f"Aviso: No se pudo completar el rastreo en {country}. Continuando con el resto.")
                st.caption(f"Detalle técnico: {e}")
        progress_bar.progress((i + 1) / len(selected_countries))

    with st.spinner("Validando impacto en la cadena de valor..."):
        start_date = date_range[0] if len(date_range) > 0 else None
        end_date = date_range[1] if len(date_range) > 1 else None

        # classifier.filter_and_process siempre devuelve una tupla (lista, dict)
        filtered_news, debug_info = classifier.filter_and_process(
            all_raw_news,
            start_date=start_date,
            end_date=end_date,
            search_query=search_query,
            focus_mode=focus_mode
        )

    # --- Resultados ---
    if filtered_news:
        st.success(f"Auditoría completada: {len(filtered_news)} reportes críticos detectados.")
        
        ai_client = classifier.ai_client
        try:
            analysis = ai_client.generate_situation_analysis([n.to_dict() for n in filtered_news])
            st.info(f"### Resumen para el Cuerpo de Delegados\n{analysis}")
        except:
            st.warning("El análisis ejecutivo no pudo generarse.")

        for item in filtered_news:
            if item.relevance_score >= 8:
                label = "ALTA PRIORIDAD"
                border_color = "#FF4B4B"
            else:
                label = "INDUSTRIA GLOBAL"
                border_color = "#00843D"
            
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"<h3 style='margin-bottom: 0;'>{item.title}</h3>", unsafe_allow_html=True)
                    st.caption(f"📍 {item.country} | 🏭 {item.source} | 🗓️ {item.date.strftime('%d/%m/%Y')}")
                with col2:
                    st.markdown(f"<div style='border: 1px solid {border_color}; color: {border_color}; padding: 5px; text-align: center; border-radius: 5px; font-weight: bold; font-size: 0.7rem;'>{label}</div>", unsafe_allow_html=True)
                    st.caption(f"📂 {item.category}")
                st.write(item.summary)
                st.link_button("Ver documento original", item.url)
    else:
        st.warning("No se detectaron reportes críticos bajo los criterios actuales.")
        
        # Mostrar información de depuración
        with st.expander("Ver detalle de auditoría (Debug)"):
            st.write(f"Noticias encontradas inicialmente: {debug_info.get('total_found', 0)}")
            st.write(f"Filtradas por fecha: {debug_info.get('filtered_by_date', 0)}")
            st.write(f"Filtradas por IA (Modo Estricto): {debug_info.get('filtered_by_ai', 0)}")
            reasons = debug_info.get('ai_reasons', {})
            if reasons:
                st.write("**Razones principales del filtrado:**")
                for reason, count in reasons.items():
                    st.write(f"- {reason} ({count} noticias)")

# Pie de Página
st.markdown("<div class='footer'>Derechos reservados SMATA</div>", unsafe_allow_html=True)
