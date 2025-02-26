import streamlit as st
import sqlite3
import pandas as pd

@st.cache_data
def cargar_datos_sql():
    # Conectar a la base de datos SQLite (asegúrate que 'tabla_iniciativas_clean.db' esté en la raíz del proyecto)
    conn = sqlite3.connect('tabla_iniciativas_clean.db')
    # Reemplaza "iniciativas" por el nombre real de la tabla si es necesario.
    df = pd.read_sql_query("SELECT * FROM iniciativas", conn)
    conn.close()
    return df

# Cargar los datos
df = cargar_datos_sql()

st.title("Visualizador de Proyectos FNDR GORE LOS LAGOS")
st.write("Utiliza el buscador para filtrar proyectos por nombre o selecciona uno directamente.")

# Campo para buscar por NOMBRE DE LA INICIATIVA
busqueda = st.text_input("Buscar por NOMBRE DE LA INICIATIVA:")

# Filtrar las opciones en función del término de búsqueda.
if busqueda:
    df_filtrado = df[df["NOMBRE DE LA INICIATIVA"].str.contains(busqueda, case=False, na=False)]
else:
    df_filtrado = df

# Crear las opciones para el selectbox:
# Cada opción muestra hasta 10 dígitos del código seguido del nombre de la iniciativa.
opciones = {
    f"{str(row['CODIGO'])[:10]} - {row['NOMBRE DE LA INICIATIVA']}": row['CODIGO']
    for _, row in df_filtrado.iterrows()
}

# Ordenar las opciones para una visualización consistente.
opciones_ordenadas = dict(sorted(opciones.items()))

# Selectbox único que muestra las opciones filtradas.
seleccion = st.selectbox("Seleccione un proyecto:", list(opciones_ordenadas.keys()))

# Se obtiene el código asociado a la opción seleccionada.
codigo_final = opciones_ordenadas[seleccion]

if codigo_final:
    # Filtrar el DataFrame para el proyecto seleccionado
    df_proyecto = df[df['CODIGO'] == codigo_final]
    
    st.subheader("Nombre de la Iniciativa:")
    st.write(df_proyecto.iloc[0]['NOMBRE DE LA INICIATIVA'])
    
    st.markdown("## Contratos asociados al proyecto")
    # Agrupar los contratos por ASIGNACION PRESUPUESTARIA CONTRATO
    grupos = df_proyecto.groupby('ASIGNACION PRESUPUESTARIA CONTRATO')
    for asignacion, grupo in grupos:
        st.markdown(f"### {asignacion}")
        # Mostrar las columnas RUT y NOMBRE / RAZON SOCIAL, eliminando duplicados
        contratos_info = grupo[['RUT', 'NOMBRE / RAZON SOCIAL']].drop_duplicates()
        st.dataframe(contratos_info)
