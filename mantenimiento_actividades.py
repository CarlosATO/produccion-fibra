
import streamlit as st
import sqlite3

def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

def crear_tabla_actividades():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            descripcion TEXT,
            unidad TEXT,
            grupo TEXT,
            tipo TEXT,
            valor_produccion REAL,
            valor_venta REAL
        )
    """)
    conn.commit()
    conn.close()

def obtener_actividades():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actividades")
    datos = cursor.fetchall()
    conn.close()
    return datos

def agregar_actividad(codigo, descripcion, unidad, grupo, tipo, valor_prod, valor_venta):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO actividades (codigo, descripcion, unidad, grupo, tipo, valor_produccion, valor_venta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (codigo, descripcion, unidad, grupo, tipo, valor_prod, valor_venta))
    conn.commit()
    conn.close()
    st.success("✅ Actividad registrada.")

def actualizar_actividad(id_act, codigo, descripcion, unidad, grupo, tipo, valor_prod, valor_venta):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE actividades
        SET codigo = ?, descripcion = ?, unidad = ?, grupo = ?, tipo = ?, valor_produccion = ?, valor_venta = ?
        WHERE id = ?
    """, (codigo, descripcion, unidad, grupo, tipo, valor_prod, valor_venta, id_act))
    conn.commit()
    conn.close()
    st.success("✏️ Actividad actualizada.")

def eliminar_actividad(id_act):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM actividades WHERE id = ?", (id_act,))
    conn.commit()
    conn.close()
    st.success("🗑️ Actividad eliminada.")

def app():
    st.subheader("🧱 Mantenimiento de Actividades")
    crear_tabla_actividades()

    with st.expander("➕ Agregar nueva actividad"):
        codigo = st.text_input("Código")
        descripcion = st.text_area("Descripción")
        unidad = st.text_input("Unidad")
        grupo = st.text_input("Grupo")
        tipo = st.selectbox("Tipo", ["Programada", "Extra Programática"])
        valor_prod = st.number_input("Valor Producción", min_value=0.0, step=100.0)
        valor_venta = st.number_input("Valor Venta", min_value=0.0, step=100.0)
        if st.button("Registrar"):
            if codigo and descripcion and isinstance(valor_prod, (int, float)) and isinstance(valor_venta, (int, float)):
                agregar_actividad(codigo, descripcion, unidad, grupo, tipo, valor_prod, valor_venta)
            else:
                st.warning("⚠️ Verifica que todos los campos estén completos y los valores numéricos sean correctos.")

    st.markdown("---")
    st.subheader("📄 Actividades registradas")

    datos = obtener_actividades()
    for act in datos:
        with st.expander(f"🔧 {act[1]} - {act[2]}"):
            codigo = st.text_input("Código", value=act[1], key=f"cod_{act[0]}")
            descripcion = st.text_area("Descripción", value=act[2], key=f"desc_{act[0]}")
            unidad = st.text_input("Unidad", value=act[3], key=f"uni_{act[0]}")
            grupo = st.text_input("Grupo", value=act[4], key=f"gru_{act[0]}")
            tipo = st.selectbox("Tipo", ["Programada", "Extra Programática"], index=0 if act[5] == "Programada" else 1, key=f"tipo_{act[0]}")
            valor_prod = st.number_input("Valor Producción", value=act[6], step=100.0, key=f"vp_{act[0]}")
            valor_venta = st.number_input("Valor Venta", value=act[7], step=100.0, key=f"vv_{act[0]}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{act[0]}"):
                    actualizar_actividad(act[0], codigo, descripcion, unidad, grupo, tipo, valor_prod, valor_venta)
            with col2:
                if st.button("Eliminar", key=f"del_{act[0]}"):
                    eliminar_actividad(act[0])
