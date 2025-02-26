import streamlit as st
import sqlite3
import pandas as pd

@st.cache_data
def cargar_datos_sql():
    # Conectar a la base de datos SQLite (asegúrate de que 'tabla_iniciativas_clean.db' esté en la raíz del proyecto)
    conn = sqlite3.connect('tabla_iniciativas_clean.db')
    # Cambia "iniciativas" por el nombre real de la tabla si es necesario.
    df = pd.read_sql_query("SELECT * FROM iniciativas", conn)
    conn.close()
    return df

# Cargar los datos
df = cargar_datos_sql()

# Título de la aplicación
st.title("Visualizador de Proyectos FNDR GORE LOS LAGOS")
st.write("Seleccione un CODIGO o busque por NOMBRE DE LA INICIATIVA para ver la información del proyecto.")

# Crear dos columnas para el selectbox y el buscador, uno al lado del otro
col1, col2 = st.columns(2)

with col1:
    # Extraer los códigos únicos y limitar su visualización a 10 dígitos
    codigos = df['CODIGO'].unique()
    # Creamos un diccionario que mapea la versión de visualización (máximo 10 dígitos) al código real
    display_codigos = {str(codigo)[:10]: codigo for codigo in codigos}
    codigo_display = st.selectbox("Seleccione un CODIGO:", list(display_codigos.keys()))
    codigo_seleccionado = display_codigos[codigo_display]

with col2:
    # Buscador por NOMBRE DE LA INICIATIVA
    busqueda_iniciativa = st.text_input("Buscar por NOMBRE DE LA INICIATIVA:")
    if busqueda_iniciativa:
        df_busqueda = df[df["NOMBRE DE LA INICIATIVA"].str.contains(busqueda_iniciativa, case=False, na=False)]
        if not df_busqueda.empty:
            # Se muestran las iniciativas coincidentes
            opciones = df_busqueda["NOMBRE DE LA INICIATIVA"].unique()
            iniciativa_seleccionada = st.selectbox("Proyectos encontrados:", opciones)
            # Se obtiene el código asociado al proyecto seleccionado
            codigo_iniciativa = df_busqueda[df_busqueda["NOMBRE DE LA INICIATIVA"] == iniciativa_seleccionada]["CODIGO"].iloc[0]
        else:
            st.write("No se encontraron proyectos que coincidan.")

# Determinar cuál código usar: si se usó la búsqueda, se prioriza ese resultado.
if busqueda_iniciativa and 'iniciativa_seleccionada' in locals():
    codigo_final = codigo_iniciativa
else:
    codigo_final = codigo_seleccionado

if codigo_final:
    # Filtrar el DataFrame para el proyecto seleccionado
    df_proyecto = df[df['CODIGO'] == codigo_final]
    
    st.subheader("Nombre de la Iniciativa:")
    st.write(df_proyecto.iloc[0]['NOMBRE DE LA INICIATIVA'])
    
    st.markdown("## Contratos asociados al proyecto")
    # Agrupar por ASIGNACION PRESUPUESTARIA CONTRATO
    grupos = df_proyecto.groupby('ASIGNACION PRESUPUESTARIA CONTRATO')
    for asignacion, grupo in grupos:
        st.markdown(f"### {asignacion}")
        # Mostrar las columnas RUT y NOMBRE / RAZON SOCIAL, eliminando duplicados
        contratos_info = grupo[['RUT', 'NOMBRE / RAZON SOCIAL']].drop_duplicates()
        st.dataframe(contratos_info)
