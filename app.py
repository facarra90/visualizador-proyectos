import streamlit as st
import pandas as pd

# Función para cargar los datos y cachearlos para mejorar el rendimiento
@st.cache_data
def cargar_datos():
    # Asegúrate de que el archivo 'tabla_iniciativas_clean.xlsx' se encuentre en el mismo directorio que este script
    df = pd.read_excel('tabla_iniciativas_clean.xlsx')
    return df

# Cargar la base de datos
df = cargar_datos()

# Título y descripción de la aplicación
st.title("Visualizador de Proyectos")
st.write("Selecciona un CODIGO para ver el nombre de la iniciativa asociada.")

# Obtener la lista de códigos únicos disponibles en la base de datos
codigos = df['CODIGO'].unique()

# Crear un widget selectbox para que el usuario seleccione el CODIGO
codigo_seleccionado = st.selectbox("Seleccione un CODIGO:", codigos)

# Al seleccionar un CODIGO, se filtra el DataFrame y se muestra el NOMBRE DE LA INICIATIVA correspondiente
if codigo_seleccionado:
    registro = df[df['CODIGO'] == codigo_seleccionado].iloc[0]
    st.subheader("Nombre de la Iniciativa:")
    st.write(registro['NOMBRE DE LA INICIATIVA'])
