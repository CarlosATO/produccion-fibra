import streamlit as st
import sqlite3
import re
import pandas as pd

# --- Conexión a la base de datos ---
def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

# --- Crear tabla empresas si no existe ---
def crear_tabla_empresas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            rut TEXT,
            representante TEXT,
            direccion TEXT,
            correo TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Validar RUT chileno ---
def validar_rut(rut):
    rut = rut.replace(".", "").replace("-", "").upper()

    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        return False

    cuerpo = rut[:-1]
    dv_ingresado = rut[-1]

    suma = 0
    multiplo = 2
    for d in reversed(cuerpo):
        suma += int(d) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1

    resto = suma % 11
    dv_calculado = 11 - resto
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)

    return dv_ingresado == dv_calculado

# --- Agregar empresa ---
def agregar_empresa(nombre, rut, representante, direccion, correo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO empresas (nombre, rut, representante, direccion, correo)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre.upper(), rut.upper(), representante.title(), direccion.title(), correo))
    conn.commit()
    conn.close()
    st.rerun()


# --- Eliminar empresa ---
def eliminar_empresa(id_):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM empresas WHERE id = ?", (id_,))
    conn.commit()
    conn.close()
    st.success("🗑️ Empresa eliminada")
    st.rerun()


# --- Interfaz Streamlit ---
def app():
    st.subheader("🏢 Mantenimiento de Empresas (Subcontratos)")
    crear_tabla_empresas()

    with st.form("form_empresa"):
        nombre = st.text_input("Nombre del Subcontrato").strip()
        rut = st.text_input("RUT (EJ xxxxxxxx-x)").strip()
        representante = st.text_input("Representante").strip()
        direccion = st.text_input("Dirección").strip()
        correo = st.text_input("Correo electrónico").strip()

        submitted = st.form_submit_button("Registrar Empresa")
        if submitted:
            if not (nombre and rut and representante):
                st.warning("⚠️ Debes completar todos los campos obligatorios.")
            elif not validar_rut(rut):
                st.warning("❌ RUT inválido.")
            else:
                try:
                    agregar_empresa(nombre, rut, representante, direccion, correo)
                    st.success("✅ Empresa registrada correctamente.")
                    st.experimental_rerun()  # Refresca la página para mostrar el nuevo registro
                except sqlite3.IntegrityError:
                    st.error("⚠️ Ya existe una empresa con ese nombre.")

    st.divider()
    st.subheader("📋 Empresas Registradas")

    conn = conectar()
    df_empresas = pd.read_sql_query("SELECT * FROM empresas", conn)
    conn.close()

    if not df_empresas.empty:
        for _, fila in df_empresas.iterrows():
            with st.expander(f"{fila['nombre']} - {fila['rut']}"):
                st.write(f"Representante: {fila['representante']}")
                st.write(f"Dirección: {fila['direccion']}")
                st.write(f"Correo: {fila['correo']}")
                if st.button("Eliminar", key=f"del_{fila['id']}"):
                    eliminar_empresa(fila['id'])
                    st.experimental_rerun()
    else:
        st.info("No hay empresas registradas.")
