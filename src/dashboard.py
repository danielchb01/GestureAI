# dashboard.py - Dashboard para ver las estadisticas del juego
# Se ejecuta con: streamlit run src/dashboard.py

import os
import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import streamlit as st

# Esto es para que matplotlib no de problemas
matplotlib.use("Agg")

# Ruta a la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "partidas.db")


# --- Funcion para cargar los datos de la BD ---

@st.cache_data(ttl=5)
def cargar_datos() -> pd.DataFrame:
    """Lee todas las partidas de la BD y las mete en un dataframe."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM partidas ORDER BY id ASC", conn
        )
        conn.close()

        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()


# --- Configuracion de la pagina ---

st.set_page_config(
    page_title="GesturaAI — Dashboard",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo gaming oscuro con toques neon
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

    /* Fondo general */
    .stApp {
        background: linear-gradient(180deg, #0a0e17 0%, #0d1321 50%, #0a0e17 100%);
    }

    /* Titulo principal */
    .main-title {
        text-align: center;
        font-family: 'Orbitron', monospace;
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: 4px;
        text-transform: uppercase;
        background: linear-gradient(90deg, #00f0ff, #7b2fff, #ff2d95);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        text-shadow: 0 0 30px rgba(0,240,255,0.3);
    }
    .sub-title {
        text-align: center;
        font-family: 'Rajdhani', sans-serif;
        color: #4a5568;
        font-size: 1rem;
        letter-spacing: 6px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    /* Linea decorativa tipo HUD */
    .hud-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00f0ff, #7b2fff, #ff2d95, transparent);
        margin: 0.5rem auto 2rem auto;
        width: 60%;
        border-radius: 2px;
    }

    /* Metricas */
    [data-testid="stMetric"] {
        background: rgba(13, 19, 33, 0.8);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #6b7fa3 !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        color: #00f0ff !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080c14 0%, #0d1321 100%);
        border-right: 1px solid rgba(0, 240, 255, 0.1);
    }

    /* Headers de secciones */
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #c0d0e8;
        border-left: 3px solid #00f0ff;
        padding-left: 12px;
        margin: 1.5rem 0 1rem 0;
    }

    /* Tabla */
    .stDataFrame {
        border: 1px solid rgba(0, 240, 255, 0.1) !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --- Titulo del dashboard ---

st.markdown('<p class="main-title">GesturaAI</p>', unsafe_allow_html=True)
st.markdown('<div class="hud-line"></div>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Performance Dashboard</p>',
            unsafe_allow_html=True)

# Cargamos los datos
df = cargar_datos()

if df.empty:
    st.warning("No hay partidas registradas todavia. "
               "Juega algunas rondas y vuelve a cargar el dashboard.")
    st.info("Ejecuta el juego con: `python src/main.py`")
    st.stop()


# --- Sidebar con filtros ---

st.sidebar.markdown('<p class="section-header">Filtros</p>',
                    unsafe_allow_html=True)

# Filtro por fecha
if "timestamp" in df.columns:
    fecha_min = df["timestamp"].min().date()
    fecha_max = df["timestamp"].max().date()
    rango = st.sidebar.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )
    if len(rango) == 2:
        mask = (df["timestamp"].dt.date >= rango[0]) & \
               (df["timestamp"].dt.date <= rango[1])
        df = df[mask]


# Filtro por gesto con toggles
st.sidebar.markdown("**Filtrar por gesto**")
show_stone = st.sidebar.toggle("Stone", value=True)
show_paper = st.sidebar.toggle("Paper", value=True)
show_scissor = st.sidebar.toggle("Scissor", value=True)

gestos_sel = []
if show_stone: gestos_sel.append("Stone")
if show_paper: gestos_sel.append("Paper")
if show_scissor: gestos_sel.append("Scissor")

if gestos_sel:
    df = df[df["gesto_usuario"].isin(gestos_sel)]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Mostrando {len(df)} partidas**")
if st.sidebar.button("Refrescar datos"):
    st.cache_data.clear()
    st.rerun()

# Win rate por gesto en el sidebar
st.sidebar.markdown("---")
st.sidebar.markdown('<p class="section-header">Win Rate por gesto</p>',
                    unsafe_allow_html=True)
for gesto in ["Stone", "Paper", "Scissor"]:
    df_gesto = cargar_datos()
    df_gesto = df_gesto[df_gesto["gesto_usuario"] == gesto]
    if len(df_gesto) > 0:
        wins = len(df_gesto[df_gesto["resultado"] == "victoria"])
        total_g = len(df_gesto)
        pct = round((wins / total_g) * 100, 1)
        st.sidebar.markdown(f"**{gesto}**: {pct}% ({wins}/{total_g})")
    else:
        st.sidebar.markdown(f"**{gesto}**: sin datos")


# --- Metricas principales ---

st.markdown('<p class="section-header">Metricas globales</p>',
            unsafe_allow_html=True)

total = len(df)
victorias = len(df[df["resultado"] == "victoria"])
derrotas = len(df[df["resultado"] == "derrota"])
empates = len(df[df["resultado"] == "empate"])
pct_victorias = round((victorias / total) * 100, 1) if total > 0 else 0

# Calculamos la mejor racha de victorias
racha_actual = 0
mejor_racha = 0
for r in df.sort_values("id")["resultado"]:
    if r == "victoria":
        racha_actual += 1
        mejor_racha = max(mejor_racha, racha_actual)
    else:
        racha_actual = 0

confianza_media = round(df["confianza"].mean() * 100, 1) if total > 0 else 0.0

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("PARTIDAS", total)
col2.metric("VICTORIAS", victorias)
col3.metric("DERROTAS", derrotas)
col4.metric("EMPATES", empates)
col5.metric("MEJOR RACHA", mejor_racha)
col6.metric("CONFIANZA MEDIA", f"{confianza_media}%")

# Barra con el porcentaje de victorias
st.markdown(f"**Win Rate: {pct_victorias}%**")
st.progress(pct_victorias / 100)

st.markdown("---")


# --- Grafica 1: Tarta con los resultados ---

col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<p class="section-header">Distribucion de resultados</p>',
                unsafe_allow_html=True)

    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_facecolor("#0a0e17")
    ax1.set_facecolor("#0a0e17")

    resultados_count = df["resultado"].value_counts()
    colores = {"victoria": "#00d26a", "derrota": "#ff2d55", "empate": "#6b7fa3"}
    colors = [colores.get(r, "#888") for r in resultados_count.index]
    etiquetas = [r.capitalize() for r in resultados_count.index]

    wedges, texts, autotexts = ax1.pie(
        resultados_count.values,
        labels=etiquetas,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.85,
        textprops={"color": "#c0d0e8", "fontsize": 11,
                    "fontfamily": "monospace"}
    )
    for autotext in autotexts:
        autotext.set_fontweight("bold")
        autotext.set_color("white")

    # Le hacemos un agujero en el centro para que quede tipo donut
    centre_circle = plt.Circle((0, 0), 0.60, fc="#0a0e17")
    ax1.add_artist(centre_circle)
    ax1.set_title("Win / Lose / Draw",
                   color="#c0d0e8", fontsize=12, pad=15,
                   fontfamily="monospace", fontweight="bold")

    st.pyplot(fig1)
    plt.close(fig1)


# --- Grafica 2: Barras con los gestos mas usados ---

with col_right:
    st.markdown('<p class="section-header">Gestos mas usados</p>',
                unsafe_allow_html=True)

    fig2, ax2 = plt.subplots(figsize=(6, 5))
    fig2.patch.set_facecolor("#0a0e17")
    ax2.set_facecolor("#0a0e17")

    gestos_count = df["gesto_usuario"].value_counts()

    neon_colors = ["#00f0ff", "#7b2fff", "#ff2d95"]
    bars = ax2.barh(gestos_count.index, gestos_count.values,
                    color=neon_colors[:len(gestos_count)],
                    edgecolor="none", height=0.5)

    ax2.set_xlabel("Veces usado", color="#6b7fa3", fontsize=10,
                    fontfamily="monospace")
    ax2.set_title("Player Gesture Distribution",
                   color="#c0d0e8", fontsize=12, pad=15,
                   fontfamily="monospace", fontweight="bold")
    ax2.tick_params(colors="#6b7fa3")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["bottom"].set_color("#1a2236")
    ax2.spines["left"].set_color("#1a2236")

    # Ponemos los numeros al lado de cada barra
    for bar, val in zip(bars, gestos_count.values):
        ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                 str(val), color="#00f0ff", va="center", fontsize=12,
                 fontweight="bold", fontfamily="monospace")

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)


st.markdown("---")


# --- Grafica 3: Linea con la evolucion del score ---

st.markdown('<p class="section-header">Evolucion del score</p>',
            unsafe_allow_html=True)

fig3, ax3 = plt.subplots(figsize=(12, 4))
fig3.patch.set_facecolor("#0a0e17")
ax3.set_facecolor("#0a0e17")

df_sorted = df.sort_values("id")
ax3.plot(range(len(df_sorted)), df_sorted["score_acumulado"],
         color="#00f0ff", linewidth=2, marker="o", markersize=4,
         markerfacecolor="#7b2fff", markeredgecolor="#7b2fff")
ax3.fill_between(range(len(df_sorted)), df_sorted["score_acumulado"],
                  alpha=0.08, color="#00f0ff")
ax3.axhline(y=0, color="#1a2236", linestyle="--", linewidth=0.8)
ax3.set_xlabel("Round", color="#6b7fa3", fontsize=10, fontfamily="monospace")
ax3.set_ylabel("Score", color="#6b7fa3", fontsize=10, fontfamily="monospace")
ax3.set_title("Score Progression",
               color="#c0d0e8", fontsize=12, pad=15,
               fontfamily="monospace", fontweight="bold")
ax3.tick_params(colors="#6b7fa3")
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.spines["bottom"].set_color("#1a2236")
ax3.spines["left"].set_color("#1a2236")

plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)


# --- Grafica 3b: Win rate por dia ---

st.markdown('<p class="section-header">Win rate por dia</p>',
            unsafe_allow_html=True)

if "timestamp" in df.columns:
    # Agrupamos por fecha y calculamos el win rate de cada dia
    df_daily = df.copy()
    df_daily["fecha"] = df_daily["timestamp"].dt.date
    df_daily["es_victoria"] = (df_daily["resultado"] == "victoria").astype(int)
    wr_por_dia = df_daily.groupby("fecha")["es_victoria"].mean().reset_index()
    wr_por_dia["win_rate"] = (wr_por_dia["es_victoria"] * 100).round(1)

    fig3b, ax3b = plt.subplots(figsize=(12, 3))
    fig3b.patch.set_facecolor("#0a0e17")
    ax3b.set_facecolor("#0a0e17")

    ax3b.plot(range(len(wr_por_dia)), wr_por_dia["win_rate"],
              color="#ff2d95", linewidth=2, marker="o", markersize=5,
              markerfacecolor="#7b2fff", markeredgecolor="#7b2fff")
    ax3b.fill_between(range(len(wr_por_dia)), wr_por_dia["win_rate"],
                      alpha=0.08, color="#ff2d95")
    ax3b.axhline(y=50, color="#1a2236", linestyle="--",
                 linewidth=0.8, label="50%")
    ax3b.set_ylim(0, 100)
    ax3b.set_xticks(range(len(wr_por_dia)))
    ax3b.set_xticklabels([str(f) for f in wr_por_dia["fecha"]],
                          rotation=30, ha="right", fontsize=8,
                          color="#6b7fa3")
    ax3b.set_xlabel("Fecha", color="#6b7fa3", fontsize=10, fontfamily="monospace")
    ax3b.set_ylabel("Win Rate (%)", color="#6b7fa3", fontsize=10,
                    fontfamily="monospace")
    ax3b.set_title("Daily Win Rate",
                   color="#c0d0e8", fontsize=12, pad=15,
                   fontfamily="monospace", fontweight="bold")
    ax3b.tick_params(colors="#6b7fa3")
    ax3b.spines["top"].set_visible(False)
    ax3b.spines["right"].set_visible(False)
    ax3b.spines["bottom"].set_color("#1a2236")
    ax3b.spines["left"].set_color("#1a2236")

    plt.tight_layout()
    st.pyplot(fig3b)
    plt.close(fig3b)
else:
    st.info("No hay datos de fecha disponibles para calcular el win rate por dia.")


st.markdown("---")


# --- Grafica 4: Boxplot de la confianza por gesto ---

st.markdown('<p class="section-header">Confianza del modelo por gesto</p>',
            unsafe_allow_html=True)

fig4, ax4 = plt.subplots(figsize=(8, 4))
fig4.patch.set_facecolor("#0a0e17")
ax4.set_facecolor("#0a0e17")

bp = sns.boxplot(data=df, x="gesto_usuario", y="confianza",
            palette=["#00f0ff", "#7b2fff", "#ff2d95"], ax=ax4,
            flierprops=dict(markerfacecolor="#6b7fa3", markersize=4),
            boxprops=dict(edgecolor="#6b7fa3"),
            whiskerprops=dict(color="#6b7fa3"),
            capprops=dict(color="#6b7fa3"),
            medianprops=dict(color="white", linewidth=2))
ax4.set_xlabel("Gesture", color="#6b7fa3", fontsize=10, fontfamily="monospace")
ax4.set_ylabel("Confidence", color="#6b7fa3", fontsize=10, fontfamily="monospace")
ax4.set_title("Model Confidence Distribution",
               color="#c0d0e8", fontsize=12, pad=15,
               fontfamily="monospace", fontweight="bold")
ax4.tick_params(colors="#6b7fa3")
ax4.spines["top"].set_visible(False)
ax4.spines["right"].set_visible(False)
ax4.spines["bottom"].set_color("#1a2236")
ax4.spines["left"].set_color("#1a2236")

plt.tight_layout()
st.pyplot(fig4)
plt.close(fig4)


st.markdown("---")


# --- Tabla con el historial ---

st.markdown('<p class="section-header">Historial de partidas</p>',
            unsafe_allow_html=True)

n_mostrar = st.slider("Partidas a mostrar", 5, min(100, len(df)),
                       min(20, len(df)))

df_display = df.sort_values("id", ascending=False).head(n_mostrar).copy()
df_display["timestamp"] = df_display["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
df_display["confianza"] = df_display["confianza"].apply(lambda x: f"{x:.2%}")
df_display["resultado"] = df_display["resultado"].apply(lambda r: r.upper())

st.dataframe(
    df_display[["id", "timestamp", "gesto_usuario", "gesto_ia",
                "resultado", "confianza", "score_acumulado"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "id": "ID",
        "timestamp": "Fecha/Hora",
        "gesto_usuario": "Tu Gesto",
        "gesto_ia": "Gesto IA",
        "resultado": "Resultado",
        "confianza": "Confianza",
        "score_acumulado": "Score"
    }
)

# Boton para descargar el historial como CSV
df_csv = df.sort_values("id", ascending=False).copy()
df_csv["timestamp"] = df_csv["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
st.download_button(
    label="⬇️ Exportar historial a CSV",
    data=df_csv.to_csv(index=False, encoding="utf-8-sig"),
    file_name="gesturaai_historial.csv",
    mime="text/csv",
    help="Descarga todas las partidas del periodo seleccionado"
)


# --- Footer ---

st.markdown("---")
st.markdown(
    '<p style="text-align:center; font-family:Rajdhani,sans-serif; '
    'color:#2a3550; font-size:0.75rem; letter-spacing:3px; '
    'text-transform:uppercase;">'
    'GesturaAI Analytics // 2026</p>',
    unsafe_allow_html=True
)
