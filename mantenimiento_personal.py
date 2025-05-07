import streamlit as st
import sqlite3
import re
import pandas as pd

# --- Conexión a la base de datos ---
def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

# --- Creación de tabla personal ---
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
    """
    )
    conn.commit()
    conn.close()

# --- Operaciones CRUD ---
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
    cursor.execute(
        """
        INSERT INTO personal (nombre, rut, cargo, empresa)
        VALUES (?, ?, ?, ?)
        """,
        (nombre, rut, cargo, empresa),
    )
    conn.commit()
    conn.close()
    st.success("✅ Personal registrado.")


def actualizar_personal(id_pers, nombre, rut, cargo, empresa):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE personal
        SET nombre = ?, rut = ?, cargo = ?, empresa = ?
        WHERE id = ?
        """,
        (nombre, rut, cargo, empresa, id_pers),
    )
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

# --- Validación de RUT ---
def es_rut_valido(rut):
    return bool(re.match(r"^\d{7,8}-[\dkK]$", rut.strip()))

# --- Interfaz de usuario ---
def app():
    st.subheader("👷 Mantenimiento de Personal")
    crear_tabla_personal()

    # Cargar lista de empresas existentes
    conn = conectar()
    df_empresas = pd.read_sql_query(
        "SELECT nombre FROM empresas ORDER BY nombre", conn
    )
    empresas = df_empresas["nombre"].tolist()
    conn.close()

    with st.expander("➕ Agregar nuevo trabajador"):
        nombre = st.text_input("Nombre", key="new_nombre")
        rut = st.text_input("RUT (ej: 12345678-9)", key="new_rut")
        cargo = st.text_input("Cargo", key="new_cargo")
        empresa = st.selectbox("Empresa", empresas, key="new_empresa")

        if st.button("Registrar"):
            if not nombre or not rut:
                st.warning("⚠️ Nombre y RUT son obligatorios.")
            elif not es_rut_valido(rut):
                st.error(
                    "❌ El RUT debe tener el formato correcto, por ejemplo: 12345678-9"
                )
            else:
                agregar_personal(
                    nombre.strip(), rut.upper().strip(), cargo.strip(), empresa
                )

    st.markdown("---")
    st.subheader("📋 Personal registrado")

    datos = obtener_personal()
    for pers in datos:
        id_pers, nom, rut_val, car, emp = pers
        with st.expander(f"🔧 {nom} - {rut_val}"):
            nombre = st.text_input("Nombre", value=nom, key=f"nom_{id_pers}")
            rut = st.text_input("RUT", value=rut_val, key=f"rut_{id_pers}")
            cargo = st.text_input("Cargo", value=car, key=f"car_{id_pers}")
            # seleccionar empresa existente
            default_idx = empresas.index(emp) if emp in empresas else 0
            empresa_sel = st.selectbox(
                "Empresa",
                empresas,
                index=default_idx,
                key=f"emp_{id_pers}",
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{id_pers}"):
                    if not es_rut_valido(rut):
                        st.error("❌ Formato de RUT incorrecto. No se puede actualizar.")
                    else:
                        actualizar_personal(
                            id_pers,
                            nombre.strip(),
                            rut.upper().strip(),
                            cargo.strip(),
                            empresa_sel,
                        )
            with col2:
                if st.button("Eliminar", key=f"del_{id_pers}"):
                    eliminar_personal(id_pers)

if __name__ == "__main__":
    app()
