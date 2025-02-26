import streamlit as st
import sqlite3
import pandas as pd

@st.cache_data
def cargar_datos_sql():
    # Conectar a la base de datos SQLite (asegúrate que el archivo esté en la raíz del proyecto)
    conn = sqlite3.connect('tabla_iniciativas_clean.db')
    # Reemplaza "iniciativas" por el nombre real de la tabla si es necesario.
    df = pd.read_sql_query("SELECT * FROM iniciativas", conn)
    conn.close()
    return df

# Cargar los datos de la base de datos SQLite
df = cargar_datos_sql()

st.title("Visualizador de Proyectos")
st.write("Selecciona un CODIGO para ver el nombre de la iniciativa y los contratos asociados.")

# Extraer los códigos únicos disponibles
codigos = df['CODIGO'].unique()

# Widget para seleccionar el CODIGO
codigo_seleccionado = st.selectbox("Seleccione un CODIGO:", codigos)

if codigo_seleccionado:
    # Filtrar el DataFrame para el CODIGO seleccionado
    df_proyecto = df[df['CODIGO'] == codigo_seleccionado]
    
    # Mostrar el nombre de la iniciativa (tomamos la primera fila, ya que es el mismo proyecto)
    registro = df_proyecto.iloc[0]
    st.subheader("Nombre de la Iniciativa:")
    st.write(registro['NOMBRE DE LA INICIATIVA'])
    
    st.markdown("## Contratos asociados al proyecto")
    
    # Agrupar los contratos por ASIGNACION PRESUPUESTARIA CONTRATO
    grupos = df_proyecto.groupby('ASIGNACION PRESUPUESTARIA CONTRATO')
    
    # Iterar sobre cada grupo y mostrar la información de contratos
    for asignacion, grupo in grupos:
        st.markdown(f"### {asignacion}")
        # Seleccionamos y eliminamos duplicados en las columnas RUT y NOMBRE / RAZON SOCIAL
        contratos_info = grupo[['RUT', 'NOMBRE / RAZON SOCIAL']].drop_duplicates()
        st.dataframe(contratos_info)
