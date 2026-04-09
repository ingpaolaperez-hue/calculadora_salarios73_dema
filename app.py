import streamlit as st
import pandas as pd
from datetime import datetime

# Estilo personalizado para DEMA
st.set_page_config(page_title="DEMA - Arquitectura Financiera", page_icon="🛡️")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #1a5276; color: white; }
    .result-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 5px solid #1a5276; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_scale=True)

st.title("🛡️ Arquitectura Financiera DEMA")
st.subheader("Calculadora de Salario Diario Promedio")

# Inicializar historial en la sesión
if 'historial' not in st.session_state:
    st.session_state.historial = []

with st.expander("➕ Agregar Nuevo Empleo", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        f_ini = st.date_input("Fecha de Inicio")
    with col2:
        f_fin = st.date_input("Fecha de Fin")
    sueldo = st.number_input("Sueldo Diario ($)", min_value=0.0, step=10.0)
    
    if st.button("Registrar Periodo"):
        st.session_state.historial.append({'inicio': f_ini, 'fin': f_fin, 'sueldo': sueldo})
        st.success("Periodo agregado correctamente")

# Cálculos
if st.session_state.historial:
    total_semanas = 0
    suma_ponderada = 0
    limite = 250
    tabla_visual = []

    for h in st.session_state.historial:
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
        tabla_visual.append([h['inicio'], h['fin'], h['sueldo'], round(semanas_uso, 2)])

    promedio = suma_ponderada / 250 if total_semanas > 0 else 0

    # Mostrar resultados elegantes
    st.markdown(f"""
    <div class="result-card">
        <h3>Salario Diario Promedio (Ley 73)</h3>
        <h1 style="color: #1a5276;">${promedio:,.2f} MXN</h1>
        <p>Semanas contabilizadas: <b>{total_semanas:.2f} / 250</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("### Detalle de Periodos")
    df = pd.DataFrame(tabla_visual, columns=["Inicio", "Fin", "Sueldo", "Semanas"])
    st.dataframe(df, use_container_width=True)

    if st.button("🗑️ Borrar todo"):
        st.session_state.historial = []
        st.rerun()
