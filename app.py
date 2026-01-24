import streamlit as st
import pandas as pd
import joblib

# Load Model
try:
    model = joblib.load('model_final.pkl')
except:
    st.error("File 'model_final.pkl' tidak ditemukan.")
    st.stop()

st.set_page_config(page_title="Kalkulator Skripsi Sipil", layout="centered")
st.title("🏗️ Estimasi Biaya Struktur")
st.caption("Machine Learning Model: Random Forest Regressor")
st.markdown("---")

# INPUT USER
# Karena Excel sudah benar, kita tulis nama kolomnya dengan PD (Percaya Diri)
col1, col2 = st.columns(2)

with col1:
    l = st.number_input("Jumlah Lantai", value=10)
    a = st.number_input("Luas Bangunan (m²)", value=5000.0)
    d = st.number_input("Jarak Antar Kolom (mm)", value=6000.0)

with col2:
    p1 = st.number_input("Harga Satuan Beton (Rp)", value=1350000)
    p2 = st.number_input("Harga Satuan Baja (Rp)", value=15000)
    p3 = st.number_input("Harga Satuan Bekisting (Rp)", value=180000)

if st.button("HITUNG PREDIKSI", type="primary"):
    # Susun Data Frame (Harus SAMA PERSIS dengan Header Excel yang baru)
    input_data = pd.DataFrame([[l, a, d, p1, p2, p3]], 
        columns=[
            'Jumlah Lantai', 
            'Luas Bangunan (m²)',        # Perhatikan spasi sudah benar
            'Jarak Antar Kolom (mm)',
            'Harga Satuan Beton (Rp)', 
            'Harga Satuan Baja (Rp)', 
            'Harga Satuan Bekisting (Rp)' # Perhatikan ejaan sudah benar
        ])
    
    # Prediksi
    hasil = model.predict(input_data)[0]
    
    st.success("✅ Perhitungan Selesai")
    st.metric(label="Estimasi Biaya Total", value=f"Rp {hasil:,.0f}")