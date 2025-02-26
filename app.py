import streamlit as st
import sqlite3
import pandas as pd

# Configuración de la página para ocupar todo el ancho disponible
st.set_page_config(layout="wide")

@st.cache_data
def cargar_datos_sql():
    # Conectar a la base de datos SQLite (asegúrate de que 'tabla_iniciativas_clean.db' esté en la raíz del proyecto)
    conn = sqlite3.connect('tabla_iniciativas_clean.db')
    # Cambia "iniciativas" por el nombre real de la tabla, si es necesario.
    df = pd.read_sql_query("SELECT * FROM iniciativas", conn)
    conn.close()
    return df

def join_resolutions(res_list):
    """Une los pares 'NRO. RESOL. de FECHA RESOLUCION' con formato:
       - 1 elemento: "1110 de 16/09/2016"
       - 2 elementos: "1110 de 16/09/2016 y 1421 de 29/11/2016"
       - Más de 2: "1110 de 16/09/2016, 1421 de 29/11/2016 y 1530 de 05/01/2017"
    """
    if not res_list:
        return ""
    elif len(res_list) == 1:
        return res_list[0]
    elif len(res_list) == 2:
        return " y ".join(res_list)
    else:
        return ", ".join(res_list[:-1]) + " y " + res_list[-1]

def pagos_por_año(x):
    """
    Para el DataFrame x (correspondiente a un RUT), filtra solo los registros con
    ESTADO DEL EEPP == 'DEVENGADO', extrae el año de FECHA RESOLUCION y suma el VALOR ESTADO DE PAGO por año.
    Devuelve una cadena formateada, por ejemplo: "2016: $1,200, 2017: $2,500"
    """
    df_dev = x[x['ESTADO DEL EEPP'] == 'DEVENGADO']
    if df_dev.empty:
        return ""
    # Convertir FECHA RESOLUCION a datetime (suponiendo formato día/mes/año)
    fechas = pd.to_datetime(df_dev['FECHA RESOLUCION'], dayfirst=True, errors='coerce')
    # Agrupar por año y sumar
    sums_by_year = df_dev.groupby(fechas.dt.year)['VALOR ESTADO DE PAGO'].sum()
    # Formatear cada suma como moneda en pesos
    formatted = [f"{year}: ${s:,.0f}" for year, s in sums_by_year.items()]
    return ", ".join(formatted)

# Cargar los datos desde la base de datos
df = cargar_datos_sql()

st.title("Visualizador de Proyectos FNDR GORE LOS LAGOS")
st.write("Seleccione un proyecto para ver la información asociada.")

# Construir las opciones para el selectbox, agregando una opción por defecto.
opciones = {"Seleccione un proyecto": None}
for _, row in df.iterrows():
    opcion = f"{str(row['CODIGO'])[:10]} - {row['NOMBRE DE LA INICIATIVA']}"
    opciones[opcion] = row['CODIGO']

# Selectbox único para la selección de proyecto, con opción por defecto.
seleccion = st.selectbox("Seleccione un proyecto:", list(opciones.keys()), key="proyecto_select")

# Si se ha seleccionado un proyecto (opción distinta a la por defecto)
if st.session_state.proyecto_select != "Seleccione un proyecto":
    codigo_final = opciones[st.session_state.proyecto_select]
    # Filtrar el DataFrame para obtener el proyecto seleccionado
    df_proyecto = df[df['CODIGO'] == codigo_final]
    
    st.markdown("## Contratos asociados al proyecto")
    # Agrupar los contratos por ASIGNACION PRESUPUESTARIA CONTRATO
    grupos = df_proyecto.groupby('ASIGNACION PRESUPUESTARIA CONTRATO')
    for asignacion, grupo in grupos:
        st.markdown(f"### {asignacion}")
        # Seleccionar las columnas de interés y eliminar duplicados
        contratos_info = grupo[['RUT', 'NOMBRE / RAZON SOCIAL', 'NRO. RESOL.', 'FECHA RESOLUCION',
                                'VALOR ESTADO DE PAGO', 'ESTADO DEL EEPP']].drop_duplicates()
        # Agrupar por RUT:
        # - Combinar resoluciones (eliminando duplicados) en una sola cadena.
        # - Sumar VALOR ESTADO DE PAGO solo para DEVENGADO.
        # - Calcular el pago desglosado por año.
        contratos_agrupados = contratos_info.groupby('RUT').apply(
            lambda x: pd.Series({
                'NOMBRE / RAZON SOCIAL': x['NOMBRE / RAZON SOCIAL'].iloc[0],
                'Resoluciones': join_resolutions(
                    list(dict.fromkeys([f"{nro} de {fecha}" for nro, fecha in zip(x['NRO. RESOL.'], x['FECHA RESOLUCION'])]))
                ),
                'TOTAL PAGADO': x.loc[x['ESTADO DEL EEPP'] == 'DEVENGADO', 'VALOR ESTADO DE PAGO'].sum(),
                'PAGADO POR AÑO': pagos_por_año(x)
            })
        ).reset_index()
        # Formatear TOTAL PAGADO como moneda en pesos
        contratos_agrupados['TOTAL PAGADO'] = contratos_agrupados['TOTAL PAGADO'].apply(lambda v: "${:,.0f}".format(v))
        
        # Usar Styler para alinear a la derecha la columna TOTAL PAGADO y ocultar el índice
        styled_table = contratos_agrupados.style.hide(axis="index").set_properties(
            subset=['TOTAL PAGADO'], **{'text-align': 'right'}
        )
        st.markdown(styled_table.to_html(), unsafe_allow_html=True)
