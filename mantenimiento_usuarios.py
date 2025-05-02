
import streamlit as st
import sqlite3
import pandas as pd
import hashlib

DB_PATH = "productividad_fibra.db"

def crear_conexion():
    return sqlite3.connect(DB_PATH)

def inicializar_tabla_usuarios():
    conn = crear_conexion()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        contrasena TEXT,
        rol TEXT
    )
    """)
    conn.commit()
    conn.close()

def encriptar_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

def agregar_usuario(usuario, contrasena, rol):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                   (usuario, encriptar_contrasena(contrasena), rol))
    conn.commit()
    conn.close()

def obtener_usuarios():
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT usuario, rol FROM usuarios", conn)
    conn.close()
    return df

st.title("💜 Mantenimiento de Usuarios")
inicializar_tabla_usuarios()

with st.form("form_usuario"):
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
    with col2:
        rol = st.selectbox("Rol", ["Administrador", "Usuario"])

    if st.form_submit_button("Agregar usuario"):
        if usuario and contrasena:
            try:
                agregar_usuario(usuario, contrasena, rol)
                st.success("✅ Usuario agregado correctamente.")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("⚠️ El usuario ya existe.")
        else:
            st.warning("Por favor completa todos los campos.")

st.subheader("📋 Usuarios registrados")
df = obtener_usuarios()
st.dataframe(df, use_container_width=True)
