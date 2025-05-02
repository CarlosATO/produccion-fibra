
import streamlit as st
import pandas as pd
import sqlite3

DB_PATH = "productividad_fibra.db"

def crear_conexion():
    return sqlite3.connect(DB_PATH)

def obtener_personal():
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT DISTINCT nombre FROM personal ORDER BY nombre", conn)
    conn.close()
    return df["nombre"].tolist()

def obtener_actividades():
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT codigo, descripcion FROM actividades ORDER BY descripcion", conn)
    conn.close()
    return df

def obtener_tramos():
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT * FROM tramos ORDER BY triot, tramo", conn)
    conn.close()
    return df

def insertar_produccion(datos):
    conn = crear_conexion()
    conn.execute("""
        INSERT INTO produccion 
        (fecha, actividad, trabajador, cantidad, triot, tramo, inicio, fin, mufa_inicio, mufa_fin, rematado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    conn.close()

st.title("📝 Ingreso de Producción")

actividades = obtener_actividades()
personal = obtener_personal()
tramos = obtener_tramos()

with st.form("form_produccion"):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha")
        actividad = st.selectbox("Actividad", actividades["descripcion"].tolist())
        trabajador = st.selectbox("Trabajador", personal)
        cantidad = st.number_input("Cantidad realizada", min_value=0.0, step=1.0)
    with col2:
        triot = st.selectbox("Triot", sorted(tramos["triot"].unique()))
        tramo = st.selectbox("Tramo", sorted(tramos["tramo"].unique()))
        rematado = st.slider("% Rematado", 0, 100, 0)

    if st.form_submit_button("Guardar Producción"):
        fila = tramos[(tramos["triot"] == triot) & (tramos["tramo"] == tramo)]
        if not fila.empty:
            fila = fila.iloc[0]
            datos = (
                fecha.strftime("%Y-%m-%d"),
                actividad,
                trabajador,
                cantidad,
                triot,
                tramo,
                fila["inicio"],
                fila["fin"],
                fila["mufa_inicio"],
                fila["mufa_fin"],
                rematado
            )
            insertar_produccion(datos)
            st.success("✅ Registro guardado correctamente.")
        else:
            st.error("❌ No se encontró información del tramo seleccionado.")
