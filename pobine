import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Dashboard Demográfico", layout="wide")
st.title("📊 Dashboard de Población por Departamento y Municipio")

# Cargar datos
@st.cache_data
def cargar_datos():
    # Aquí puedes cambiar la fuente: CSV, Excel, o pegar datos
    # Opción 1: Desde archivo subido
    uploaded_file = st.sidebar.file_uploader("Cargar archivo (CSV o Excel)", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return df
    else:
        # Datos de ejemplo (reemplázalos con tus datos reales)
        st.sidebar.warning("Usando datos de ejemplo. Sube tu archivo.")
        return crear_datos_ejemplo()

def crear_datos_ejemplo():
    # Función para generar datos demo (solo para probar)
    data = {
        'Departamento': ['Dept A', 'Dept A', 'Dept B', 'Dept B'],
        'Municipio': ['Mun 1', 'Mun 2', 'Mun 3', 'Mun 4'],
        'Total': [10000, 15000, 20000, 12000],
        'Mujeres': [5200, 7800, 10500, 6300],
        'Hombres': [4800, 7200, 9500, 5700],
        'Total <1': [200, 300, 400, 250],
        'Total 65+': [800, 1200, 1500, 900]
    }
    return pd.DataFrame(data)

df = cargar_datos()

if df is not None:
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por departamento
    deptos = ['Todos'] + sorted(df['Departamento'].unique().tolist())
    depto_seleccionado = st.sidebar.selectbox("Departamento", deptos)
    
    # Filtrar datos
    if depto_seleccionado != 'Todos':
        df_filtrado = df[df['Departamento'] == depto_seleccionado]
    else:
        df_filtrado = df.copy()
    
    # Filtro por municipio
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
        porcentaje_mujeres = (df_filtrado['Mujeres'].sum() / df_filtrado['Total'].sum()) * 100
        st.metric("% Mujeres", f"{porcentaje_mujeres:.1f}%")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras por municipio
        fig_bar = px.bar(
            df_filtrado, 
            x='Municipio', 
            y=['Mujeres', 'Hombres'],
            title="Población por Municipio",
            barmode='group'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Gráfico de pastel departamental
        if depto_seleccionado == 'Todos':
            datos_pastel = df_filtrado.groupby('Departamento')['Total'].sum().reset_index()
            fig_pie = px.pie(
                datos_pastel, 
                values='Total', 
                names='Departamento',
                title="Distribución por Departamento"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            # Si hay un departamento seleccionado, mostrar distribución municipal
            fig_pie = px.pie(
                df_filtrado, 
                values='Total', 
                names='Municipio',
                title=f"Distribución en {depto_seleccionado}"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tabla de datos
    st.subheader("📋 Datos Detallados")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Análisis por grupos de edad (si las columnas existen)
    columnas_edad = [col for col in df.columns if 'Total' in col and any(str(i) in col for i in range(0, 100))]
    
    if columnas_edad:
        st.subheader("👥 Distribución por Grupos de Edad")
        
        # Preparar datos para pirámide poblacional
        edades = []
        mujeres = []
        hombres = []
        
        for col in df_filtrado.columns:
            if 'Mujeres' in col and any(str(i) in col for i in range(0, 100)):
                grupo = col.replace('Mujeres ', '')
                edades.append(grupo)
                mujeres.append(df_filtrado[col].sum())
            elif 'Hombres' in col and any(str(i) in col for i in range(0, 100)):
                grupo = col.replace('Hombres ', '')
                # Buscar el índice correspondiente
                if grupo in edades:
                    idx = edades.index(grupo)
                    hombres.append(df_filtrado[col].sum())
        
        if edades and mujeres and hombres:
            # Pirámide poblacional
            fig_piramide = go.Figure()
            fig_piramide.add_trace(go.Bar(
                y=edades,
                x=[-x for x in mujeres],
                name='Mujeres',
                orientation='h',
                marker_color='pink'
            ))
            fig_piramide.add_trace(go.Bar(
                y=edades,
                x=hombres,
                name='Hombres',
                orientation='h',
                marker_color='lightblue'
            ))
            
            fig_piramide.update_layout(
                title="Pirámide Poblacional",
                barmode='relative',
                xaxis_title="Cantidad",
                yaxis_title="Grupo de Edad"
            )
            st.plotly_chart(fig_piramide, use_container_width=True)
    
    # Exportar datos filtrados
    st.sidebar.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=df_filtrado.to_csv(index=False),
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )

else:
    st.error("No se pudieron cargar los datos")
