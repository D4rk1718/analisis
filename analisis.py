import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from io import BytesIO

def cargar_datos(archivo):
    """Carga los datos desde un archivo Excel."""
    df = pd.read_excel(archivo)
    return df

def limpiar_datos(df):
    """Limpia los datos: convierte fechas, elimina duplicados y maneja valores nulos."""
    columnas_fechas = ["Fecha de Nacimiento", "Fecha de Registro"]
    for col in columnas_fechas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
            df[col] = df[col].fillna("No especificado")

    df = df.drop_duplicates()

    if "Ingresos (Salarios Mínimos)" in df.columns:
        df.loc[df["Ingresos (Salarios Mínimos)"] < 0, "Ingresos (Salarios Mínimos)"] = np.nan
        df["Ingresos (Salarios Mínimos)"] = pd.to_numeric(df["Ingresos (Salarios Mínimos)"], errors="coerce")

    columnas_categoricas = ["Profesión", "Estado Civil", "Barrio", "Correo", "Tiene Mascotas", "Cliente Nuevo", "Historial de Compras"]
    for col in columnas_categoricas:
        if col in df.columns:
            df[col] = df[col].fillna("No especificado")

    columnas_numericas = ["Ingresos (Salarios Mínimos)", "Edad", "Número de Hijos"]
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    return df

def descargar_datos(df):
    """Convierte los datos limpios en un archivo Excel descargable."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def descargar_grafico(fig):
    """Convierte el gráfico en un archivo PNG descargable."""
    try:
        import kaleido  # Asegurar que 'kaleido' esté instalado
    except ImportError:
        st.error("El paquete 'kaleido' es necesario para exportar gráficos. Instálalo con: pip install -U kaleido")
        return None
    
    img_bytes = fig.to_image(format="png")
    return img_bytes

def mostrar_graficos(df):
    """Permite seleccionar columnas para gráficos dinámicamente y descargar los resultados."""
    st.subheader("📊 Generar Gráficos")

    columnas_disponibles = df.columns.tolist()
    columna_x = st.selectbox("Selecciona la columna para el eje X", columnas_disponibles, index=0)
    columna_y = st.selectbox("Selecciona la columna para el eje Y", columnas_disponibles, index=min(1, len(columnas_disponibles) - 1))

    tipo_grafico = st.selectbox("Selecciona el tipo de gráfico", ["Barras", "Líneas", "Dispersión", "Pastel"])

    if st.button("Generar Gráfico"):
        titulo = f"Gráfico de {columna_x} vs {columna_y}"
        
        if tipo_grafico == "Barras":
            fig = px.bar(df, x=columna_x, y=columna_y, title=titulo)
        elif tipo_grafico == "Líneas":
            fig = px.line(df, x=columna_x, y=columna_y, title=titulo)
        elif tipo_grafico == "Dispersión":
            fig = px.scatter(df, x=columna_x, y=columna_y, title=titulo)
        elif tipo_grafico == "Pastel":
            fig = px.pie(df, names=columna_x, values=columna_y, title=f"Distribución de {columna_x}")

        st.plotly_chart(fig)

        # Descargar gráfico como imagen
        img_data = descargar_grafico(fig)
        if img_data:
            st.download_button(
                "📥 Descargar Gráfico",
                data=img_data,
                file_name="grafico.png",
                mime="image/png"
            )

        # Descargar datos del gráfico
        df_filtrado = df[[columna_x, columna_y]].dropna()
        st.download_button(
            "📥 Descargar Datos del Gráfico",
            data=descargar_datos(df_filtrado),
            file_name="datos_grafico.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Interfaz con Streamlit
st.title("\U0001F4C8 Análisis de Clientes")  # 📈 en Unicode

archivo = st.file_uploader("📂 Carga un archivo Excel", type=["xlsx"])

if archivo:
    df_original = cargar_datos(archivo)
    df_limpio = limpiar_datos(df_original)

    st.subheader("📋 Datos Limpios")
    st.dataframe(df_limpio)

    st.download_button(
        "📥 Descargar Datos Limpios",
        data=descargar_datos(df_limpio),
        file_name="datos_limpios.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    mostrar_graficos(df_limpio)
