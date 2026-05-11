import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Poblacional", layout="wide")

st.title("📊 Dashboard de Población por Municipio")
st.caption("Año 2022")

# Cargar datos
uploaded_file = st.sidebar.file_uploader("Cargar archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Sidebar: Selección
    st.sidebar.header("📍 Selección Geográfica")
    
    if 'Municipio' in df.columns:
        municipios = ['Todos'] + sorted(df['Municipio'].unique().tolist())
        municipio_seleccionado = st.sidebar.selectbox("Municipio", municipios)
        
        if municipio_seleccionado != 'Todos':
            df_filtrado = df[df['Municipio'] == municipio_seleccionado]
            titulo = municipio_seleccionado
        else:
            df_filtrado = df
            titulo = "Todos los Municipios"
        
        if 'Departamento' in df.columns and municipio_seleccionado == 'Todos':
            deptos = ['Todos'] + sorted(df['Departamento'].unique().tolist())
            depto_seleccionado = st.sidebar.selectbox("Departamento", deptos)
            if depto_seleccionado != 'Todos':
                df_filtrado = df_filtrado[df_filtrado['Departamento'] == depto_seleccionado]
                titulo = depto_seleccionado
    else:
        df_filtrado = df
        titulo = "Datos"
    
    # Calcular totales
    total_poblacion = df_filtrado['Total'].sum() if 'Total' in df_filtrado.columns else 0
    total_mujeres = df_filtrado['Mujeres'].sum() if 'Mujeres' in df_filtrado.columns else 0
    total_hombres = df_filtrado['Hombres'].sum() if 'Hombres' in df_filtrado.columns else 0
    
    # Tarjetas de totales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 TOTAL POBLACIÓN", f"{total_poblacion:,.0f}")
    with col2:
        st.metric("👩 MUJERES", f"{total_mujeres:,.0f}", delta=f"{total_mujeres/total_poblacion*100:.1f}%" if total_poblacion > 0 else None)
    with col3:
        st.metric("👨 HOMBRES", f"{total_hombres:,.0f}", delta=f"{total_hombres/total_poblacion*100:.1f}%" if total_poblacion > 0 else None)
    
    st.markdown("---")
    
    # Tabla de grupos de edad
    st.subheader("📊 Distribución por Grupos de Edad")
    
    grupos_edad = ['<1', '1-4', '5-9', '10-14', '15-19', '20-24', '25-29', 
                   '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65+']
    
    tabla_data = []
    for grupo in grupos_edad:
        col_total = f'Total {grupo}'
        col_mujeres = f'Mujeres {grupo}'
        col_hombres = f'Hombres {grupo}'
        
        if col_total in df_filtrado.columns:
            total_grupo = df_filtrado[col_total].sum()
            mujeres_grupo = df_filtrado[col_mujeres].sum() if col_mujeres in df_filtrado.columns else 0
            hombres_grupo = df_filtrado[col_hombres].sum() if col_hombres in df_filtrado.columns else 0
            
            tabla_data.append({
                'Grupo Etario': grupo,
                'Total': total_grupo,
                'Mujeres': mujeres_grupo,
                'Hombres': hombres_grupo,
                '%': (total_grupo/total_poblacion*100) if total_poblacion > 0 else 0
            })
    
    if tabla_data:
        df_edades = pd.DataFrame(tabla_data)
        st.dataframe(
            df_edades.style.format({
                'Total': '{:,.0f}',
                'Mujeres': '{:,.0f}',
                'Hombres': '{:,.0f}',
                '%': '{:.1f}%'
            }),
            use_container_width=True
        )
        
        # Gráfico de barras nativo de Streamlit
        st.subheader("📈 Población por Grupo de Edad")
        st.bar_chart(df_edades.set_index('Grupo Etario')['Total'])
        
        # Gráfico de área para comparación por sexo
        st.subheader("👥 Comparación por Sexo y Edad")
        df_comparacion = df_edades.set_index('Grupo Etario')[['Mujeres', 'Hombres']]
        st.bar_chart(df_comparacion)
    
    st.markdown("---")
    
    # Tabla por municipio si hay más de uno
    if 'Municipio' in df.columns and len(df_filtrado['Municipio'].unique()) > 1:
        st.subheader("📋 Resumen por Municipio")
        resumen = df_filtrado.groupby('Municipio').agg({
            'Total': 'sum',
            'Mujeres': 'sum',
            'Hombres': 'sum'
        }).reset_index()
        
        if 'Mujeres' in resumen.columns and 'Total' in resumen.columns:
            resumen['% Mujeres'] = (resumen['Mujeres'] / resumen['Total'] * 100).round(1)
        
        st.dataframe(resumen, use_container_width=True)
        
        # Gráfico de barras por municipio
        st.subheader("Población por Municipio")
        st.bar_chart(resumen.set_index('Municipio')['Total'])
    
    # Descarga de datos
    csv = df_filtrado.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name=f"datos_{titulo}.csv",
        mime="text/csv"
    )
    
    # Información en sidebar
    st.sidebar.info(f"""
    ### 📊 Estadísticas
    - **Municipios:** {df_filtrado['Municipio'].nunique() if 'Municipio' in df_filtrado.columns else 1}
    - **Total registros:** {len(df_filtrado)}
    - **Población total:** {total_poblacion:,.0f}
    """)

else:
    st.info("""
    ### 📁 Carga tu archivo CSV
    
    El archivo debe tener estas columnas:
    - `Municipio` (nombre)
    - `Total` (población total)
    - `Mujeres` (total mujeres)
    - `Hombres` (total hombres)
    - `Total <1`, `Total 1-4`, etc.
    - `Mujeres <1`, `Hombres <1`, etc.
    
    **Puedes usar el botón "Browse files" para subir tu archivo.**
    """)
