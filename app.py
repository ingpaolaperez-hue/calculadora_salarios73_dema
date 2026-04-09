import streamlit as st
import pandas as pd
from datetime import datetime

# Estilo personalizado para DEMA
st.set_page_config(page_title="DEMA - Arquitectura Financiera", page_icon="🛡️")

# ESTA ES LA LÍNEA QUE CORREGIMOS:
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #1a5276; color: white; border: none; height: 3em; }
    .result-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 5px solid #1a5276; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Arquitectura Financiera DEMA")
st.subheader("Calculadora de Salario Diario Promedio")

# Inicializar historial en la sesión
if 'historial' not in st.session_state:
    st.session_state.historial = []

with st.expander("➕ Agregar Nuevo Empleo", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        f_ini = st.date_input("Fecha de Inicio", key="ini")
    with col2:
        f_fin = st.date_input("Fecha de Fin", key="fin")
    sueldo = st.number_input("Sueldo Diario ($)", min_value=0.0, step=1.0, key="sueldo")
    
    if st.button("Registrar Periodo"):
        st.session_state.historial.append({'inicio': f_ini, 'fin': f_fin, 'sueldo': sueldo})
        st.rerun()

# Cálculos
if st.session_state.historial:
    total_semanas = 0
    suma_ponderada = 0
    limite = 250
    tabla_visual = []

    # Ordenar por fecha (más reciente primero)
    sorted_historial = sorted(st.session_state.historial, key=lambda x: x['inicio'], reverse=True)

    for h in sorted_historial:
        if total_semanas >= limite: break
        
        dias = (h['fin'] - h['inicio']).days + 1
        semanas_p = dias / 7
        
        if total_semanas + semanas_p > limite:
            semanas_uso = limite - total_semanas
            total_semanas = limite
        else:
            semanas_uso = semanas_p
            total_semanas += semanas_p
            
        suma_ponderada += semanas_uso * h['sueldo']
        tabla_visual.append([h['inicio'].strftime('%d/%m/%Y'), h['fin'].strftime('%d/%m/%Y'), f"${h['sueldo']:,.2f}", round(semanas_uso, 2)])

    promedio = suma_ponderada / 250 if total_semanas >= 0 else 0

    # Mostrar resultados elegantes
    st.markdown(f"""
    <div class="result-card">
        <p style="margin-bottom: 5px; color: gray;">Salario Diario Promedio (Ley 73)</p>
        <h1 style="color: #1a5276; margin-top: 0;">${promedio:,.2f} MXN</h1>
        <p>Semanas contabilizadas: <b>{total_semanas:.2f} / 250</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("### Detalle de Periodos")
    df = pd.DataFrame(tabla_visual, columns=["Inicio", "Fin", "Sueldo", "Semanas"])
    st.table(df)

    if st.button("🗑️ Borrar todo e iniciar nuevo cálculo"):
        st.session_state.historial = []
        st.rerun()
else:
    st.info("Aún no hay datos. Agrega el primer periodo arriba para comenzar.")
