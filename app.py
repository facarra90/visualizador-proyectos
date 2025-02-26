import streamlit as st
import sqlite3
import pandas as pd

# Configurar la página para ocupar todo el ancho disponible
st.set_page_config(layout="wide")

@st.cache_data
def cargar_datos_sql():
    # Conectar a la base de datos SQLite; asegúrate de que 'tabla_iniciativas_clean.db' esté en la raíz del proyecto.
    conn = sqlite3.connect('tabla_iniciativas_clean.db')
    # Cambia "iniciativas" por el nombre real de la tabla si es necesario.
    df = pd.read_sql_query("SELECT * FROM iniciativas", conn)
    conn.close()
    return df

def join_resolutions(res_list):
    """
    Une los pares "NRO. RESOL. de FECHA RESOLUCION" según:
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

# Cargar la base de datos
df = cargar_datos_sql()

# Usar session_state para almacenar el contrato seleccionado
if 'selected_contract' not in st.session_state:
    st.session_state.selected_contract = None

# Si ya se ha seleccionado un contrato, mostrar solo su detalle
if st.session_state.selected_contract is not None:
    contrato_detalle = df.loc[st.session_state.selected_contract]
    st.title("Detalle del Contrato")
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
    if st.button("Volver"):
        st.session_state.selected_contract = None
        st.experimental_rerun()

# Sino, mostrar la vista del proyecto y la lista de contratos asociados
else:
    st.title("Visualizador de Proyectos FNDR GORE LOS LAGOS")
    st.write("Seleccione un proyecto para ver la información asociada.")
    
    # Construir las opciones del selectbox para proyectos (opción por defecto incluida)
    opciones = {"Seleccione un proyecto": None}
    for _, row in df.iterrows():
        opcion = f"{str(row['CODIGO'])[:10]} - {row['NOMBRE DE LA INICIATIVA']}"
        opciones[opcion] = row['CODIGO']
    
    proyecto_sel = st.selectbox("Seleccione un proyecto:", list(opciones.keys()), key="proyecto_select")
    
    if proyecto_sel != "Seleccione un proyecto":
        codigo_final = opciones[proyecto_sel]
        df_proyecto = df[df['CODIGO'] == codigo_final]
        
        st.subheader("Nombre de la Iniciativa:")
        st.write(df_proyecto.iloc[0]['NOMBRE DE LA INICIATIVA'])
        
        st.markdown("## Contratos asociados al proyecto")
        # Agrupar por ASIGNACION PRESUPUESTARIA CONTRATO
        grupos = df_proyecto.groupby('ASIGNACION PRESUPUESTARIA CONTRATO')
        for asignacion, grupo in grupos:
            st.markdown(f"### {asignacion}")
            # Seleccionar columnas relevantes y eliminar duplicados
            contratos_info = grupo[['RUT', 'NOMBRE / RAZON SOCIAL', 'NRO. RESOL.', 'FECHA RESOLUCION']].drop_duplicates()
            # Agrupar por RUT y combinar las resoluciones en una sola cadena formateada
            contratos_agrupados = contratos_info.groupby('RUT').apply(
                lambda x: pd.Series({
                    'NOMBRE / RAZON SOCIAL': x['NOMBRE / RAZON SOCIAL'].iloc[0],
                    'Resoluciones': join_resolutions([f"{nro} de {fecha}" for nro, fecha in zip(x['NRO. RESOL.'], x['FECHA RESOLUCION'])])
                })
            ).reset_index()
            
            # Mostrar cada fila con un botón "Seleccionar" al lado
            for idx, row in contratos_agrupados.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**RUT:** {row['RUT']}")
                    st.write(f"**Nombre / Razón Social:** {row['NOMBRE / RAZON SOCIAL']}")
                    st.write(f"**Resoluciones:** {row['Resoluciones']}")
                with col2:
                    if st.button("Seleccionar", key=f"select_{asignacion}_{row['RUT']}"):
                        # Buscar la primera fila del DataFrame original para ese RUT
                        matching_rows = contratos_info[contratos_info['RUT'] == row['RUT']]
                        if not matching_rows.empty:
                            original_index = matching_rows.index[0]
                            st.session_state.selected_contract = original_index
                            st.experimental_rerun()
