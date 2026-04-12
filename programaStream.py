import streamlit as st
import pandas as pd
import json
import os
from streamlit_gsheets import GSheetsConnection

# ==========================================
# --- 1. CONFIGURACIÓN VISUAL (STYLE) ---
# ==========================================
st.set_page_config(page_title="Regatas Manager Pro", layout="wide")

# Diseño Oscuro con detalles Celeste y Rojo
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #002d62 !important; border-right: 3px solid #e63946; }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Cards estilo Dark Pro con detalle Rojo y Celeste */
    .metric-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00aae4; 
        border-right: 5px solid #e63946;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-title { color: #8b949e; font-size: 14px; text-transform: uppercase; font-weight: bold; }
    .metric-value { color: white !important; font-size: 24px; font-weight: bold; }
    
    /* TABLAS OSCURAS PROFESIONALES (CORREGIDAS) */
    .stTable { 
        background-color: #161b22 !important; 
        color: white !important; 
        border-radius: 10px !important; 
        border: 1px solid #30363d !important;
    }
    .stTable thead tr th { 
        background-color: #e63946 !important; 
        color: white !important; 
        font-size: 16px;
    }
    .stTable tbody tr td { 
        color: white !important; 
        border-bottom: 1px solid #30363d !important;
        background-color: #161b22 !important;
    }
    
    /* Botones con estilo */
    .stButton>button { background-color: #00aae4; color: white; border-radius: 8px; font-weight: bold; border: none; transition: 0.3s; width: 100%;}
    .stButton>button:hover { background-color: #e63946 !important; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)

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

def guardar_datos(estado):
    df_tabla = pd.DataFrame(estado["tabla"]).T.reset_index().rename(columns={'index': 'Equipo'})
    df_historial = pd.DataFrame(estado["historial"])
    datos_p = []
    for k, v in estado["plantel"].items():
        datos_p.append([k] + v)
    df_plantel = pd.DataFrame(datos_p, columns=['ID', 'Nombre', 'PJ', 'Goles', 'Asist', 'Amarillas', 'Rojas', 'MVP', 'Vallas'])

    try:
        # Forzamos la limpieza de cache antes de intentar el update
        st.cache_data.clear()
        
        try:
        conn.update(worksheet="Tabla", data=df_tabla)
        st.success("¡Guardó Tabla!")
    except Exception as e:
        st.error(f"GOOGLE DIJO: {e}")

if 'db' not in st.session_state:
    try:
        # Leemos con ttl=0 para evitar que use datos viejos
        df_t = conn.read(worksheet="Tabla", ttl=0)
        df_h = conn.read(worksheet="Historial", ttl=0)
        df_p = conn.read(worksheet="Plantel", ttl=0)
        
        st.session_state.db = {
            "tabla": df_t.set_index('Equipo').to_dict('index'),
            "historial": df_h.to_dict('records'),
            "fecha_actual": len(df_h) + 1,
            "plantel": df_p.set_index('ID').to_dict('list')
        }
    except Exception as e:
        # Si da error 400, cargamos los datos por defecto
        st.session_state.db = {
            "fecha_actual": 1,
            "historial": [],
            "tabla": {eq: {"PTS": 0, "PJ": 0, "PG": 0, "PE": 0, "PP": 0, "GF": 0, "GC": 0} for eq in Liga().equipos},
            "plantel": {
                "1": ["Toro", 0,0,0,0,0,0,0], "2": ["Ochoa", 0,0,0,0,0,0,0], "3": ["Peña", 0,0,0,0,0,0,0],
                "4": ["Caputo", 0,0,0,0,0,0,0], "5": ["Amato", 0,0,0,0,0,0,0], "6": ["Basto", 0,0,0,0,0,0,0],
                "7": ["Tano", 0,0,0,0,0,0,0], "8": ["Ciro", 0,0,0,0,0,0,0], "9": ["Rocca", 0,0,0,0,0,0,0],
                "10": ["Beni", 0,0,0,0,0,0,0], "11": ["Feli", 0,0,0,0,0,0,0], "13": ["Juani Blanco", 0,0,0,0,0,0,0],
                "14": ["Galo", 0,0,0,0,0,0,0], "15": ["Capri", 0,0,0,0,0,0,0], "16": ["Vigna", 0,0,0,0,0,0,0],
                "17": ["Lucio", 0,0,0,0,0,0,0], "18": ["Mateo", 0,0,0,0,0,0,0], "19": ["Zurdo", 0,0,0,0,0,0,0],
                "20": ["Pena", 0,0,0,0,0,0,0], "21": ["Churri", 0,0,0,0,0,0,0], "22": ["Giacovino", 0,0,0,0,0,0,0], 
                "23": ["Manu", 0,0,0,0,0,0,0]
            }
        }
def procesar_tabla(e1, g1, e2, g2):
    t = st.session_state.db["tabla"]
    for e, gf, gc in [(e1, g1, g2), (e2, g2, g1)]:
        t[e]["PJ"] += 1
        t[e]["GF"] += gf
        t[e]["GC"] += gc
        if gf > gc: t[e]["PTS"] += 3; t[e]["PG"] += 1
        elif gf == gc: t[e]["PTS"] += 1; t[e]["PE"] += 1
        else: t[e]["PP"] += 1

def metric_card(title, value):
    st.markdown(f"""<div class="metric-card"><div class="metric-title">{title}</div><div class="metric-value">{value}</div></div>""", unsafe_allow_html=True)

# ==========================================
# --- 3. INTERFAZ ---
# ==========================================
st.sidebar.markdown("<h2 style='text-align:center; color:white;'>🔴 REGATAS 🔵</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("NAVEGACIÓN", ["🏠 INICIO", "🏆 TABLA", "👤 PLANTEL", "🎥 GOLES", "⚠️ TARJETAS", "📝 CARGAR FECHA", "📅 FIXTURE"])

plantel_dict = st.session_state.db["plantel"]
jugadores_lista = [f"{n}-{d[0]}" for n, d in plantel_dict.items()]

if menu == "🏠 INICIO":
    st.header("⚽ BIENVENIDO A LA BASE DE DATOS DE JUVENILES CELESTE")
    # Banner desde carpeta /img
    if os.path.exists("img/banner.png"):
        st.image("img/banner.png", use_container_width=True)
    else:
        st.info("📷 Agregá tu foto en 'img/banner.png' para verla aquí.")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏁 ÚLTIMO PARTIDO")
        hist = st.session_state.db.get("historial", [])
        if hist:
            ult = hist[-1]
            metric_card("RESULTADO FINAL", f"Regatas {ult['g_reg']} - {ult['g_riv']} {ult['rival']}")
        else: st.write("No hay partidos registrados.")
    with c2:
        st.subheader("📅 PRÓXIMO PARTIDO")
        idx = st.session_state.db["fecha_actual"] - 1
        if idx < len(Liga().fixture_completo):
            riv, loc = Liga().fixture_completo[idx]
            metric_card(f"FECHA {idx+1}", f"vs {riv} ({'LOCAL' if loc else 'VISITANTE'})")
        else: st.success("¡TEMPORADA FINALIZADA!")

elif menu == "🏆 TABLA":
    st.header("🏆 TABLA DE POSICIONES")
    df = pd.DataFrame(st.session_state.db["tabla"]).T
    df['DG'] = df['GF'] - df['GC']
    st.table(df.sort_values(by=["PTS", "DG"], ascending=False)[['PTS', 'PJ', 'PG', 'PE', 'PP', 'GF', 'GC', 'DG']])

elif menu == "👤 PLANTEL":
    st.header("📊 ESTADÍSTICAS DEL PLANTEL")
    
    # --- 1. LÓGICA DE LÍDERES (SOPORTA EMPATES) ---
    jugadores_campo = {k: v for k, v in plantel_dict.items() if k != "1"}
    
    # Máximos Goleadores
    max_goles = max(v[2] for v in jugadores_campo.values())
    goleadores = [v[0] for v in jugadores_campo.values() if v[2] == max_goles and max_goles > 0]
    
    # Máximos Asistidores
    max_asist = max(v[3] for v in jugadores_campo.values())
    asistidores = [v[0] for v in jugadores_campo.values() if v[3] == max_asist and max_asist > 0]

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        texto_gol = ", ".join(goleadores) if goleadores else "Sin goles"
        metric_card("⚽ MÁXIMO GOLEADOR", f"{texto_gol} ({max_goles})")
    with col_l2:
        texto_asist = ", ".join(asistidores) if asistidores else "Sin asistencias"
        metric_card("🎯 MÁXIMO ASISTIDOR", f"{texto_asist} ({max_asist})")

    st.divider()

    # --- 2. TABLA GENERAL INTERACTIVA ---
    st.subheader("📋 Ficha General de Jugadores")
    st.write("Clickeá en los encabezados para ordenar la tabla:")
    
    datos_tabla = []
    for nro, d in plantel_dict.items():
        datos_tabla.append({
            "NRO": int(nro),
            "JUGADOR": d[0],
            "PJ": d[1],
            "GOLES": d[2] if nro != "1" else "-", # El arquero no suele llevar goles
            "ASIST": d[3] if nro != "1" else "-",
            "V. INVICTAS": d[7] if nro == "1" else "-",
            "MVP": d[6]
        })
    
    df_plantel = pd.DataFrame(datos_tabla)
    # Mostramos con st.dataframe para que el usuario pueda ordenar haciendo clic
    st.dataframe(df_plantel, use_container_width=True, hide_index=True)

    st.divider()
    
    # --- 3. BÚSQUEDA INDIVIDUAL (Mantenida por si querés ver detalle) ---
    sel = st.selectbox("Detalle individual por jugador:", jugadores_lista)
    nro_sel = sel.split("-")[0]
    s = plantel_dict[nro_sel]
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("PARTIDOS", s[1])
    with c2: 
        if nro_sel == "1": metric_card("V. INVICTAS", s[7])
        else: metric_card("GOLES", s[2])
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
    else: st.info("Todavía no hay partidos jugados.")

elif menu == "⚠️ TARJETAS":
    st.header("⚠️ CONTROL DE DISCIPLINARIOS")
    data_disc = [{"NRO": k, "NOMBRE": v[0], "AMARILLAS": v[4], "ROJAS": v[5]} for k, v in plantel_dict.items()]
    df_disc = pd.DataFrame(data_disc).sort_values(by="AMARILLAS", ascending=False)
    # hide_index=True elimina esa primera columna de números
    st.dataframe(df_disc, use_container_width=True, hide_index=True)

elif menu == "📝 CARGAR FECHA":
    st.header("📝 REGISTRO DE DATOS (SOLO ADMIN)")
    
    # --- SISTEMA DE SEGURIDAD ---
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
                
                # --- AQUÍ ESTABA EL ERROR: RESTAURANDO SELECTORES DE GOLES ---
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
                    
                    # Guardar en historial para el inicio
                    if "historial" not in st.session_state.db: st.session_state.db["historial"] = []
                    st.session_state.db["historial"].append({"rival": rival, "g_reg": g_reg, "g_riv": g_riv})
                    
                    # Sumar estadísticas a jugadores
                    for p in quienes: plantel_dict[p.split("-")[0]][1] += 1
                    for p, c in g_dict.items(): plantel_dict[p.split("-")[0]][2] += c
                    for p, c in a_dict.items(): plantel_dict[p.split("-")[0]][3] += c
                    for p in ama: plantel_dict[p.split("-")[0]][4] += 1
                    for p in roj: plantel_dict[p.split("-")[0]][5] += 1
                    plantel_dict[mvp.split("-")[0]][6] += 1
                    
                    # Valla invicta para el Toro (#1)
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
    c1, c2 = st.columns(2)
    with c1:
        for i in range(11):
            r, l = fix[i]; st.write(f"**F{i+1}:** {'Regatas vs ' + r if l else r + ' vs Regatas'}")
    with c2:
        for i in range(11, 22):
            r, l = fix[i]; st.write(f"**F{i+1}:** {'Regatas vs ' + r if l else r + ' vs Regatas'}")
