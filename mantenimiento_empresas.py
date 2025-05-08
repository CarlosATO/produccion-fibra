import streamlit as st
import re
from config import supabase

# --- Validación de RUT chileno ---
def validar_rut(rut: str) -> bool:
    rut_clean = rut.replace('.', '').replace('-', '').upper()
    if not re.match(r"^\d{7,8}[0-9K]$", rut_clean):
        return False
    cuerpo, dv_ingresado = rut_clean[:-1], rut_clean[-1]
    suma, multiplo = 0, 2
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

# --- Funciones de acceso a datos ---

def listar_empresas():
    """Devuelve todas las empresas registradas."""
    resp = (
        supabase
        .table('empresas')
        .select('id, nombre, rut, representante, direccion, correo')
        .order('nombre')
        .execute()
    )
    return resp.data or []


def agregar_empresa(nombre: str, rut: str, representante: str, direccion: str, correo: str):
    """Inserta una nueva empresa en Supabase."""
    supabase.table('empresas').insert({
        'nombre': nombre.upper(),
        'rut': rut.upper(),
        'representante': representante.title(),
        'direccion': direccion.title(),
        'correo': correo
    }).execute()
    st.success('✅ Empresa registrada correctamente.')


def eliminar_empresa(id_emp: int):
    """Elimina la empresa especificada por ID."""
    supabase.table('empresas').delete().eq('id', id_emp).execute()
    st.success('🗑️ Empresa eliminada.')

# --- Interfaz de usuario ---
def app():
    st.subheader('🏢 Mantenimiento de Empresas (Subcontratos)')

    # 1) Formulario de registro
    with st.form('form_empresa'):
        nombre = st.text_input('Nombre del Subcontrato', key='new_nombre')
        rut = st.text_input('RUT (EJ xxxxxxxx-x)', key='new_rut')
        representante = st.text_input('Representante', key='new_rep')
        direccion = st.text_input('Dirección', key='new_dir')
        correo = st.text_input('Correo electrónico', key='new_email')
        submitted = st.form_submit_button('Registrar Empresa')
        if submitted:
            if not (nombre and rut and representante):
                st.warning('⚠️ Debes completar todos los campos obligatorios.')
            elif not validar_rut(rut):
                st.warning('❌ RUT inválido.')
            else:
                try:
                    agregar_empresa(nombre, rut, representante, direccion, correo)
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f'⚠️ Error al registrar empresa: {e}')

    st.divider()
    st.subheader('📋 Empresas Registradas')

    # 2) Listado y acciones
    empresas = listar_empresas()
    if empresas:
        for emp in empresas:
            with st.expander(f"{emp['nombre']} - {emp['rut']}"):
                st.write(f"**Representante:** {emp['representante']}")
                st.write(f"**Dirección:** {emp['direccion']}")
                st.write(f"**Correo:** {emp['correo']}")
                if st.button('Eliminar', key=f"del_{emp['id']}"):
                    eliminar_empresa(emp['id'])
                    st.experimental_rerun()
    else:
        st.info('No hay empresas registradas.')

if __name__ == '__main__':
    app()
