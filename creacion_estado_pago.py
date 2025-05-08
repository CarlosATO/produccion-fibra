import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
from config import supabase

# --- Funciones de acceso a datos en Supabase ---

def leer_empresas():
    resp = (
        supabase
        .table("empresas")
        .select("nombre")
        .order("nombre")
        .execute()
    )
    return [r["nombre"] for r in resp.data] if resp.data else []


def leer_produccion(empresa_sel):
    prod = pd.DataFrame(
        supabase
        .table("produccion")
        .select("id, fecha, actividad, trabajador, cantidad")
        .execute()
        .data
    )
    perso = pd.DataFrame(
        supabase
        .table("personal")
        .select("nombre, empresa")
        .execute()
        .data
    )
    acts = pd.DataFrame(
        supabase
        .table("actividades")
        .select("descripcion, valor_produccion, valor_venta")
        .execute()
        .data
    )
    if prod.empty or perso.empty or acts.empty:
        return pd.DataFrame()
    df = prod.merge(perso, left_on="trabajador", right_on="nombre")
    df = df[df["empresa"] == empresa_sel]
    df = df.merge(acts, left_on="actividad", right_on="descripcion")
    used = {r["produccion_id"] for r in supabase.table(
        "estados_pago_detalle").select("produccion_id").execute().data}
    df = df[~df["id"].isin(used)]
    df["Monto Producción"] = df["cantidad"] * df["valor_produccion"]
    return df.reset_index(drop=True)


def leer_gastos(empresa_sel):
    df_g = pd.DataFrame(
        supabase
        .table("gastos")
        .select("id, empresa, detalle, monto")
        .execute()
        .data
    )
    if df_g.empty:
        return pd.DataFrame()
    df_g = df_g[df_g["empresa"] == empresa_sel]
    used = {r["gasto_id"] for r in supabase.table(
        "estados_pago_gastos").select("gasto_id").execute().data}
    df_g = df_g[~df_g["id"].isin(used)]
    df_g = df_g.rename(columns={"detalle": "descripcion"})
    return df_g.reset_index(drop=True)

# --- Generación de PDF ---

def generar_pdf_bytes(corr, empresa, fecha, df_prod, df_g, tot_p, tot_g, neto):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(True, 15)

    # Título
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 10, f'Estado de Pago {corr}', ln=True, align='C')
    pdf.ln(5)

    # Empresa y Fecha
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(100, 6, f'Empresa: {empresa}', ln=0)
    pdf.cell(0, 6, f'Fecha: {fecha}', ln=1)
    pdf.ln(3)

        # Separador de texto
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 4, '-' * 100, ln=1)
    pdf.ln(5)

    # Sección Producción
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 6, 'Producción', ln=1)
    pdf.ln(2)
    pdf.set_font('Helvetica', '', 11)
    for _, r in df_prod.iterrows():
        pdf.multi_cell(0, 6, f"{r['actividad']}  |  Cant: {r['cantidad']}  |  Monto: ${r['Monto Producción']:,.0f}")
    pdf.ln(2)
        # Total Producción
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 6, f"Total Producción: ${tot_p:,.0f}", ln=1)
    pdf.ln(5)
    # Separador de texto
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 4, '-' * 100, ln=1)
    pdf.ln(5)

    # Sección Gastos
    if not df_g.empty:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 6, 'Gastos', ln=1)
        pdf.ln(2)
        pdf.set_font('Helvetica', '', 11)
        for _, r in df_g.iterrows():
            pdf.multi_cell(0, 6, f"{r['descripcion']}  |  Monto: ${r['monto']:,.0f}")
        pdf.ln(2)
                # Total Gastos
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 6, f"Total Gastos: ${tot_g:,.0f}", ln=1)
        pdf.ln(5)
        # Separador de texto
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 4, '-' * 100, ln=1)
        pdf.ln(5)

    # Neto a Pagar
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, f"Neto a Pagar: ${neto:,.0f}", ln=1)
    pdf.ln(10)

    # Bloque Autorización
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 6, 'SE AUTORIZA A FACTURAR A', ln=1)
    pdf.ln(2)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 6, 'SOMYL S.A. | RUT: 76.002.581-K', ln=1)
    pdf.multi_cell(0, 6, 'Dirección: Puerta Oriente 361 Of. 311 B, Torre B, Colina')
    pdf.ln(2)
    pdf.cell(0, 6, 'AUTORIZA: Luis Medina', ln=1)
    pdf.cell(0, 6, 'CORREO: lmedina@somyl.com', ln=1)
    pdf.ln(2)
    pdf.multi_cell(0, 6, 'ENVIAR FACTURA A: cynthia.miranda@somyl.com; carlos.alegria@somyl.com')

    return pdf.output(dest='S').encode('latin1')

# --- Inserción en Supabase ---

def insertar_estado_pago(corr, emp, tp, tg, neto):
    supabase.table('estados_pago').insert({
        'correlativo': corr,
        'fecha': datetime.date.today().isoformat(),
        'empresa': emp,
        'total_produccion': float(tp),
        'total_gastos': float(tg),
        'neto': float(neto)
    }).execute()
    supabase.table('estados_pago_detalle').insert([
        {'correlativo': corr, 'produccion_id': int(i)}
        for i in st.session_state['prod_sel']['id']
    ]).execute()
    supabase.table('estados_pago_gastos').insert([
        {'correlativo': corr, 'gasto_id': int(i)}
        for i in st.session_state['gast_sel']['id']
    ]).execute()

# --- UI principal ---

def app():
    st.subheader("🧾 Creación de Estado de Pago")

    # Callback para reset
    def reset_on_change():
        for k in ['prod_disp', 'prod_sel', 'gast_disp', 'gast_sel']:
            st.session_state.pop(k, None)

    empresa_sel = st.selectbox(
        "Selecciona Subcontrato", leer_empresas(),
        key='empresa_sel', on_change=reset_on_change
    )

    df_prod = leer_produccion(empresa_sel)
    df_g = leer_gastos(empresa_sel)
    if df_prod.empty and df_g.empty:
        st.info("No hay datos para este subcontrato.")
        return

    # Initialize session state tables
    for key, df in [('prod_disp', df_prod), ('prod_sel', df_prod.iloc[0:0]),
                    ('gast_disp', df_g), ('gast_sel', df_g.iloc[0:0])]:
        if key not in st.session_state:
            st.session_state[key] = df.copy()

    # Producción section
    st.markdown("### Producción")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Disponibles**")
        st.dataframe(st.session_state['prod_disp'], use_container_width=True)
        sel_add = st.multiselect(
            'IDs a añadir', st.session_state['prod_disp']['id'].tolist(),
            key='prod_ids_add'
        )
        if st.button('>> Añadir Producción'):
            to_add = st.session_state['prod_disp'][
                st.session_state['prod_disp']['id'].isin(sel_add)
            ]
            st.session_state['prod_sel'] = pd.concat([
                st.session_state['prod_sel'], to_add
            ]).reset_index(drop=True)
            st.session_state['prod_disp'] = st.session_state['prod_disp'][
                ~st.session_state['prod_disp']['id'].isin(sel_add)
            ].reset_index(drop=True)
    with col2:
        st.write("**Seleccionadas**")
        st.dataframe(st.session_state['prod_sel'], use_container_width=True)
        sel_rem = st.multiselect(
            'IDs a quitar', st.session_state['prod_sel']['id'].tolist(),
            key='prod_ids_rem'
        )
        if st.button('<< Quitar Producción'):
            back = st.session_state['prod_sel'][
                st.session_state['prod_sel']['id'].isin(sel_rem)
            ]
            st.session_state['prod_disp'] = pd.concat([
                st.session_state['prod_disp'], back
            ]).reset_index(drop=True)
            st.session_state['prod_sel'] = st.session_state['prod_sel'][
                ~st.session_state['prod_sel']['id'].isin(sel_rem)
            ].reset_index(drop=True)

    # Gastos section
    st.markdown("### Gastos")
    g1, g2 = st.columns(2)
    with g1:
        st.write("**Disponibles**")
        st.dataframe(st.session_state['gast_disp'], use_container_width=True)
        sel_addg = st.multiselect(
            'IDs gasto añadir', st.session_state['gast_disp']['id'].tolist(),
            key='gast_ids_add'
        )
        if st.button('>> Añadir Gasto'):
            addg = st.session_state['gast_disp'][
                st.session_state['gast_disp']['id'].isin(sel_addg)
            ]
            st.session_state['gast_sel'] = pd.concat([
                st.session_state['gast_sel'], addg
            ]).reset_index(drop=True)
            st.session_state['gast_disp'] = st.session_state['gast_disp'][
                ~st.session_state['gast_disp']['id'].isin(sel_addg)
            ].reset_index(drop=True)
    with g2:
        st.write("**Seleccionados**")
        st.dataframe(st.session_state['gast_sel'], use_container_width=True)
        sel_remg = st.multiselect(
            'IDs gasto quitar', st.session_state['gast_sel']['id'].tolist(),
            key='gast_ids_rem'
        )
        if st.button('<< Quitar Gasto'):
            backg = st.session_state['gast_sel'][
                st.session_state['gast_sel']['id'].isin(sel_remg)
            ]
            st.session_state['gast_disp'] = pd.concat([
                st.session_state['gast_disp'], backg
            ]).reset_index(drop=True)
            st.session_state['gast_sel'] = st.session_state['gast_sel'][
                ~st.session_state['gast_sel']['id'].isin(sel_remg)
            ].reset_index(drop=True)

    # Totales
    df_s = st.session_state['prod_sel']
    df_gs = st.session_state['gast_sel']
    tp = (df_s['cantidad'] * df_s['valor_produccion']).sum()
    tg = df_gs['monto'].sum()
    neto = tp - tg
    st.markdown("---")
    ctp, ctg, cneto = st.columns(3)
    ctp.metric('PRODUCCIÓN', f"${tp:,.0f}")
    ctg.metric('GASTOS', f"${tg:,.0f}")
    cneto.metric('NETO', f"${neto:,.0f}")

    # PDF y Guardar
    st.markdown("---")
    pbtn, gbtn = st.columns(2)
    with pbtn:
        if st.button('📄 Previsualizar PDF'):
            count = len(supabase.table('estados_pago').select('correlativo').execute().data)
            corr = f"EGTD-{count+1:02d}"
            fecha = datetime.date.today().isoformat()
            pdf = generar_pdf_bytes(corr, empresa_sel, fecha, df_s, df_gs, tp, tg, neto)
            st.download_button('Descargar Preview', pdf, f'preview_{corr}.pdf', 'application/pdf')
    with gbtn:
        if st.button('💾 Guardar Estado'):
            insertar_estado_pago(corr, empresa_sel, tp, tg, neto)
            st.success(f'✅ Estado {corr} guardado')

if __name__ == '__main__':
    app()
