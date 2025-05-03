
import streamlit as st
import sqlite3

def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

def crear_tabla_personal():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
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

def obtener_personal():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personal")
    datos = cursor.fetchall()
    conn.close()
    return datos

def agregar_persona(nombre, rut, cargo, empresa):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO personal (nombre, rut, cargo, empresa)
        VALUES (?, ?, ?, ?)
    """, (nombre, rut, cargo, empresa))
    conn.commit()
    conn.close()
    st.success("✅ Personal registrado correctamente.")

def actualizar_persona(idp, nombre, rut, cargo, empresa):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE personal
        SET nombre = ?, rut = ?, cargo = ?, empresa = ?
        WHERE id = ?
    """, (nombre, rut, cargo, empresa, idp))
    conn.commit()
    conn.close()
    st.success("✏️ Datos actualizados.")

def eliminar_persona(idp):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personal WHERE id = ?", (idp,))
    conn.commit()
    conn.close()
    st.success("🗑️ Registro eliminado.")

def app():
    st.subheader("👷 Mantenimiento de Personal")
    crear_tabla_personal()

    with st.expander("➕ Agregar nuevo personal"):
        nombre = st.text_input("Nombre completo")
        rut = st.text_input("RUT")
        cargo = st.text_input("Cargo")
        empresa = st.text_input("Empresa")
        if st.button("Registrar"):
            if nombre and rut:
                agregar_persona(nombre, rut, cargo, empresa)
            else:
                st.warning("⚠️ Ingresa al menos nombre y RUT.")

    st.markdown("---")
    st.subheader("📋 Personal registrado")

    datos = obtener_personal()
    for persona in datos:
        with st.expander(f"🧾 {persona[1]}"):
            nombre = st.text_input("Nombre", value=persona[1], key=f"n_{persona[0]}")
            rut = st.text_input("RUT", value=persona[2], key=f"r_{persona[0]}")
            cargo = st.text_input("Cargo", value=persona[3], key=f"c_{persona[0]}")
            empresa = st.text_input("Empresa", value=persona[4], key=f"e_{persona[0]}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{persona[0]}"):
                    actualizar_persona(persona[0], nombre, rut, cargo, empresa)
            with col2:
                if st.button("Eliminar", key=f"del_{persona[0]}"):
                    eliminar_persona(persona[0])
