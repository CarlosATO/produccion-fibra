
import streamlit as st
import sqlite3
import hashlib

# Conexión
def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

# Encriptar contraseña
def encriptar_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

# Mostrar usuarios
def mostrar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, rol FROM usuarios")
    datos = cursor.fetchall()
    conn.close()
    return datos

# Agregar usuario
def agregar_usuario(usuario, contrasena, rol):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                       (usuario, encriptar_contrasena(contrasena), rol))
        conn.commit()
        st.success("✅ Usuario agregado correctamente.")
    except sqlite3.IntegrityError:
        st.error("❌ El usuario ya existe.")
    conn.close()

# Actualizar usuario
def actualizar_usuario(id_usuario, nuevo_usuario, nueva_contrasena, nuevo_rol):
    conn = conectar()
    cursor = conn.cursor()
    if nueva_contrasena:
        cursor.execute("UPDATE usuarios SET usuario = ?, contrasena = ?, rol = ? WHERE id = ?",
                       (nuevo_usuario, encriptar_contrasena(nueva_contrasena), nuevo_rol, id_usuario))
    else:
        cursor.execute("UPDATE usuarios SET usuario = ?, rol = ? WHERE id = ?",
                       (nuevo_usuario, nuevo_rol, id_usuario))
    conn.commit()
    conn.close()
    st.success("✅ Usuario actualizado.")

# Eliminar usuario
def eliminar_usuario(id_usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
    conn.commit()
    conn.close()
    st.success("🗑️ Usuario eliminado.")

# Interfaz principal
def app():
    st.subheader("🔐 Mantenimiento de Usuarios")

    with st.expander("➕ Agregar nuevo usuario"):
        nuevo_usuario = st.text_input("Usuario")
        nueva_contrasena = st.text_input("Contraseña", type="password")
        nuevo_rol = st.selectbox("Rol", ["admin", "editor", "visualizador"])
        if st.button("Agregar usuario"):
            if nuevo_usuario and nueva_contrasena:
                agregar_usuario(nuevo_usuario, nueva_contrasena, nuevo_rol)
            else:
                st.warning("⚠️ Debes completar usuario y contraseña.")

    st.markdown("---")
    st.subheader("👥 Usuarios registrados")

    usuarios = mostrar_usuarios()
    for usuario in usuarios:
        with st.expander(f"🔧 {usuario[1]}"):
            nuevo_usuario = st.text_input("Usuario", value=usuario[1], key=f"usuario_{usuario[0]}")
            nueva_contrasena = st.text_input("Nueva contraseña (opcional)", type="password", key=f"pass_{usuario[0]}")
            nuevo_rol = st.selectbox("Rol", ["admin", "editor", "visualizador"], index=["admin", "editor", "visualizador"].index(usuario[2]), key=f"rol_{usuario[0]}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"actualizar_{usuario[0]}"):
                    actualizar_usuario(usuario[0], nuevo_usuario, nueva_contrasena, nuevo_rol)
            with col2:
                if st.button("Eliminar", key=f"eliminar_{usuario[0]}"):
                    eliminar_usuario(usuario[0])
