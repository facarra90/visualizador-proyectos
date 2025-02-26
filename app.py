import streamlit as st
import sqlite3
import pandas as pd

# Configuración de la página para ocupar todo el ancho disponible
st.set_page_config(layout="wide")

@st.cache_data
def cargar_datos_sql():
    # Conectar a la base de datos SQLite (asegúrate que 'tabla_iniciativas_clean.db' esté en la raíz del proyecto)
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

# Cargar los datos desde la base de datos
df = cargar_datos_sql()

st.title("Visualizador de Proyectos FNDR GORE LOS LAGOS")
st.write("Seleccione un proyecto para ver la información asociada.")

# Construir las opciones para el selectbox, agregando una opción por defecto.
opciones = {"Seleccione un proyecto": None}
for _, row in df.iterrows():
    opcion = f"{str(row['CODIGO'])[:10]} - {row['NOMBRE DE LA INICIATIVA']}"
    opciones[opcion] = row['CODIGO']

# Selectbox único para la selección de proyecto, con una opción por defecto.
seleccion = st.selectbox("Seleccione un proyecto:", list(opciones.keys()), key="proyecto_select")

# Si se ha seleccionado un proyecto (es decir, no se mantiene la opción por defecto)
if st.session_state.proyecto_select != "Seleccione un proyecto":
    codigo_final = opciones[st.session_state.proyecto_select]
    # Filtrar el DataFrame para obtener el proyecto seleccionado
    df_proyecto = df[df['CODIGO'] == codigo_final]
    
    st.subheader("Nombre de la Iniciativa:")
    st.write(df_proyecto.iloc[0]['NOMBRE DE LA INICIATIVA'])
    
    st.markdown("## Contratos asociados al proyecto")
    # Agrupar los contratos por ASIGNACION PRESUPUESTARIA CONTRATO
    grupos = df_proyecto.groupby('ASIGNACION PRESUPUESTARIA CONTRATO')
    for asignacion, grupo in grupos:
        st.markdown(f"### {asignacion}")
        # Seleccionar las columnas de interés y eliminar duplicados
        contratos_info = grupo[['RUT', 'NOMBRE / RAZON SOCIAL', 'NRO. RESOL.', 'FECHA RESOLUCION', 'VALOR ESTADO DE PAGO']].drop_duplicates()
        # Agrupar por RUT y combinar NRO. RESOL. y FECHA RESOLUCION en una sola columna formateada,
        # además de sumar VALOR ESTADO DE PAGO para cada RUT.
        contratos_agrupados = contratos_info.groupby('RUT').apply(
            lambda x: pd.Series({
                'NOMBRE / RAZON SOCIAL': x['NOMBRE / RAZON SOCIAL'].iloc[0],
                'Resoluciones': join_resolutions([f"{nro} de {fecha}" for nro, fecha in zip(x['NRO. RESOL.'], x['FECHA RESOLUCION'])]),
                'Total VALOR ESTADO DE PAGO': x['VALOR ESTADO DE PAGO'].sum()
            })
        ).reset_index()
        # Convertir el DataFrame a HTML sin mostrar el índice y renderizarlo
        html_table = contratos_agrupados.to_html(index=False)
        st.markdown(html_table, unsafe_allow_html=True)
