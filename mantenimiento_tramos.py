
import streamlit as st
import sqlite3

def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

def crear_tabla_tramos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tramos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            triot TEXT,
            tramo TEXT,
            inicio TEXT,
            fin TEXT,
            mufa_inicio TEXT,
            mufa_fin TEXT
        )
    """)
    conn.commit()
    conn.close()

def obtener_tramos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tramos")
    datos = cursor.fetchall()
    conn.close()
    return datos

def agregar_tramo(triot, tramo, inicio, fin, mufa_inicio, mufa_fin):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tramos (triot, tramo, inicio, fin, mufa_inicio, mufa_fin)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (triot, tramo, inicio, fin, mufa_inicio, mufa_fin))
    conn.commit()
    conn.close()
    st.success("✅ Tramo registrado correctamente.")

def actualizar_tramo(idt, triot, tramo, inicio, fin, mufa_inicio, mufa_fin):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tramos
        SET triot = ?, tramo = ?, inicio = ?, fin = ?, mufa_inicio = ?, mufa_fin = ?
        WHERE id = ?
    """, (triot, tramo, inicio, fin, mufa_inicio, mufa_fin, idt))
    conn.commit()
    conn.close()
    st.success("✏️ Tramo actualizado.")

def eliminar_tramo(idt):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tramos WHERE id = ?", (idt,))
    conn.commit()
    conn.close()
    st.success("🗑️ Tramo eliminado.")

def app():
    st.subheader("📍 Mantenimiento de Tramos")
    crear_tabla_tramos()

    with st.expander("➕ Agregar nuevo tramo"):
        triot = st.text_input("Nombre del TRIOT")
        tramo = st.text_input("Tramo")
        inicio = st.text_input("Inicio (metro)")
        fin = st.text_input("Fin (metro)")
        mufa_inicio = st.text_input("MUFA Inicio")
        mufa_fin = st.text_input("MUFA Fin")
        if st.button("Registrar tramo"):
            if triot and tramo:
                agregar_tramo(triot, tramo, inicio, fin, mufa_inicio, mufa_fin)
            else:
                st.warning("⚠️ Ingresa al menos TRIOT y Tramo.")

    st.markdown("---")
    st.subheader("📄 Tramos registrados")

    datos = obtener_tramos()
    for t in datos:
        with st.expander(f"🔧 {t[1]} - Tramo {t[2]}"):
            triot = st.text_input("TRIOT", value=t[1], key=f"tr_{t[0]}")
            tramo = st.text_input("Tramo", value=t[2], key=f"tt_{t[0]}")
            inicio = st.text_input("Inicio", value=t[3], key=f"i_{t[0]}")
            fin = st.text_input("Fin", value=t[4], key=f"f_{t[0]}")
            mufa_inicio = st.text_input("MUFA Inicio", value=t[5], key=f"mi_{t[0]}")
            mufa_fin = st.text_input("MUFA Fin", value=t[6], key=f"mf_{t[0]}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar", key=f"act_{t[0]}"):
                    actualizar_tramo(t[0], triot, tramo, inicio, fin, mufa_inicio, mufa_fin)
            with col2:
                if st.button("Eliminar", key=f"del_{t[0]}"):
                    eliminar_tramo(t[0])
