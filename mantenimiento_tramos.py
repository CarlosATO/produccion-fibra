
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "productividad_fibra.db"

def crear_conexion():
    return sqlite3.connect(DB_PATH)

def inicializar_tabla():
    conn = crear_conexion()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS tramos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        triot TEXT,
        tramo TEXT,
        inicio TEXT,
        fin TEXT,
        mufa_inicio TEXT,
        mufa_fin TEXT
    )
    """)
    conn.commit()
    conn.close()

def agregar_tramo(triot, tramo, inicio, fin, mufa_inicio, mufa_fin):
    conn = crear_conexion()
    conn.execute("INSERT INTO tramos (triot, tramo, inicio, fin, mufa_inicio, mufa_fin) VALUES (?, ?, ?, ?, ?, ?)",
                 (triot, tramo, inicio, fin, mufa_inicio, mufa_fin))
    conn.commit()
    conn.close()

def obtener_tramos():
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT * FROM tramos", conn)
    conn.close()
    return df

st.title("📍 Mantenimiento de Tramos")
inicializar_tabla()

with st.form("form_tramo"):
    col1, col2 = st.columns(2)
    with col1:
        triot = st.text_input("Triot")
        tramo = st.text_input("Tramo")
        inicio = st.text_input("Inicio")
    with col2:
        fin = st.text_input("Fin")
        mufa_inicio = st.text_input("Mufa Inicio")
        mufa_fin = st.text_input("Mufa Fin")

    if st.form_submit_button("Agregar Tramo"):
        agregar_tramo(triot, tramo, inicio, fin, mufa_inicio, mufa_fin)
        st.success("✅ Tramo agregado correctamente.")
        st.rerun()

st.subheader("📋 Tramos registrados")
df = obtener_tramos()
st.dataframe(df, use_container_width=True)
