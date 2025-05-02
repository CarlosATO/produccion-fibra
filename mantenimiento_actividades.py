
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "productividad_fibra.db"

def crear_conexion():
    return sqlite3.connect(DB_PATH)

def inicializar_tabla():
    conn = crear_conexion()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS actividades (
        codigo TEXT PRIMARY KEY,
        grupo TEXT,
        descripcion TEXT,
        unidad TEXT,
        tipo TEXT,
        valor REAL
    )
    """)
    conn.commit()
    conn.close()

def agregar_actividad(codigo, grupo, descripcion, unidad, tipo, valor):
    conn = crear_conexion()
    conn.execute("INSERT INTO actividades (codigo, grupo, descripcion, unidad, tipo, valor) VALUES (?, ?, ?, ?, ?, ?)",
                 (codigo, grupo, descripcion, unidad, tipo, valor))
    conn.commit()
    conn.close()

def obtener_actividades():
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT * FROM actividades", conn)
    conn.close()
    return df

st.title("➕ Agregar nueva actividad")
inicializar_tabla()

with st.form("form_actividad"):
    col1, col2 = st.columns(2)
    with col1:
        codigo = st.text_input("Código")
        grupo = st.text_input("Grupo")
        descripcion = st.text_input("Descripción")
    with col2:
        unidad = st.selectbox("Unidad", ["metro lineal", "c/u"])
        tipo = st.selectbox("Tipo", ["Programada", "Extra"])
        valor = st.number_input("Precio unitario", min_value=0.0, step=100.0)

    if st.form_submit_button("Guardar"):
        agregar_actividad(codigo, grupo, descripcion, unidad, tipo, valor)
        st.success("✅ Actividad agregada exitosamente.")
        st.rerun()

st.subheader("📋 Actividades registradas")
df = obtener_actividades()
st.dataframe(df, use_container_width=True)
