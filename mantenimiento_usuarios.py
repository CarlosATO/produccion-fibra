
import streamlit as st
import sqlite3
import pandas as pd
import hashlib

DB_PATH = "productividad_fibra.db"

def crear_conexion():
    return sqlite3.connect(DB_PATH)

def inicializar_usuarios():
    conn = crear_conexion()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        usuario TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def agregar_usuario(nombre, usuario, password, rol):
    conn = crear_conexion()
    conn.execute("INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (?, ?, ?, ?)",
                 (nombre, usuario, hash_password(password), rol))
    conn.commit()
    conn.close()

def actualizar_usuario(id_, nombre, usuario, password, rol):
    conn = crear_conexion()
    if password:
        conn.execute("UPDATE usuarios SET nombre=?, usuario=?, password=?, rol=? WHERE id=?",
                     (nombre, usuario, hash_password(password), rol, id_))
    else:
        conn.execute("UPDATE usuarios SET nombre=?, usuario=?, rol=? WHERE id=?",
                     (nombre, usuario, rol, id_))
    conn.commit()
    conn.close()

def eliminar_usuario(id_):
    conn = crear_conexion()
    conn.execute("DELETE FROM usuarios WHERE id=?", (id_,))
    conn.commit()
    conn.close()

def obtener_usuarios():
    conn = crear_conexion()
    df = pd.read_sql_query("SELECT id, nombre, usuario, rol FROM usuarios", conn)
    conn.close()
    return df

# Validar sesión
if "usuario" not in st.session_state:
    st.warning("🔒 Debes iniciar sesión como administrador.")
    st.stop()

if st.session_state.get("rol") != "admin":
    st.error("⛔ No tienes permisos para acceder a esta sección.")
    st.stop()

# UI
st.title("👥 Mantenimiento de Usuarios")
inicializar_usuarios()

df_usuarios = obtener_usuarios()
st.subheader("📋 Usuarios registrados")
st.dataframe(df_usuarios, use_container_width=True)

st.subheader("➕ Agregar nuevo usuario")
with st.form("form_agregar"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre completo")
        usuario = st.text_input("Usuario")
    with col2:
        password = st.text_input("Contraseña", type="password")
        rol = st.selectbox("Rol", ["admin", "lector", "editor"])

    if st.form_submit_button("Agregar"):
        agregar_usuario(nombre, usuario, password, rol)
        st.success("✅ Usuario agregado correctamente.")
        st.experimental_rerun()

# Editar usuario
st.subheader("✏️ Editar usuario existente")
ids = df_usuarios["id"].tolist()
if ids:
    id_editar = st.selectbox("Seleccionar ID", ids)
    user = df_usuarios[df_usuarios["id"] == id_editar].iloc[0]

    with st.form("form_editar"):
        col1, col2 = st.columns(2)
        with col1:
            new_nombre = st.text_input("Nombre", value=user["nombre"])
            new_usuario = st.text_input("Usuario", value=user["usuario"])
        with col2:
            new_password = st.text_input("Nueva contraseña (dejar en blanco si no cambia)", type="password")
            new_rol = st.selectbox("Rol", ["admin", "lector", "editor"], index=["admin", "lector", "editor"].index(user["rol"]))

        if st.form_submit_button("Actualizar"):
            actualizar_usuario(id_editar, new_nombre, new_usuario, new_password, new_rol)
            st.success("✅ Usuario actualizado.")
            st.experimental_rerun()

# Eliminar usuario
st.subheader("❌ Eliminar usuario")
id_eliminar = st.selectbox("Seleccionar ID a eliminar", ids, key="delete_user")
if st.button("Eliminar usuario"):
    eliminar_usuario(id_eliminar)
    st.warning(f"⚠️ Usuario con ID {id_eliminar} eliminado.")
    st.experimental_rerun()
