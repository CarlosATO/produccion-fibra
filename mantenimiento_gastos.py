import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- Conexión a la base de datos ---
def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

# --- Crear tabla gastos si no existe ---
def crear_tabla_gastos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT,
            detalle TEXT,
            monto REAL,
            observacion TEXT,
            fecha TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Obtener nombres de empresas ---
def obtener_empresas():
    conn = conectar()
    df = pd.read_sql_query("SELECT nombre FROM empresas", conn)
    conn.close()
    return df["nombre"].tolist()

# --- Guardar gasto ---
def guardar_gasto(empresa, detalle, monto, observacion):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO gastos (empresa, detalle, monto, observacion, fecha)
        VALUES (?, ?, ?, ?, ?)
    """, (empresa, detalle.title(), monto, observacion.title(), str(date.today())))
    conn.commit()
    conn.close()
    st.success("✅ Gasto registrado correctamente")
    st.rerun()

# --- Eliminar gasto ---
def eliminar_gasto(id_):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gastos WHERE id = ?", (id_,))
    conn.commit()
    conn.close()
    st.success("🗑️ Gasto eliminado")
    st.rerun()

# --- Interfaz principal ---
def app():
    st.subheader("💸 Registro de Gastos por Empresa")
    crear_tabla_gastos()

    empresas = obtener_empresas()
    if not empresas:
        st.warning("⚠️ Debes registrar empresas antes de ingresar gastos.")
        return

    with st.form("form_gasto"):
        empresa = st.selectbox("Nombre del Subcontrato", empresas)
        detalle = st.text_input("Detalle del gasto").strip()
        monto = st.number_input("Monto del gasto", min_value=0.0, step=100.0)
        observacion = st.text_area("Observación").strip()

        if st.form_submit_button("Registrar Gasto"):
            if not detalle:
                st.warning("⚠️ El campo 'Detalle del gasto' es obligatorio.")
            elif monto == 0:
                st.warning("⚠️ El monto debe ser mayor que 0.")
            else:
                guardar_gasto(empresa, detalle, monto, observacion)

    st.divider()
    st.subheader("📋 Gastos Registrados")

    conn = conectar()
    df_gastos = pd.read_sql_query("SELECT * FROM gastos ORDER BY fecha DESC", conn)
    conn.close()

    if not df_gastos.empty:
        for _, row in df_gastos.iterrows():
            with st.expander(f"{row['empresa']} - {row['detalle']} - ${row['monto']:.0f}"):
                st.write(f"Fecha: {row['fecha']}")
                st.write(f"Observación: {row['observacion']}")
                if st.button("Eliminar", key=f"del_{row['id']}"):
                    eliminar_gasto(row['id'])
    else:
        st.info("No hay gastos registrados.")
