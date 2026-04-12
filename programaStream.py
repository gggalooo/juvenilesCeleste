import streamlit as st
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# --- 1. CONFIGURACIÓN VISUAL ---
# ==========================================
st.set_page_config(page_title="Regatas Manager Pro", layout="wide", page_icon="⚽")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #002d62 !important; border-right: 3px solid #e63946; }
    [data-testid="stSidebar"] * { color: white !important; }
    .metric-card {
        background-color: #161b22; padding: 20px; border-radius: 12px;
        border-left: 5px solid #00aae4; border-right: 5px solid #e63946;
        margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-title { color: #8b949e; font-size: 14px; text-transform: uppercase; font-weight: bold; }
    .metric-value { color: white !important; font-size: 24px; font-weight: bold; }
    .forma-badge {
        display: inline-block; width: 32px; height: 32px; border-radius: 50%;
        text-align: center; line-height: 32px; font-weight: bold; font-size: 14px; margin: 2px;
    }
    .forma-G { background-color: #2ea043; color: white; }
    .forma-E { background-color: #e3a62f; color: white; }
    .forma-P { background-color: #e63946; color: white; }
    .countdown-card {
        background: linear-gradient(135deg, #002d62, #00aae4); padding: 24px;
        border-radius: 16px; text-align: center; box-shadow: 0 8px 24px rgba(0,170,228,0.3); margin-bottom: 20px;
    }
    .countdown-title { color: #cce7ff; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
    .countdown-rival { color: white; font-size: 22px; font-weight: bold; margin-bottom: 12px; }
    .countdown-time { color: #00aae4; font-size: 36px; font-weight: bold; background: #0e1117; border-radius: 10px; padding: 10px 20px; display: inline-block; }
    .pred-card { background-color: #161b22; padding: 16px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
    .stButton>button { background-color: #00aae4; color: white; border-radius: 8px; font-weight: bold; border: none; transition: 0.3s; width: 100%;}
    .stButton>button:hover { background-color: #e63946 !important; transform: scale(1.02); }
    .stTable { background-color: #161b22 !important; color: white !important; border-radius: 10px !important; border: 1px solid #30363d !important; }
    .stTable thead tr th { background-color: #e63946 !important; color: white !important; font-size: 16px; }
    .stTable tbody tr td { color: white !important; border-bottom: 1px solid #30363d !important; background-color: #161b22 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# --- 2. CONEXIÓN GSPREAD ---
# ==========================================
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1BkBD5F1F5PZ27KND_7cJMIvy9-s5wtKXP7hQKwAqDNA/edit"

def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"],
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

# ==========================================
# --- 3. LIGA Y FIXTURE ---
# ==========================================
class Liga:
    def __init__(self):
        self.equipos = ["Regatas Celeste", "Club Harrods", "Centro Galicia", "Banco Ciudad Negro",
                        "Esc. Daniel Messina", "Sitas Rojo", "A.F. Tocalli", "Porteño A.C.",
                        "River Plate 'F. Cavenaghi'", "Geba", "Club Santa Barbara", "Vilo"]
        r1 = [("Sitas Rojo", False), ("Club Santa Barbara", True), ("A.F. Tocalli", False),
              ("Banco Ciudad Negro", True), ("Esc. Daniel Messina", False), ("Centro Galicia", True),
              ("Geba", False), ("River Plate 'F. Cavenaghi'", False), ("Porteño A.C.", True),
              ("Vilo", False), ("Club Harrods", True)]
        self.fixture_completo = r1 + [(r, not l) for r, l in r1]
        # *** AJUSTÁ ESTAS FECHAS A TU CALENDARIO REAL ***
        self.fechas_datetime = [
            datetime(2025, 4, 11), datetime(2025, 4, 18), datetime(2025, 4, 25),
            datetime(2025, 5, 2), datetime(2025, 5, 9), datetime(2025, 5, 16),
            datetime(2025, 5, 23), datetime(2025, 5, 30), datetime(2025, 5, 6),
            datetime(2025, 6, 13), datetime(2025, 6, 14), datetime(2025, 6, 21),
            datetime(2025, 6, 28), datetime(2025, 7, 5), datetime(2025, 7, 12),
            datetime(2025, 7, 19), datetime(2025, 7, 26), datetime(2025, 8, 2),
            datetime(2025, 8, 9), datetime(2025, 8, 16), datetime(2025, 8, 23),
            datetime(2025, 8, 30),
        ]

# ==========================================
# --- 4. FUNCIONES DE GUARDADO ---
# ==========================================
def guardar_datos(estado):
    try:
        gc = get_gspread_client()
        sh = gc.open_by_url(SPREADSHEET_URL)
        df_tabla = pd.DataFrame(estado["tabla"]).T.reset_index().rename(columns={'index': 'Equipo'})
        ws = sh.worksheet("Tabla"); ws.clear()
        ws.update([df_tabla.columns.tolist()] + df_tabla.values.tolist())
        df_historial = pd.DataFrame(estado["historial"])
        ws2 = sh.worksheet("Historial"); ws2.clear()
        if not df_historial.empty:
            ws2.update([df_historial.columns.tolist()] + df_historial.values.tolist())
        datos_p = [[k] + v for k, v in estado["plantel"].items()]
        df_plantel = pd.DataFrame(datos_p, columns=['ID','Nombre','PJ','Goles','Asist','Amarillas','Rojas','MVP','Vallas'])
        ws3 = sh.worksheet("Plantel"); ws3.clear()
        ws3.update([df_plantel.columns.tolist()] + df_plantel.values.tolist())
        st.success("🔥 ¡Sincronizado con Google Sheets!")
    except Exception as e:
        st.error(f"Error: {e}")

def get_or_create_worksheet(sh, nombre):
    try:
        return sh.worksheet(nombre)
    except:
        return sh.add_worksheet(title=nombre, rows=200, cols=10)

def guardar_votos_mvp(data_votos):
    try:
        gc = get_gspread_client()
        sh = gc.open_by_url(SPREADSHEET_URL)
        ws = get_or_create_worksheet(sh, "VotosMVP")
        ws.clear()
        ws.update([["Nombre", "Voto", "Fecha"]] + data_votos)
    except Exception as e:
        st.error(f"Error guardando votos: {e}")

def cargar_votos_mvp():
    try:
        gc = get_gspread_client()
        sh = gc.open_by_url(SPREADSHEET_URL)
        ws = get_or_create_worksheet(sh, "VotosMVP")
        return ws.get_all_records()
    except:
        return []

def guardar_predicciones(data_preds):
    try:
        gc = get_gspread_client()
        sh = gc.open_by_url(SPREADSHEET_URL)
        ws = get_or_create_worksheet(sh, "Predicciones")
        ws.clear()
        ws.update([["Nombre", "Fecha", "G_Reg", "G_Riv", "Rival", "Timestamp"]] + data_preds)
    except Exception as e:
        st.error(f"Error guardando predicciones: {e}")

def cargar_predicciones():
    try:
        gc = get_gspread_client()
        sh = gc.open_by_url(SPREADSHEET_URL)
        ws = get_or_create_worksheet(sh, "Predicciones")
        return ws.get_all_records()
    except:
        return []

# ==========================================
# --- 5. CARGA INICIAL DE DATOS ---
# ==========================================
if 'db' not in st.session_state:
    try:
        gc = get_gspread_client()
        sh = gc.open_by_url(SPREADSHEET_URL)
        df_t = pd.DataFrame(sh.worksheet("Tabla").get_all_records())
        df_h = pd.DataFrame(sh.worksheet("Historial").get_all_records())
        df_p = pd.DataFrame(sh.worksheet("Plantel").get_all_records())
        st.session_state.db = {
            "tabla": df_t.set_index('Equipo').to_dict('index'),
            "historial": df_h.to_dict('records'),
            "fecha_actual": len(df_h) + 1,
            "plantel": {str(r['ID']): [r['Nombre'],r['PJ'],r['Goles'],r['Asist'],r['Amarillas'],r['Rojas'],r['MVP'],r['Vallas']] for _, r in df_p.iterrows()}
        }
    except:
        st.session_state.db = {
            "fecha_actual": 1, "historial": [],
            "tabla": {eq: {"PTS": 0, "PJ": 0, "PG": 0, "PE": 0, "PP": 0, "GF": 0, "GC": 0} for eq in Liga().equipos},
            "plantel": {
                "1": ["Toro",0,0,0,0,0,0,0], "2": ["Ochoa",0,0,0,0,0,0,0], "3": ["Peña",0,0,0,0,0,0,0],
                "4": ["Caputo",0,0,0,0,0,0,0], "5": ["Amato",0,0,0,0,0,0,0], "6": ["Basto",0,0,0,0,0,0,0],
                "7": ["Tano",0,0,0,0,0,0,0], "8": ["Ciro",0,0,0,0,0,0,0], "9": ["Rocca",0,0,0,0,0,0,0],
                "10": ["Beni",0,0,0,0,0,0,0], "11": ["Feli",0,0,0,0,0,0,0], "13": ["Juani Blanco",0,0,0,0,0,0,0],
                "14": ["Galo",0,0,0,0,0,0,0], "15": ["Capri",0,0,0,0,0,0,0], "16": ["Vigna",0,0,0,0,0,0,0],
                "17": ["Lucio",0,0,0,0,0,0,0], "18": ["Mateo",0,0,0,0,0,0,0], "19": ["Zurdo",0,0,0,0,0,0,0],
                "20": ["Pena",0,0,0,0,0,0,0], "21": ["Churri",0,0,0,0,0,0,0], "22": ["Giacovino",0,0,0,0,0,0,0],
                "23": ["Manu",0,0,0,0,0,0,0]
            }
        }

def procesar_tabla(e1, g1, e2, g2):
    t = st.session_state.db["tabla"]
    for e, gf, gc in [(e1, g1, g2), (e2, g2, g1)]:
        t[e]["PJ"] += 1; t[e]["GF"] += gf; t[e]["GC"] += gc
        if gf > gc: t[e]["PTS"] += 3; t[e]["PG"] += 1
        elif gf == gc: t[e]["PTS"] += 1; t[e]["PE"] += 1
        else: t[e]["PP"] += 1

def metric_card(title, value):
    st.markdown(f'<div class="metric-card"><div class="metric-title">{title}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

def forma_reciente(historial, n=5):
    ultimos = historial[-n:] if len(historial) >= n else historial
    badges = ""
    for p in ultimos:
        if p['g_reg'] > p['g_riv']: letra, cls = "G", "forma-G"
        elif p['g_reg'] == p['g_riv']: letra, cls = "E", "forma-E"
        else: letra, cls = "P", "forma-P"
        badges += f'<span class="forma-badge {cls}">{letra}</span>'
    return badges or "<span style='color:#8b949e'>Sin partidos</span>"

# ==========================================
# --- 6. SIDEBAR ---
# ==========================================
st.sidebar.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <div style='font-size: 52px;'>⚓</div>
        ...
        <h2 style='color:white; margin:0;'>REGATAS</h2>
        <p style='color:#00aae4; margin:0; font-size:11px; letter-spacing:3px;'>JUVENILES CELESTE</p>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("NAVEGACIÓN", [
    "🏠 INICIO", "🏆 TABLA", "👤 PLANTEL", "🎥 GOLES",
    "⚠️ TARJETAS", "🔮 PREDICCIONES", "🏅 VOTAR MVP",
    "📝 CARGAR FECHA", "📅 FIXTURE"
])

plantel_dict = st.session_state.db["plantel"]
jugadores_lista = [f"{n}-{d[0]}" for n, d in plantel_dict.items()]

# ==========================================
# --- 7. PÁGINAS ---
# ==========================================

if menu == "🏠 INICIO":
    st.markdown("<h1 style='text-align:center;'>⚽ JUVENILES CELESTE</h1>", unsafe_allow_html=True)
    if os.path.exists("img/banner.png"):
        st.image("img/banner.png", use_container_width=True)
    st.divider()

    liga = Liga()
    idx = st.session_state.db["fecha_actual"] - 1
    hist = st.session_state.db.get("historial", [])
    tabla_reg = st.session_state.db["tabla"].get("Regatas Celeste", {})
    pj = tabla_reg.get("PJ", 0)
    pg = tabla_reg.get("PG", 0)
    pe = tabla_reg.get("PE", 0)
    pp = tabla_reg.get("PP", 0)
    pts = tabla_reg.get("PTS", 0)

    # Countdown
    if idx < len(liga.fixture_completo):
        riv, loc = liga.fixture_completo[idx]
        cond = "LOCAL 🏠" if loc else "VISITANTE ✈️"
        if idx < len(liga.fechas_datetime):
            diff = liga.fechas_datetime[idx] - datetime.now()
            if diff.total_seconds() > 0:
                dias, horas, mins = diff.days, diff.seconds // 3600, (diff.seconds % 3600) // 60
                tiempo = f"{dias}d {horas}h {mins}m"
            else:
                tiempo = "¡HOY ES EL DÍA! 🔥"
            st.markdown(f"""<div class="countdown-card">
                <div class="countdown-title">⏱ PRÓXIMO PARTIDO — FECHA {idx+1} — {cond}</div>
                <div class="countdown-rival">Regatas vs {riv}</div>
                <div class="countdown-time">{tiempo}</div>
            </div>""", unsafe_allow_html=True)

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("🏆 PUNTOS", pts)
    with c2: metric_card("✅ VICTORIAS", pg)
    with c3: metric_card("➖ EMPATES", pe)
    with c4: metric_card("❌ DERROTAS", pp)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 RENDIMIENTO")
        if pj > 0:
            fig = go.Figure(data=[go.Pie(
                labels=["Victorias", "Empates", "Derrotas"], values=[pg, pe, pp], hole=0.5,
                marker_colors=["#2ea043", "#e3a62f", "#e63946"]
            )])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_color="white", margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin partidos jugados aún.")

    with col2:
        st.subheader("🔥 FORMA RECIENTE")
        st.markdown(forma_reciente(hist), unsafe_allow_html=True)
        if hist:
            ult = hist[-1]
            metric_card("ÚLTIMO RESULTADO", f"Regatas {ult['g_reg']} - {ult['g_riv']} {ult['rival']}")
        st.divider()
        st.subheader("👑 REY DEL MVP")
        jugadores_campo = {k: v for k, v in plantel_dict.items() if k != "1"}
        if jugadores_campo:
            max_mvp = max(v[6] for v in jugadores_campo.values())
            if max_mvp > 0:
                mvp_kings = [v[0] for v in jugadores_campo.values() if v[6] == max_mvp]
                metric_card("MVP ACUMULADO", f"{', '.join(mvp_kings)} ({max_mvp})")

elif menu == "🏆 TABLA":
    st.header("🏆 TABLA DE POSICIONES")
    df = pd.DataFrame(st.session_state.db["tabla"]).T
    df['DG'] = df['GF'] - df['GC']
    df_sorted = df.sort_values(by=["PTS", "DG"], ascending=False)[['PTS','PJ','PG','PE','PP','GF','GC','DG']]
    def highlight_regatas(row):
        if row.name == "Regatas Celeste":
            return ['background-color: #002d62; color: #00aae4; font-weight: bold'] * len(row)
        return [''] * len(row)
    st.dataframe(df_sorted.style.apply(highlight_regatas, axis=1), use_container_width=True)

elif menu == "👤 PLANTEL":
    st.header("📊 ESTADÍSTICAS DEL PLANTEL")
    jugadores_campo = {k: v for k, v in plantel_dict.items() if k != "1"}
    max_goles = max((v[2] for v in jugadores_campo.values()), default=0)
    goleadores = [v[0] for v in jugadores_campo.values() if v[2] == max_goles and max_goles > 0]
    max_asist = max((v[3] for v in jugadores_campo.values()), default=0)
    asistidores = [v[0] for v in jugadores_campo.values() if v[3] == max_asist and max_asist > 0]
    col_l1, col_l2 = st.columns(2)
    with col_l1: metric_card("⚽ MÁXIMO GOLEADOR", f"{', '.join(goleadores) if goleadores else 'Sin goles'} ({max_goles})")
    with col_l2: metric_card("🎯 MÁXIMO ASISTIDOR", f"{', '.join(asistidores) if asistidores else 'Sin asistencias'} ({max_asist})")
    st.divider()
    st.subheader("⚽ RANKING GOLEADORES")
    goles_data = sorted([(v[0], v[2]) for k, v in jugadores_campo.items() if v[2] > 0], key=lambda x: x[1], reverse=True)
    if goles_data:
        nombres, goles = zip(*goles_data)
        fig = px.bar(x=list(goles), y=list(nombres), orientation='h',
                     color=list(goles), color_continuous_scale=["#002d62", "#00aae4"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="white", showlegend=False, coloraxis_showscale=False, margin=dict(t=10,b=10))
        fig.update_xaxes(color="white"); fig.update_yaxes(color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aún no hay goles registrados.")
    st.divider()
    st.subheader("📋 Ficha General")
    datos_tabla = [{"NRO": int(nro), "JUGADOR": d[0], "PJ": d[1],
                    "GOLES": d[2] if nro != "1" else "-", "ASIST": d[3] if nro != "1" else "-",
                    "V. INVICTAS": d[7] if nro == "1" else "-", "MVP": d[6]} for nro, d in plantel_dict.items()]
    st.dataframe(pd.DataFrame(datos_tabla), use_container_width=True, hide_index=True)
    st.divider()
    sel = st.selectbox("Detalle individual:", jugadores_lista)
    nro_sel = sel.split("-")[0]; s = plantel_dict[nro_sel]
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("PARTIDOS", s[1])
    with c2: metric_card("V. INVICTAS" if nro_sel == "1" else "GOLES", s[7] if nro_sel == "1" else s[2])
    with c3: metric_card("ASISTENCIAS", s[3])
    with c4: metric_card("MVP", s[6])

elif menu == "🎥 GOLES":
    st.header("🎬 GALERÍA DE VIDEOS")
    if st.session_state.db["fecha_actual"] > 1:
        fecha_vid = st.selectbox("Elegí Fecha:", [f"Fecha {i}" for i in range(1, st.session_state.db["fecha_actual"])])
        num_f = fecha_vid.split(" ")[1]; enc = False
        for i in range(1, 11):
            vid_path = f"videos/F{num_f}_{i}.mp4"
            if os.path.exists(vid_path): st.video(vid_path); enc = True
        if not enc:
            cp = f"videos/F{num_f}.mp4"
            if os.path.exists(cp): st.video(cp)
            else: st.warning("Video no encontrado.")
    else:
        st.info("Todavía no hay partidos jugados.")

elif menu == "⚠️ TARJETAS":
    st.header("⚠️ CONTROL DE DISCIPLINARIOS")
    data_disc = [{"NRO": k, "NOMBRE": v[0], "AMARILLAS": v[4], "ROJAS": v[5]} for k, v in plantel_dict.items()]
    df_disc = pd.DataFrame(data_disc).sort_values(by="AMARILLAS", ascending=False)
    st.dataframe(df_disc, use_container_width=True, hide_index=True)
    en_riesgo = [v[0] for v in plantel_dict.values() if v[4] >= 3]
    if en_riesgo:
        st.warning(f"⚠️ En riesgo de suspensión: {', '.join(en_riesgo)}")

elif menu == "🔮 PREDICCIONES":
    st.header("🔮 PREDICCIONES DEL PARTIDO")
    liga = Liga()
    idx = st.session_state.db["fecha_actual"] - 1
    if idx < len(liga.fixture_completo):
        rival, local = liga.fixture_completo[idx]
        st.subheader(f"Fecha {idx+1}: Regatas vs {rival} ({'LOCAL' if local else 'VISITANTE'})")
        st.write("¿Cuál creés que va a ser el resultado?")
        with st.form("pred_form"):
            nombre = st.text_input("Tu nombre")
            c1, c2 = st.columns(2)
            g_reg_pred = c1.number_input("Goles Regatas", 0, 20)
            g_riv_pred = c2.number_input(f"Goles {rival}", 0, 20)
            if st.form_submit_button("🔮 ENVIAR PREDICCIÓN") and nombre:
                preds = cargar_predicciones()
                preds_filtradas = [p for p in preds if not (str(p.get('Nombre','')) == nombre and str(p.get('Fecha','')) == str(idx+1))]
                nueva = [nombre, idx+1, g_reg_pred, g_riv_pred, rival, datetime.now().strftime("%Y-%m-%d %H:%M")]
                data_guardar = [[p['Nombre'],p['Fecha'],p['G_Reg'],p['G_Riv'],p['Rival'],p['Timestamp']] for p in preds_filtradas] + [nueva]
                guardar_predicciones(data_guardar)
                st.success(f"¡Predicción de {nombre} guardada! {g_reg_pred}-{g_riv_pred}")
        st.divider()
        st.subheader("📋 Predicciones de todos")
        preds = cargar_predicciones()
        preds_fecha = [p for p in preds if str(p.get('Fecha','')) == str(idx+1)]
        if preds_fecha:
            for p in preds_fecha:
                st.markdown(f'<div class="pred-card"><b>{p["Nombre"]}</b> predice: <span style="color:#00aae4; font-size:20px; font-weight:bold;">Regatas {p["G_Reg"]} - {p["G_Riv"]} {p["Rival"]}</span></div>', unsafe_allow_html=True)
        else:
            st.info("Nadie predijo todavía. ¡Sé el primero!")
    else:
        st.success("¡Temporada finalizada!")

elif menu == "🏅 VOTAR MVP":
    st.header("🏅 VOTACIÓN MVP DEL PARTIDO")
    if st.session_state.db["fecha_actual"] > 1:
        ultimo_rival = st.session_state.db["historial"][-1]["rival"] if st.session_state.db["historial"] else "último partido"
        st.subheader(f"¿Quién fue el mejor contra {ultimo_rival}?")
        jugadores_campo = [f"{n}-{d[0]}" for n, d in plantel_dict.items() if n != "1"]
        with st.form("mvp_form"):
            nombre_votante = st.text_input("Tu nombre")
            voto = st.selectbox("Votá al MVP", jugadores_campo)
            if st.form_submit_button("🏅 VOTAR") and nombre_votante:
                votos = cargar_votos_mvp()
                votos_filtrados = [v for v in votos if v.get('Nombre','') != nombre_votante]
                data_votos = [[v['Nombre'],v['Voto'],v['Fecha']] for v in votos_filtrados]
                data_votos.append([nombre_votante, voto.split("-")[1], datetime.now().strftime("%Y-%m-%d %H:%M")])
                guardar_votos_mvp(data_votos)
                st.success(f"¡Voto de {nombre_votante} registrado!")
        st.divider()
        st.subheader("📊 Resultados parciales")
        votos = cargar_votos_mvp()
        if votos:
            conteo = {}
            for v in votos:
                j = v['Voto'] if isinstance(v, dict) else v[1]
                conteo[j] = conteo.get(j, 0) + 1
            for j, c in sorted(conteo.items(), key=lambda x: x[1], reverse=True):
                pct = int(c / len(votos) * 100)
                st.markdown(f"**{j}** — {c} voto{'s' if c>1 else ''} ({pct}%)")
                st.progress(pct / 100)
        else:
            st.info("Sin votos todavía.")
    else:
        st.info("Todavía no se jugó ningún partido.")

elif menu == "📝 CARGAR FECHA":
    st.header("📝 REGISTRO DE DATOS (SOLO ADMIN)")
    password = st.text_input("Introduzca la clave para editar:", type="password")
    if password == st.secrets["auth"]["admin_password"]:
        st.success("✅ Acceso concedido, Capitán.")
        t1, t2 = st.tabs(["🔴 REGATAS", "🔵 LIGA"])
        with t1:
            f_idx = st.session_state.db["fecha_actual"] - 1
            if f_idx < len(Liga().fixture_completo):
                rival, local = Liga().fixture_completo[f_idx]
                st.subheader(f"Fecha {st.session_state.db['fecha_actual']}: {'Regatas' if local else rival} vs {rival if local else 'Regatas'}")
                c1, c2 = st.columns(2)
                g_reg = c1.number_input("Goles Regatas", 0, key="reg_g")
                g_riv = c2.number_input(f"Goles {rival}", 0, key="riv_g")
                quienes = st.multiselect("¿Quiénes jugaron?", jugadores_lista)
                g_dict = {}; a_dict = {}
                if g_reg > 0:
                    st.write("--- DETALLE DE GOLES ---")
                    for i in range(g_reg):
                        colg, cola = st.columns(2)
                        g = colg.selectbox(f"Autor Gol {i+1}", jugadores_lista, key=f"g_{i}")
                        a = cola.selectbox(f"Asistidor Gol {i+1}", ["Ninguno"] + jugadores_lista, key=f"a_{i}")
                        g_dict[g] = g_dict.get(g, 0) + 1
                        if a != "Ninguno": a_dict[a] = a_dict.get(a, 0) + 1
                st.write("--- EXTRAS DEL PARTIDO ---")
                mvp = st.selectbox("MVP del Partido", jugadores_lista)
                ama = st.multiselect("Tarjetas Amarillas", jugadores_lista)
                roj = st.multiselect("Tarjetas Rojas", jugadores_lista)
                if st.button("GUARDAR FECHA REGATAS"):
                    procesar_tabla("Regatas Celeste", g_reg, rival, g_riv)
                    if "historial" not in st.session_state.db: st.session_state.db["historial"] = []
                    st.session_state.db["historial"].append({"rival": rival, "g_reg": g_reg, "g_riv": g_riv})
                    for p in quienes: plantel_dict[p.split("-")[0]][1] += 1
                    for p, c in g_dict.items(): plantel_dict[p.split("-")[0]][2] += c
                    for p, c in a_dict.items(): plantel_dict[p.split("-")[0]][3] += c
                    for p in ama: plantel_dict[p.split("-")[0]][4] += 1
                    for p in roj: plantel_dict[p.split("-")[0]][5] += 1
                    plantel_dict[mvp.split("-")[0]][6] += 1
                    if g_riv == 0 and "1" in [px.split("-")[0] for px in quienes]:
                        if len(plantel_dict["1"]) < 8: plantel_dict["1"].append(0)
                        plantel_dict["1"][7] += 1
                    st.session_state.db["fecha_actual"] += 1
                    guardar_datos(st.session_state.db)
                    st.success("¡Datos guardados!")
                    st.rerun()
            else:
                st.info("No hay más fechas en el fixture.")
        with t2:
            st.subheader("Otros resultados de la fecha")
            c3, c4 = st.columns(2)
            eq_l = c3.selectbox("Local", Liga().equipos, key="loc_l")
            eq_v = c4.selectbox("Visitante", [e for e in Liga().equipos if e != eq_l], key="vis_l")
            gl_l = c3.number_input("Goles Local", 0, key="gl_l")
            gv_l = c4.number_input("Goles Visitante", 0, key="gv_l")
            if st.button("GUARDAR RESULTADO LIGA"):
                procesar_tabla(eq_l, gl_l, eq_v, gv_l)
                guardar_datos(st.session_state.db)
                st.success("Tabla actualizada")
                st.rerun()
    elif password == "":
        st.info("Escribí la contraseña para habilitar la carga de datos.")
    else:
        st.error("❌ Clave incorrecta. Solo lectura habilitada.")

elif menu == "📅 FIXTURE":
    st.header("📅 CALENDARIO")
    fix = Liga().fixture_completo
    fecha_actual = st.session_state.db["fecha_actual"]
    c1, c2 = st.columns(2)
    with c1:
        for i in range(11):
            r, l = fix[i]
            icono = "✅ " if i+1 < fecha_actual else ("🔜 " if i+1 == fecha_actual else "")
            st.write(f"{icono}**F{i+1}:** {'Regatas vs ' + r if l else r + ' vs Regatas'}")
    with c2:
        for i in range(11, 22):
            r, l = fix[i]
            icono = "✅ " if i+1 < fecha_actual else ("🔜 " if i+1 == fecha_actual else "")
            st.write(f"{icono}**F{i+1}:** {'Regatas vs ' + r if l else r + ' vs Regatas'}")

