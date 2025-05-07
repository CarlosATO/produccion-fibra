import streamlit as st
import sqlite3
import pandas as pd

# --- Conexión a base de datos ---
def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

# --- Crear tabla de gastos ---
def crear_tabla_gastos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT,
            detalle TEXT,
            monto REAL,
            observacion TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Agregar gasto ---
def agregar_gasto(empresa, detalle, monto, observacion):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO gastos (empresa, detalle, monto, observacion)
        VALUES (?, ?, ?, ?)
    """, (empresa, detalle, monto, observacion))
    conn.commit()
    conn.close()
    st.success("✅ Gasto registrado exitosamente")
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

    conn = conectar()
    empresas = pd.read_sql("SELECT nombre FROM empresas", conn)["nombre"].tolist()
    conn.close()

    with st.form("form_gasto"):
        empresa = st.selectbox("Empresa (Subcontrato)", empresas)
        detalle = st.text_area("Detalle del gasto")
        monto = st.number_input("Monto ($)", min_value=0.0, step=100.0)
        observacion = st.text_input("Observación")
        if st.form_submit_button("Registrar Gasto"):
            if empresa and detalle and monto > 0:
                agregar_gasto(empresa, detalle, monto, observacion)
            else:
                st.warning("⚠️ Completa todos los campos obligatorios")

    st.divider()
    st.subheader("📋 Gastos registrados")

    conn = conectar()
    df = pd.read_sql("SELECT * FROM gastos", conn)
    conn.close()

    if not df.empty:
        for _, fila in df.iterrows():
            with st.expander(f"{fila['empresa']} - ${fila['monto']:.0f}"):
                st.write(f"Detalle: {fila['detalle']}")
                st.write(f"Observación: {fila['observacion']}")
                if st.button("Eliminar", key=f"del_{fila['id']}"):
                    eliminar_gasto(fila['id'])
    else:
        st.info("No hay gastos registrados.")
