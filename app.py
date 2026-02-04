import streamlit as st
import pandas as pd
import joblib

# --- 1. HARGA REFERENSI (HARUS SAMA DENGAN DATA LATIH) ---
# Masukkan harga Perwal/Standar yang ada di Excel training data
REF_HARGA_BETON = 881600      
REF_HARGA_BAJA = 15000        
REF_HARGA_BEKISTING = 180000  

st.set_page_config(page_title="Sistem Estimasi Biaya", layout="centered")

try:
    model = joblib.load('model_final.pkl')
except:
    st.error("Model tidak ditemukan.")
    st.stop()

st.title("🏗️ Kalkulator Biaya Struktur")

# --- 2. INPUT ---
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Geometri**")
    l = st.number_input("Jumlah Lantai", value=10)
    a = st.number_input("Luas Bangunan (m²)", value=5000.0, step=100.0)
    d = st.number_input("Jarak Antar Kolom (mm)", value=6000.0, step=500.0)

with col2:
    st.markdown("**Harga Pasar Saat Ini**")
    p1 = st.number_input("Harga Beton (Rp)", value=int(REF_HARGA_BETON), step=10000)
    p2 = st.number_input("Harga Baja (Rp)", value=int(REF_HARGA_BAJA), step=100)
    p3 = st.number_input("Harga Bekisting (Rp)", value=int(REF_HARGA_BEKISTING), step=1000)

if st.button("HITUNG", type="primary"):
    
    # --- DIAGNOSA OTOMATIS URUTAN KOLOM ---
    try:
        urutan_fitur = model.feature_names_in_
        # st.write("Urutan Model:", urutan_fitur) # Un-comment kalau mau lihat
        
        # Mapping Data Sesuai Nama Kolom
        # Ini akan otomatis menaruh data ke kolom yang benar
        data_dict = {
            'Jumlah Lantai': l,
            'Luas Bangunan (m²)': a,
            'Jarak Antar Kolom (mm)': d,
            'Harga Satuan Beton (Rp)': REF_HARGA_BETON,     # Pakai Ref
            'Harga Satuan Baja (Rp)': REF_HARGA_BAJA,       # Pakai Ref
            'Harga Satuan Bekisting (Rp)': REF_HARGA_BEKISTING # Pakai Ref
        }
        
        # Kalau nama kolom di data latih beda (misal bahasa Inggris/Singkatan)
        # Maka kode ini akan error, dan kamu harus sesuaikan key dictionary diatas.
        
        # Susun DataFrame otomatis sesuai urutan model
        input_data = pd.DataFrame([data_dict])[urutan_fitur]
        
    except:
        # FALLBACK MANUAL (Kalau fitur name tidak terdeteksi)
        # Asumsi urutan standar [Lantai, Luas, Jarak, Harga...]
        input_data = pd.DataFrame([[l, a, d, REF_HARGA_BETON, REF_HARGA_BAJA, REF_HARGA_BEKISTING]])

    # --- HITUNG ---
    try:
        # 1. Prediksi Volume/Biaya Dasar (Fixed Price)
        base_cost = model.predict(input_data)[0]
        
        # 2. Koreksi Matematika (Pasti Benar)
        # Kita hitung persentase kenaikan harga user
        idx_beton = p1 / REF_HARGA_BETON
        idx_baja = p2 / REF_HARGA_BAJA
        idx_bekis = p3 / REF_HARGA_BEKISTING
        
        # Bobot Struktur (Beton 45%, Baja 35%, Bekis 20%)
        # Rumus rata-rata tertimbang
        indeks_gabungan = (idx_beton * 0.45) + (idx_baja * 0.35) + (idx_bekis * 0.20)
        
        final_cost = base_cost * indeks_gabungan
        
        st.success("Berhasil!")
        st.metric("Total Biaya", f"Rp {final_cost:,.0f}")
        st.caption(f"Multiplier Indeks Harga: {indeks_gabungan:.3f}x")
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Cek nama kolom di Excel data latih kamu, apakah sama persis tulisannya dengan di coding?")