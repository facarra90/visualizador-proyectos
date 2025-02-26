import streamlit as st
import sqlite3
import pandas as pd

@st.cache_data
def cargar_datos_sql():
    # Conectar a la base de datos SQLite (asegúrate de que 'tabla_iniciativas_clean.db' esté en la raíz del proyecto)
    conn = sqlite3.connect('tabla_iniciativas_clean.db')
    # Cambia "iniciativas" por el nombre real de la tabla, si es necesario.
    df = pd.read_sql_query("SELECT * FROM iniciativas", conn)
    conn.close()
    return df

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

# Botón para borrar la selección (restablecer a la opción por defecto).
if st.button("Borrar selección"):
    st.session_state.proyecto_select = "Seleccione un proyecto"

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
        contratos_info = grupo[['RUT', 'NOMBRE / RAZON SOCIAL']].drop_duplicates()
        st.dataframe(contratos_info)
