import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración y Estilo Profesional DEMA
st.set_page_config(page_title="DEMA - Simulador de Pensión", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    div.stButton > button:first-child { background-color: #1a5276; color: white; border-radius: 25px; height: 3em; font-weight: bold; }
    .footer { text-align: center; color: gray; font-size: 0.8em; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- TABLA ART 167 ---
def obtener_porcentajes(factor_uma):
    if factor_uma <= 1.0: return 80.00, 0.563
    elif factor_uma <= 1.25: return 80.00, 0.563
    elif factor_uma <= 1.50: return 77.11, 0.814
    elif factor_uma <= 1.75: return 58.18, 1.178
    elif factor_uma <= 2.00: return 49.23, 1.430
    elif factor_uma <= 2.25: return 42.67, 1.615
    elif factor_uma <= 2.50: return 37.65, 1.756
    elif factor_uma <= 2.75: return 33.68, 1.868
    elif factor_uma <= 3.00: return 30.48, 1.963
    elif factor_uma <= 3.25: return 27.83, 2.038
    elif factor_uma <= 3.50: return 25.60, 2.100
    elif factor_uma <= 3.75: return 23.70, 2.148
    elif factor_uma <= 4.00: return 22.07, 2.201
    elif factor_uma <= 4.25: return 20.65, 2.238
    elif factor_uma <= 4.50: return 19.39, 2.275
    elif factor_uma <= 4.75: return 18.29, 2.302
    elif factor_uma <= 5.00: return 17.30, 2.332
    elif factor_uma <= 5.25: return 16.41, 2.355
    elif factor_uma <= 5.50: return 15.61, 2.375
    elif factor_uma <= 5.75: return 14.88, 2.398
    elif factor_uma <= 6.00: return 14.22, 2.415
    else: return 13.00, 2.450

# --- INTERFAZ ---
st.title("🛡️ Arquitectura Financiera DEMA")
st.subheader("Simulador Integral de Pensión Ley 73")

tab1, tab2 = st.tabs(["📋 1. Salario Diario Promedio", "💰 2. Proyección de Pensión"])

with tab1:
    if 'historial' not in st.session_state: st.session_state.historial = []
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.write("#### Registro de Historial")
        f_ini = st.date_input("Fecha Inicio", key="f_ini")
        f_fin = st.date_input("Fecha Fin", key="f_fin")
        sueldo = st.number_input("Sueldo Diario ($)", min_value=0.0, step=10.0, format="%.2f")
        if st.button("➕ Registrar Periodo"):
            st.session_state.historial.append({'inicio': f_ini, 'fin': f_fin, 'sueldo': sueldo})
            st.rerun()
        if st.button("🗑️ Limpiar Datos"):
            st.session_state.historial = []
            st.rerun()

    promedio_final = 0.0
    if st.session_state.historial:
        total_s, suma_p, datos_t = 0, 0, []
        for h in sorted(st.session_state.historial, key=lambda x: x['inicio'], reverse=True):
            if total_s >= 250: break
            dias = (h['fin'] - h['inicio']).days + 1
            sem = dias / 7
            sem_uso = 250 - total_s if total_s + sem > 250 else sem
            total_s += sem_uso
            suma_p += sem_uso * h['sueldo']
            datos_t.append([h['inicio'].strftime('%d/%m/%Y'), h['fin'].strftime('%d/%m/%Y'), f"${h['sueldo']:,.2f}", round(sem_uso, 2)])
        
        promedio_final = suma_p / 250
        with col_b:
            st.metric("SALARIO DIARIO PROMEDIO", f"${promedio_final:,.2f}")
            st.table(pd.DataFrame(datos_t, columns=["Inicio", "Fin", "Sueldo", "Semanas"]))

with tab2:
    if promedio_final <= 0:
        st.warning("⚠️ Primero ingresa los datos en la pestaña de Salario Diario Promedio.")
    else:
        st.write("#### Parámetros de Jubilación")
        c1, c2, c3 = st.columns(3)
        with c1:
            uma = st.number_input("Valor UMA vigente", value=117.31)
            semanas_t = st.number_input("Total de Semanas Cotizadas", min_value=500, value=1500, step=1)
        with c2:
            edad = st.selectbox("Edad al pensionarse", [60, 61, 62, 63, 64, 65], index=0)
            pct_edad = {60: 0.75, 61: 0.80, 62: 0.85, 63: 0.90, 64: 0.95, 65: 1.0}
        with c3:
            st.write("Asignaciones Familiares")
            esposa = st.checkbox("Esposa / Viuda (15%)")
            hijos = st.number_input("Hijos Estudiando (10% c/u)", 0, 5, 0)
            padres = st.number_input("Padres Dependientes (10% c/u)", 0, 2, 0)
            soledad = st.checkbox("Ayuda por Soledad (15%)") if not esposa and hijos==0 and padres==0 else False

        # --- LÓGICA MATEMÁTICA DEMA ---
        factor_u = promedio_final / uma
        pct_cb, pct_ia = obtener_porcentajes(factor_u)
        
        cb_anual = (promedio_final * (pct_cb/100) * 365)
        anios_exc = (semanas_t - 500) / 52
        ia_anual = (promedio_final * (pct_ia/100) * 365) * anios_exc
        cuantia_pension_anual = cb_anual + ia_anual
        
        # Ayudas
        ayuda_esposa = cuantia_pension_anual * 0.15 if esposa else 0
        ayuda_hijos = (cuantia_pension_anual * 0.10) * hijos
        ayuda_padres = (cuantia_pension_anual * 0.10) * padres
        ayuda_soledad = cuantia_pension_anual * 0.15 if soledad else 0
        total_ayudas = ayuda_esposa + ayuda_hijos + ayuda_padres + ayuda_soledad
        
        # Suma + Fox + Edad
        subtotal = cuantia_pension_anual + total_ayudas
        total_fox = subtotal * 1.11
        pension_anual_final = total_fox * pct_edad[edad]
        pension_mensual = pension_anual_final / 12

        st.divider()
        st.write("### 📜 Resultados de la Proyección")
        r1, r2, r3 = st.columns(3)
        r1.metric("Cuantía Anual Base", f"${cuantia_pension_anual:,.2f}")
        r2.metric("Total Ayudas Anuales", f"${total_ayudas:,.2f}")
        r3.metric("Pensión Mensual Final", f"${pension_mensual:,.2f}", delta=f"{int(pct_edad[edad]*100)}% por Edad")

        with st.expander("Ver Desglose Técnico"):
            st.write(f"**Factor UMA:** {factor_u:.2f}")
            st.write(f"**Años Reconocidos Posteriores a 500 sem:** {anios_exc:.2f}")
            st.write(f"**Subtotal con Factor Fox (1.11):** ${total_fox:,.2f}")

st.markdown('<div class="footer">DEMA - Mayordomía Financiera Bíblica & Arquitectura Financiera</div>', unsafe_allow_html=True)
