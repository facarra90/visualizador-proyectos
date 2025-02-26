import streamlit as st
import sqlite3
import pandas as pd

@st.cache_data
def cargar_datos_sql():
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('tabla_iniciativas_clean.db')
    # Ajusta el nombre de la tabla según corresponda; en este ejemplo se asume que la tabla se llama "iniciativas"
    df = pd.read_sql_query("SELECT * FROM iniciativas", conn)
    conn.close()
    return df

# Cargar los datos de la base de datos SQLite
df = cargar_datos_sql()

st.title("Visualizador de Proyectos")
st.write("Selecciona un CODIGO para ver el nombre de la iniciativa asociada.")

# Extraer los códigos únicos de la base de datos
codigos = df['CODIGO'].unique()

# Crear un selectbox para que el usuario seleccione un CODIGO
codigo_seleccionado = st.selectbox("Seleccione un CODIGO:", codigos)

if codigo_seleccionado:
    # Filtrar el DataFrame para obtener la fila correspondiente al CODIGO seleccionado
    registro = df[df['CODIGO'] == codigo_seleccionado].iloc[0]
    st.subheader("Nombre de la Iniciativa:")
    st.write(registro['NOMBRE DE LA INICIATIVA'])
