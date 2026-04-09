import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURACIÓN DEMA ---
st.set_page_config(page_title="DEMA - Simulador de Pension", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    div.stButton > button:first-child { background-color: #1a5276; color: white; border-radius: 25px; font-weight: bold; }
    .ganantizada-box { background-color: #fff4e5; border-left: 5px solid #ffa000; padding: 15px; border-radius: 5px; color: #856404; }
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

# --- GENERADOR DE PDF CORREGIDO (Soporta caracteres latinos) ---
def generar_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    # Usamos 'latin-1' para que acepte la ñ y acentos correctamente
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Arquitectura Financiera DEMA".encode('latin-1','replace').decode('latin-1'), ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, "Reporte de Proyección de Pensión Ley 73".encode('latin-1','replace').decode('latin-1'), ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_fill_color(26, 82, 118)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(190, 10, " RESUMEN DE CÁLCULO".encode('latin-1','replace').decode('latin-1'), ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    
    for clave, valor in datos.items():
        pdf.cell(95, 10, f"{clave}:".encode('latin-1','replace').decode('latin-1'), border=1)
        pdf.cell(95, 10, f"{valor}".encode('latin-1','replace').decode('latin-1'), border=1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    msg = "Este documento es una proyección informativa basada en los datos proporcionados. No sustituye la resolución oficial del IMSS."
    pdf.multi_cell(0, 5, msg.encode('latin-1','replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

st.title("🛡️ Arquitectura Financiera DEMA")
tab1, tab2 = st.tabs(["📋 1. Salario Diario Promedio", "💰 2. Proyección de Pensión"])

# --- PESTAÑA 1 (Sin cambios) ---
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

# --- PESTAÑA 2 (Actualizada 2026 y Mínima) ---
with tab2:
    if promedio_final <= 0:
        st.warning("⚠️ Primero calcula el promedio en la pestaña 1.")
    else:
        st.write("#### Parámetros de Jubilación (Ciclo 2026)")
        nombre_c = st.text_input("Nombre del Cliente", "Prospecto DEMA")
        c1, c2, c3 = st.columns(3)
        with c1:
            uma = st.number_input("Valor UMA 2026", value=117.31)
            semanas_t = st.number_input("Total Semanas Cotizadas", min_value=500, value=1500)
            s_minimo = st.number_input("Salario Mínimo Actual", value=315.04)
        with c2:
            edad = st.selectbox("Edad al pensionarse", [60, 61, 62, 63, 64, 65])
            pct_edad = {60: 0.75, 61: 0.80, 62: 0.85, 63: 0.90, 64: 0.95, 65: 1.0}
        with c3:
            st.write("Asignaciones Familiares")
            esposa = st.checkbox("Esposa / Viuda (15%)")
            hijos = st.number_input("Hijos Estudiando (10% c/u)", 0, 5)
            padres = st.number_input("Padres Dependientes (10% c/u)", 0, 2)
            soledad = st.checkbox("Ayuda por Soledad (15%)") if not esposa and hijos==0 and padres==0 else False

        # --- LÓGICA DE CÁLCULO DEMA ---
        minima_mensual = ((s_minimo * 365) * 1.11) / 12
        
        factor_uma = promedio_final / uma
        p_cb, p_ia = obtener_porcentajes(factor_uma)
        cb_anual = promedio_final * (p_cb/100) * 365
        ia_anual = (promedio_final * (p_ia/100) * 365) * ((semanas_t - 500) / 52)
        
        suma_base = cb_anual + ia_anual
        ayudas_pct = (0.15 if esposa or soledad else 0) + (0.10 * (hijos + padres))
        total_pre_edad = (suma_base * (1 + ayudas_pct)) * 1.11
        mensual_calc = (total_pre_edad * pct_edad[edad]) / 12

        # Comparación definitiva
        es_minima = False
        if mensual_calc < minima_mensual:
            pension_final = minima_mensual
            es_minima = True
        else:
            pension_final = mensual_calc

        st.divider()
        if es_minima:
            st.markdown(f'<div class="ganantizada-box">📢 <b>Cálculo de Ley:</b> El monto calculado (${mensual_calc:,.2f}) es inferior al mínimo. Por Ley, se asigna la <b>Pensión Mínima Garantizada</b>.</div>', unsafe_allow_html=True)
            st.metric("PENSIÓN FINAL", f"${pension_final:,.2f}", delta="MÍNIMA GARANTIZADA")
        else:
            st.success(f"### Pensión Mensual Estimada: ${pension_final:,.2f}")
            st.metric("PENSIÓN CALCULADA", f"${pension_final:,.2f}")

        # --- REPORTE PDF PERSONALIZADO ---
        datos_pdf = {
            "Cliente": nombre_c,
            "Salario Diario Promedio": f"${promedio_final:,.2f}",
            "Semanas Totales": f"{int(semanas_t)}",
            "Edad de Jubilación": f"{edad} años",
            "Monto Mensual": f"${pension_final:,.2f}",
            "Observaciones": "Pensión Mínima" if es_minima else "Cálculo según Art. 167"
        }
        
        st.download_button("📄 Descargar Reporte PDF DEMA", 
                           data=generar_pdf(datos_pdf), 
                           file_name=f"Proyeccion_DEMA_{nombre_c}.pdf")

st.markdown('<div class="footer">DEMA - Arquitectura Financiera 2026</div>', unsafe_allow_html=True)
