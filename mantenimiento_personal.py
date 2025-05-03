import streamlit as st
import sqlite3
import re

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

def agregar_personal(nombre, rut, cargo, empresa):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO personal (nombre, rut, cargo, empresa)
        VALUES (?, ?, ?, ?)
    """, (nombre, rut, cargo, empresa))
    conn.commit()
    conn.close()
    st.success("✅ Personal registrado.")

def actualizar_personal(id_pers, nombre, rut, cargo, empresa):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE personal
        SET nombre = ?, rut = ?, cargo = ?, empresa = ?
        WHERE id = ?
    """, (nombre, rut, cargo, empresa, id_pers))
    conn.commit()
    conn.close()
    st.success("✏️ Personal actualizado.")

def eliminar_personal(id_pers):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personal WHERE id = ?", (id_pers,))
    conn.commit()
    conn.close()
    st.success("🗑️ Personal eliminado.")

def es_rut_valido(rut):
    return bool(re.match(r"^\d{7,8}-[\dkK]$", rut.strip()))

def app():
    st.subheader("👷 Mantenimiento de Personal")
    crear_tabla_personal()

    with st.expander("➕ Agregar nuevo trabajador"):
        nombre = st.text_input("Nombre")
        rut = st.text_input("RUT (ej: 12345678-9)")
        cargo = st.text_input("Cargo")
        empresa = st.text_input("Empresa")

        if st.button("Registrar"):
            if not nombre or not rut:
                st.warning("⚠️ Nombre y RUT son obligatorios.")
            elif not es_rut_valido(rut):
                st.error("❌ El RUT debe tener el formato correcto, por ejemplo: 12345678-9")
            else:
                agregar_personal(nombre, rut.upper().strip(), cargo, empresa)

    st.markdown("---")
    st.subheader("📋 Personal registrado")

    datos = obtener_personal()
    for pers in datos:
        with st.expander(f"🔧 {pers[1]} - {pers[2]}"):
            nombre = st.text_input("Nombre", value=pers[1], key=f"nom_{pers[0]}")
            rut = st.text_input("RUT", value=pers[2], key=f"rut_{pers[0]}")
            cargo = st.text_input("Cargo", value=pers[3], key=f"car_{pers[0]}")
            empresa = st.text_input("Empresa", value=pers[4], key=f"emp_{pers[0]}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{pers[0]}"):
                    if not es_rut_valido(rut):
                        st.error("❌ Formato de RUT incorrecto. No se puede actualizar.")
                    else:
                        actualizar_personal(pers[0], nombre, rut.upper().strip(), cargo, empresa)
            with col2:
                if st.button("Eliminar", key=f"del_{pers[0]}"):
                    eliminar_personal(pers[0])
