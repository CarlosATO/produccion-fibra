
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "productividad_fibra.db"

def crear_conexion():
    return sqlite3.connect(DB_PATH)

def inicializar_tabla():
    conn = crear_conexion()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS personal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        rut TEXT,
        cargo TEXT,
        empresa TEXT
    )
    """)
    conn.commit()
    conn.close()

def agregar_personal(nombre, rut, cargo, empresa):
    conn = crear_conexion()
    conn.execute("INSERT INTO personal (nombre, rut, cargo, empresa) VALUES (?, ?, ?, ?)",
                 (nombre, rut, cargo, empresa))
    conn.commit()
    conn.close()

def obtener_personal():
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT * FROM personal", conn)
    conn.close()
    return df

st.title("👷 Mantenimiento de Personal")
inicializar_tabla()

with st.form("form_personal"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        rut = st.text_input("RUT")
    with col2:
        cargo = st.text_input("Cargo")
        empresa = st.text_input("Empresa")

    if st.form_submit_button("Agregar"):
        agregar_personal(nombre, rut, cargo, empresa)
        st.success("✅ Personal agregado correctamente.")
        st.rerun()

st.subheader("📋 Personal registrado")
df = obtener_personal()
st.dataframe(df, use_container_width=True)
