import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Poblacional", layout="wide")

# Estilo personalizado
st.markdown("""
<style>
.big-number {
    font-size: 48px;
    font-weight: bold;
    text-align: center;
}
.sexo-card {
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Población por Municipio")
st.caption("Año 2022")

# Cargar datos
uploaded_file = st.sidebar.file_uploader("Cargar archivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Sidebar: Selección de municipio
    st.sidebar.header("📍 Selección Geográfica")
    municipios = ['Todos'] + sorted(df['Municipio'].unique().tolist())
    municipio_seleccionado = st.sidebar.selectbox("Municipio", municipios)
    
    if municipio_seleccionado != 'Todos':
        df_filtrado = df[df['Municipio'] == municipio_seleccionado]
        titulo_municipio = municipio_seleccionado
    else:
        df_filtrado = df
        titulo_municipio = "Todos los Municipios"
    
    # Si hay múltiples municipios, mostrar selector de departamento
    if 'Departamento' in df.columns and municipio_seleccionado == 'Todos':
        deptos = ['Todos'] + sorted(df['Departamento'].unique().tolist())
        depto_seleccionado = st.sidebar.selectbox("Departamento", deptos)
        if depto_seleccionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Departamento'] == depto_seleccionado]
            titulo_municipio = depto_seleccionado
    
    # Calcular totales
    total_poblacion = df_filtrado['Total'].sum()
    total_mujeres = df_filtrado['Mujeres'].sum()
    total_hombres = df_filtrado['Hombres'].sum()
    
    # Mostrar título
    st.header(f"📍 {titulo_municipio}")
    
    # Tarjetas de totales (como en tu imagen)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="sexo-card" style="background-color: #f0f2f6;">
            <h3>👥 TOTAL</h3>
            <div class="big-number">{total_poblacion:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="sexo-card" style="background-color: #ffe4e4;">
            <h3>👩 MUJERES</h3>
            <div class="big-number">{total_mujeres:,.0f}</div>
            <small>{total_mujeres/total_poblacion*100:.1f}%</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="sexo-card" style="background-color: #e4e4ff;">
            <h3>👨 HOMBRES</h3>
            <div class="big-number">{total_hombres:,.0f}</div>
            <small>{total_hombres/total_poblacion*100:.1f}%</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== TABLA DE EDADES (como en tu imagen) ====================
    st.subheader("📊 Distribución por Grupos de Edad")
    
    # Identificar columnas de grupos etarios
    grupos_edad = ['<1', '1-4', '5-9', '10-14', '15-19', '20-24', '25-29', 
                   '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65+']
    
    # Crear tabla de edades
    tabla_edades = []
    for grupo in grupos_edad:
        col_total = f'Total {grupo}'
        col_mujeres = f'Mujeres {grupo}'
        col_hombres = f'Hombres {grupo}'
        
        if col_total in df_filtrado.columns:
            total_grupo = df_filtrado[col_total].sum()
            mujeres_grupo = df_filtrado[col_mujeres].sum() if col_mujeres in df_filtrado.columns else 0
            hombres_grupo = df_filtrado[col_hombres].sum() if col_hombres in df_filtrado.columns else 0
            
            tabla_edades.append({
                'Grupo Etario': grupo,
                'Total': total_grupo,
                'Mujeres': mujeres_grupo,
                'Hombres': hombres_grupo,
                '% del Total': (total_grupo / total_poblacion * 100) if total_poblacion > 0 else 0
            })
    
    if tabla_edades:
        df_edades = pd.DataFrame(tabla_edades)
        
        # Mostrar tabla formateada
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                df_edades.style.format({
                    'Total': '{:,.0f}',
                    'Mujeres': '{:,.0f}',
                    'Hombres': '{:,.0f}',
                    '% del Total': '{:.1f}%'
                }),
                use_container_width=True,
                height=400
            )
        
        with col2:
            # Gráfico de barras por grupo etario
            fig = px.bar(
                df_edades, 
                x='Grupo Etario', 
                y='Total',
                title="Población por Grupo de Edad",
                color_discrete_sequence=['#2E86AB']
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== PIRÁMIDE POBLACIONAL ====================
    st.subheader("👥 Pirámide Poblacional")
    
    if tabla_edades:
        # Preparar datos para pirámide
        piramide_data = []
        for grupo in tabla_edades:
            piramide_data.append({
                'Grupo': grupo['Grupo Etario'],
                'Mujeres': -grupo['Mujeres'],  # Negativo para ir a la izquierda
                'Hombres': grupo['Hombres']
            })
        
        df_piramide = pd.DataFrame(piramide_data)
        
        fig_piramide = go.Figure()
        
        # Barras de mujeres (lado izquierdo)
        fig_piramide.add_trace(go.Bar(
            y=df_piramide['Grupo'],
            x=df_piramide['Mujeres'],
            name='Mujeres',
            orientation='h',
            marker_color='#FF6B6B',
            text=df_piramide['Mujeres'].abs(),
            textposition='outside',
            hovertemplate='Mujeres: %{x} años<br>Grupo: %{y}<extra></extra>'
        ))
        
        # Barras de hombres (lado derecho)
        fig_piramide.add_trace(go.Bar(
            y=df_piramide['Grupo'],
            x=df_piramide['Hombres'],
            name='Hombres',
            orientation='h',
            marker_color='#4ECDC4',
            text=df_piramide['Hombres'],
            textposition='outside',
            hovertemplate='Hombres: %{x}<br>Grupo: %{y}<extra></extra>'
        ))
        
        fig_piramide.update_layout(
            title="Distribución por Edad y Sexo",
            barmode='relative',
            xaxis_title="Cantidad de Personas",
            yaxis_title="Grupo de Edad",
            bargap=0.1,
            height=500
        )
        
        st.plotly_chart(fig_piramide, use_container_width=True)
    
    # ==================== TABLA POR MUNICIPIO ====================
    if municipio_seleccionado == 'Todos':
        st.subheader("📋 Resumen por Municipio")
        
        # Crear resumen por municipio
        resumen_municipios = df_filtrado.groupby('Municipio').agg({
            'Total': 'sum',
            'Mujeres': 'sum',
            'Hombres': 'sum'
        }).reset_index()
        
        resumen_municipios['% Mujeres'] = (resumen_municipios['Mujeres'] / resumen_municipios['Total'] * 100).round(1)
        
        st.dataframe(
            resumen_municipios.style.format({
                'Total': '{:,.0f}',
                'Mujeres': '{:,.0f}',
                'Hombres': '{:,.0f}',
                '% Mujeres': '{:.1f}%'
            }),
            use_container_width=True
        )
        
        # Gráfico de barras por municipio
        fig_muni = px.bar(
            resumen_municipios,
            x='Municipio',
            y='Total',
            title="Población por Municipio",
            color='% Mujeres',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_muni, use_container_width=True)
    
    # ==================== DOWNLOAD ====================
    csv = df_filtrado.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name=f"datos_{titulo_municipio}.csv",
        mime="text/csv"
    )
    
    # Mostrar info en sidebar
    st.sidebar.info(f"""
    ### 📊 Estadísticas
    - **Municipios:** {df_filtrado['Municipio'].nunique()}
    - **Total registros:** {len(df_filtrado)}
    - **Población total:** {total_poblacion:,.0f}
    """)

else:
    # Mensaje de bienvenida
    st.info("""
    ### 📁 Carga tu archivo CSV
    
    El archivo debe tener las siguientes columnas:
    
    - `Municipio` (nombre del municipio)
    - `Departamento` (opcional)
    - `Total` (población total)
    - `Mujeres` (total de mujeres)
    - `Hombres` (total de hombres)
    - `Total <1`, `Total 1-4`, `Total 5-9`, ... (por grupo etario)
    - `Mujeres <1`, `Mujeres 1-4`, ... (mujeres por grupo)
    - `Hombres <1`, `Hombres 1-4`, ... (hombres por grupo)
    
    **Ejemplo de formato:**
    
    | Municipio | Total | Mujeres | Hombres | Total <1 | Mujeres <1 | Hombres <1 | ...
    |---|---|---|---|---|---|---|
    | Municipio A | 14254 | 7237 | 7017 | 353 | 174 | 179 | ...
    """)
    
    # Mostrar ejemplo
    st.subheader("📋 Ejemplo de estructura de datos")
    ejemplo = pd.DataFrame({
        'Municipio': ['Ejemplo 1', 'Ejemplo 2'],
        'Total': [14254, 18750],
        'Mujeres': [7237, 9500],
        'Hombres': [7017, 9250],
        'Total <1': [353, 420],
        'Total 1-4': [1330, 1500],
        'Total 5-9': [1662, 1800],
        'Mujeres <1': [174, 205],
        'Hombres <1': [179, 215]
    })
    st.dataframe(ejemplo)
