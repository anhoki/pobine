import streamlit as st
import pandas as pd
import altair as alt

# Configuración de la página
st.set_page_config(page_title="Dashboard Demográfico", layout="wide")
st.title("📊 Dashboard de Población por Departamento y Municipio")

# Cargar datos
@st.cache_data
def cargar_datos():
    uploaded_file = st.sidebar.file_uploader("Cargar archivo (CSV o Excel)", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return df
    else:
        st.sidebar.warning("⚠️ Por favor, sube tu archivo de datos")
        # Datos de ejemplo
        data = {
            'Departamento': ['Ejemplo A', 'Ejemplo B'],
            'Municipio': ['Municipio 1', 'Municipio 2'],
            'Total': [10000, 15000],
            'Mujeres': [5200, 7800],
            'Hombres': [4800, 7200],
        }
        return pd.DataFrame(data)

df = cargar_datos()

if df is not None and len(df) > 0:
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    deptos = ['Todos'] + sorted(df['Departamento'].unique().tolist())
    depto_seleccionado = st.sidebar.selectbox("Departamento", deptos)
    
    if depto_seleccionado != 'Todos':
        df_filtrado = df[df['Departamento'] == depto_seleccionado]
    else:
        df_filtrado = df.copy()
    
    municipios = ['Todos'] + sorted(df_filtrado['Municipio'].unique().tolist())
    municipio_seleccionado = st.sidebar.selectbox("Municipio", municipios)
    
    if municipio_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Municipio'] == municipio_seleccionado]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Población", f"{df_filtrado['Total'].sum():,}")
    with col2:
        st.metric("Total Mujeres", f"{df_filtrado['Mujeres'].sum():,}")
    with col3:
        st.metric("Total Hombres", f"{df_filtrado['Hombres'].sum():,}")
    with col4:
        if df_filtrado['Total'].sum() > 0:
            porcentaje_mujeres = (df_filtrado['Mujeres'].sum() / df_filtrado['Total'].sum()) * 100
            st.metric("% Mujeres", f"{porcentaje_mujeres:.1f}%")
        else:
            st.metric("% Mujeres", "0%")
    
    # Gráfico con Altair (ya viene con Streamlit)
    st.subheader("📊 Comparativa por Municipio")
    
    # Preparar datos para gráfico
    df_melted = df_filtrado.melt(
        id_vars=['Municipio'], 
        value_vars=['Mujeres', 'Hombres'],
        var_name='Género', 
        value_name='Cantidad'
    )
    
    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('Municipio:N', title='Municipio'),
        y=alt.Y('Cantidad:Q', title='Población'),
        color='Género:N',
        tooltip=['Municipio', 'Género', 'Cantidad']
    ).properties(
        height=400
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Gráfico de distribución
    st.subheader("🥧 Distribución por Departamento")
    
    if depto_seleccionado == 'Todos':
        df_departamentos = df_filtrado.groupby('Departamento')['Total'].sum().reset_index()
        chart_pie = alt.Chart(df_departamentos).mark_arc().encode(
            theta=alt.Theta(field="Total", type="quantitative"),
            color=alt.Color(field="Departamento", type="nominal"),
            tooltip=['Departamento', 'Total']
        ).properties(
            height=400
        )
        st.altair_chart(chart_pie, use_container_width=True)
    else:
        df_municipios = df_filtrado.groupby('Municipio')['Total'].sum().reset_index()
        chart_pie = alt.Chart(df_municipios).mark_arc().encode(
            theta=alt.Theta(field="Total", type="quantitative"),
            color=alt.Color(field="Municipio", type="nominal"),
            tooltip=['Municipio', 'Total']
        ).properties(
            height=400
        )
        st.altair_chart(chart_pie, use_container_width=True)
    
    # Tabla de datos
    st.subheader("📋 Datos Detallados")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Gráfico de líneas por grupos de edad (si existen columnas de edad)
    columnas_edad = [col for col in df.columns if 'Total' in col and ('<' in col or '-' in col)]
    
    if columnas_edad:
        st.subheader("👥 Distribución por Grupos de Edad")
        
        # Preparar datos para gráfico de líneas
        edad_data = []
        for col in columnas_edad:
            edad_data.append({
                'Grupo de Edad': col.replace('Total ', ''),
                'Población': df_filtrado[col].sum()
            })
        
        df_edad = pd.DataFrame(edad_data)
        
        chart_edad = alt.Chart(df_edad).mark_line(point=True).encode(
            x=alt.X('Grupo de Edad:N', title='Grupo de Edad', sort=None),
            y=alt.Y('Población:Q', title='Población'),
            tooltip=['Grupo de Edad', 'Población']
        ).properties(
            height=400
        )
        
        st.altair_chart(chart_edad, use_container_width=True)
    
    # Exportar datos
    csv = df_filtrado.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )
    
    # Mostrar información del archivo
    st.sidebar.info(f"📊 {len(df_filtrado)} registros mostrados")

else:
    st.error("No se pudieron cargar los datos. Por favor, verifica el formato del archivo.")
