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
    """
    Une los pares "NRO. RESOL. de FECHA RESOLUCION" de la siguiente forma:
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

# Cargar los datos
df = cargar_datos_sql()

st.title("Visualizador de Proyectos FNDR GORE LOS LAGOS")
st.write("Seleccione un proyecto para ver la información asociada.")

# Construir las opciones para el selectbox de proyecto (opción por defecto incluida)
opciones = {"Seleccione un proyecto": None}
for _, row in df.iterrows():
    opcion = f"{str(row['CODIGO'])[:10]} - {row['NOMBRE DE LA INICIATIVA']}"
    opciones[opcion] = row['CODIGO']

# Selectbox único para seleccionar el proyecto
seleccion = st.selectbox("Seleccione un proyecto:", list(opciones.keys()), key="proyecto_select")

# Botón para borrar la selección (restablece al valor por defecto)
if st.button("Borrar selección"):
    st.session_state.proyecto_select = "Seleccione un proyecto"

# Si se ha seleccionado un proyecto (valor distinto al por defecto)
if st.session_state.proyecto_select != "Seleccione un proyecto":
    codigo_final = opciones[st.session_state.proyecto_select]
    # Filtrar el DataFrame para el proyecto seleccionado
    df_proyecto = df[df['CODIGO'] == codigo_final]
    
    st.subheader("Nombre de la Iniciativa:")
    st.write(df_proyecto.iloc[0]['NOMBRE DE LA INICIATIVA'])
    
    st.markdown("## Contratos asociados al proyecto")
    # Agrupar contratos por ASIGNACION PRESUPUESTARIA CONTRATO
    grupos = df_proyecto.groupby('ASIGNACION PRESUPUESTARIA CONTRATO')
    for asignacion, grupo in grupos:
        st.markdown(f"### {asignacion}")
        # Seleccionar columnas de interés y eliminar duplicados
        contratos_info = grupo[['RUT', 'NOMBRE / RAZON SOCIAL', 'NRO. RESOL.', 'FECHA RESOLUCION']].drop_duplicates()
        # Agrupar por RUT y combinar las resoluciones con su fecha en una sola cadena
        contratos_agrupados = contratos_info.groupby('RUT').apply(
            lambda x: pd.Series({
                'NOMBRE / RAZON SOCIAL': x['NOMBRE / RAZON SOCIAL'].iloc[0],
                'Resoluciones': join_resolutions([f"{nro} de {fecha}" for nro, fecha in zip(x['NRO. RESOL.'], x['FECHA RESOLUCION'])])
            })
        ).reset_index()
        # Convertir a HTML sin índice y renderizar
        html_table = contratos_agrupados.to_html(index=False)
        st.markdown(html_table, unsafe_allow_html=True)
    
    st.markdown("## Detalle del contrato")
    # Crear opciones para seleccionar un contrato individual usando el DataFrame original filtrado
    detalles_options = {}
    for idx, row in df_proyecto.iterrows():
        label = f"{row['RUT']} - {row['NOMBRE / RAZON SOCIAL']} - {row['NRO. RESOL.']} de {row['FECHA RESOLUCION']}"
        detalles_options[label] = idx

    contrato_sel = st.selectbox("Seleccione un contrato para ver el detalle:", list(detalles_options.keys()), key="contrato_detalle")
    
    if contrato_sel:
        idx = detalles_options[contrato_sel]
        contrato_detalle = df_proyecto.loc[idx]
        st.markdown("### Detalle del contrato seleccionado")
        # Preparar un DataFrame con los campos de detalle
        detalle_fields = {
            "N EST. PAGO": contrato_detalle["N EST. PAGO"],
            "FECHA ESTADO DE PAGO": contrato_detalle["FECHA ESTADO DE PAGO"],
            "TIPO DE PAGO": contrato_detalle["TIPO DE PAGO"],
            "MES DE CARGO": contrato_detalle["MES DE CARGO"],
            "N DOC. A PAGAR": contrato_detalle["N DOC. A PAGAR"],
            "FECHA DOC. A PAGAR": contrato_detalle["FECHA DOC. A PAGAR"],
            "DETALLE ESTADO DE PAGO": contrato_detalle["DETALLE ESTADO DE PAGO"],
            "VALOR ESTADO DE PAGO": contrato_detalle["VALOR ESTADO DE PAGO"],
            "TOTAL A PAGAR": contrato_detalle["TOTAL A PAGAR"],
            "ESTADO DEL EEPP": contrato_detalle["ESTADO DEL EEPP"],
            "ANALISTA DE ESTADO DE PAGO": contrato_detalle["ANALISTA DE ESTADO DE PAGO"]
        }
        df_detalle = pd.DataFrame(list(detalle_fields.items()), columns=["Campo", "Valor"])
        st.dataframe(df_detalle)
