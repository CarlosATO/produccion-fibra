import streamlit as st
import sqlite3
import pandas as pd

# --- Conexión a la base de datos ---
def conectar():
    return sqlite3.connect("productividad_fibra.db", check_same_thread=False)

# --- Módulo de Resumen de Producción ---
def app():
    st.subheader("📊 Resumen de Producción por Actividad")
    
    # Leer datos
    conn = conectar()
    df_prod = pd.read_sql("SELECT actividad, cantidad FROM produccion", conn)
    df_act = pd.read_sql("SELECT descripcion, valor_produccion, valor_venta FROM actividades", conn)
    conn.close()

    if df_prod.empty:
        st.info("No hay datos de producción registrados.")
        return

    # Agrupar cantidades por actividad
    resumen = df_prod.groupby("actividad", as_index=False).sum()

    # Unir con valores unitarios
    resumen = resumen.merge(
        df_act,
        left_on="actividad", right_on="descripcion",
        how="left"
    )

    # Calcular montos
    resumen["Monto de Producción"] = resumen["cantidad"] * resumen["valor_produccion"]
    resumen["Monto de Venta"] = resumen["cantidad"] * resumen["valor_venta"]

    # Armar tabla final
    tabla = resumen[[
        "actividad",
        "cantidad",
        "Monto de Producción",
        "Monto de Venta"
    ]].rename(columns={
        "actividad": "Actividad Realizada",
        "cantidad": "Realizado QTY"
    })

    # Mostrar con formato
    st.dataframe(
        tabla.style.format({
            "Realizado QTY": "{:.0f}",
            "Monto de Producción": "$ {:,.0f}",
            "Monto de Venta": "$ {:,.0f}"
        }),
        use_container_width=True
    )
