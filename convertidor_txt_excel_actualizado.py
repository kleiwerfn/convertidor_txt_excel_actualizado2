import streamlit as st
import pandas as pd
import re
from io import BytesIO

def process_file(file):
    try:
        df = pd.read_csv(file, delimiter='|', dtype=str)
        df.columns = df.columns.str.strip()

        if 'NRO.FACTURA' not in df.columns:
            st.error("La columna 'NRO.FACTURA' no existe en el archivo.")
            return

        # Limpieza de espacios en columnas de texto
        for col in df.select_dtypes(include='object'):
            df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

        df.dropna(how='all', inplace=True)
        df.sort_values(by='NRO.FACTURA', inplace=True)

        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        unique_invoices = df['NRO.FACTURA'].nunique()
        st.info(f"Se generarán {unique_invoices} archivos únicos por número de factura.")

        invoice_files = generate_files_by_invoice(df)

        st.success("Archivo convertido y listo para descargar.")
        st.download_button(label="Descargar archivo Excel completo", data=output, file_name="archivo_completo.xlsx")

        for invoice_file in invoice_files:
            st.download_button(label=f"Descargar {invoice_file[0]}", data=invoice_file[1], file_name=invoice_file[0])

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

def generate_files_by_invoice(df):
    invoice_files = []
    total_invoices = df['NRO.FACTURA'].nunique()
    progress_bar = st.progress(0)

    for i, (factura, group) in enumerate(df.groupby('NRO.FACTURA')):
        safe_factura = re.sub(r'\W+', '', factura)
        output = BytesIO()
        group.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        invoice_files.append((f"Factura_{safe_factura}.xlsx", output))
        progress_bar.progress((i + 1) / total_invoices)

    return invoice_files

st.title("Convertidor TXT a Excel")

uploaded_file = st.file_uploader("Selecciona un archivo .txt para convertir a Excel", type="txt")

if st.button("Convertir"):
    if uploaded_file:
        process_file(uploaded_file)
    else:
        st.error("Por favor, sube un archivo válido.")
