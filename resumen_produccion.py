import streamlit as st
import pandas as pd
from config import supabase

# --- Funciones de acceso a datos en Supabase ---

def leer_produccion():
    """Obtiene actividad y cantidad desde la tabla 'produccion'."""
    resp = (
        supabase
        .table("produccion")
        .select("actividad, cantidad")
        .execute()
    )
    return pd.DataFrame(resp.data)


def leer_actividades():
    """Obtiene descripción y valores unitarios desde la tabla 'actividades'."""
    resp = (
        supabase
        .table("actividades")
        .select("descripcion, valor_produccion, valor_venta")
        .execute()
    )
    return pd.DataFrame(resp.data)

# --- Módulo de Resumen de Producción ---

def app():
    st.subheader("📊 Resumen de Producción por Actividad")

    # 1) Obtener datos
    df_prod = leer_produccion()
    df_act = leer_actividades()

    if df_prod.empty:
        st.info("No hay datos de producción registrados.")
        return

    # 2) Agrupar y sumar
    resumen = df_prod.groupby("actividad", as_index=False).sum()

    # 3) Unir con valores unitarios
    resumen = resumen.merge(
        df_act,
        left_on="actividad", right_on="descripcion",
        how="left"
    )

    # 4) Calcular montos
    resumen["Monto de Producción"] = resumen["cantidad"] * resumen["valor_produccion"]
    resumen["Monto de Venta"] = resumen["cantidad"] * resumen["valor_venta"]

    # 5) Preparar tabla final
    tabla = resumen[[
        "actividad", "cantidad",
        "Monto de Producción", "Monto de Venta"
    ]].rename(columns={
        "actividad": "Actividad Realizada",
        "cantidad": "Realizado QTY"
    })

    # 6) Mostrar con formato
    st.dataframe(
        tabla.style.format({
            "Realizado QTY": "{:.0f}",
            "Monto de Producción": "$ {:,.0f}",
            "Monto de Venta": "$ {:,.0f}"
        }),
        use_container_width=True
    )

if __name__ == "__main__":
    app()
