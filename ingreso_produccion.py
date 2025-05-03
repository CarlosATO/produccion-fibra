
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

def crear_tabla_produccion():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produccion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            actividad TEXT,
            trabajador TEXT,
            triot TEXT,
            tramo TEXT,
            inicio TEXT,
            fin TEXT,
            mufa_origen TEXT,
            mufa_final TEXT,
            cantidad REAL,
            rematado REAL
        )
    """)
    conn.commit()
    conn.close()

def obtener_datos_tabla(tabla):
    conn = conectar()
    df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
    conn.close()
    return df

def guardar_produccion(fecha, actividad, trabajador, triot, tramo, inicio, fin, mufa_o, mufa_f, cantidad, rematado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produccion (fecha, actividad, trabajador, triot, tramo, inicio, fin, mufa_origen, mufa_final, cantidad, rematado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (fecha, actividad, trabajador, triot, tramo, inicio, fin, mufa_o, mufa_f, cantidad, rematado))
    conn.commit()
    conn.close()
    st.success("✅ Producción registrada.")

def app():
    st.subheader("📥 Ingreso de Producción")
    crear_tabla_produccion()

    df_actividades = obtener_datos_tabla("actividades")
    df_personal = obtener_datos_tabla("personal")
    df_tramos = obtener_datos_tabla("tramos")

    with st.form("formulario_produccion"):
        fecha = st.date_input("Fecha", value=date.today())
        actividad = st.selectbox("Actividad", df_actividades["descripcion"].tolist())
        trabajador = st.selectbox("Trabajador", df_personal["nombre"].tolist())
        triot = st.selectbox("TRIOT", df_tramos["triot"].unique().tolist())
        tramo = st.selectbox("Tramo", df_tramos[df_tramos["triot"] == triot]["tramo"].tolist())

        tramo_sel = df_tramos[(df_tramos["triot"] == triot) & (df_tramos["tramo"] == tramo)]
        if not tramo_sel.empty:
            inicio = tramo_sel["inicio"].values[0]
            fin = tramo_sel["fin"].values[0]
            mufa_o = tramo_sel["mufa_inicio"].values[0]
            mufa_f = tramo_sel["mufa_fin"].values[0]
        else:
            inicio = fin = mufa_o = mufa_f = ""

        st.text_input("Inicio (metros)", value=inicio, key="i", disabled=True)
        st.text_input("Fin (metros)", value=fin, key="f", disabled=True)
        st.text_input("MUFA Origen", value=mufa_o, key="mo", disabled=True)
        st.text_input("MUFA Final", value=mufa_f, key="mf", disabled=True)

        cantidad = st.number_input("Cantidad realizada", min_value=0.0, step=1.0)
        rematado = st.slider("% Rematado", 0, 100, 0)

        submitted = st.form_submit_button("Registrar producción")
        if submitted:
            guardar_produccion(
                str(fecha), actividad, trabajador, triot, tramo,
                inicio, fin, mufa_o, mufa_f, cantidad, rematado
            )

    st.markdown("---")
    st.subheader("📄 Historial de producción")

    conn = conectar()
    df_historial = pd.read_sql_query("SELECT * FROM produccion", conn)
    conn.close()
    st.dataframe(df_historial, use_container_width=True)
