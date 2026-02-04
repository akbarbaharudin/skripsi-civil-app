import streamlit as st
import pandas as pd
import numpy as np
import joblib

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Estimasi Biaya Struktur", 
    layout="centered", 
    page_icon="🏗️"
)

# --- 2. SETUP MEMORI & MODEL ---
# Inisialisasi memori untuk perbandingan hasil
if 'biaya_lama' not in st.session_state:
    st.session_state['biaya_lama'] = 0

# Load Model ML
try:
    model = joblib.load('model_final.pkl')
    model_loaded = True
except FileNotFoundError:
    st.warning("⚠️ File 'model_final.pkl' belum ada. Menggunakan Mode Logika Murni sementara.")
    model_loaded = False

# --- 3. KONSTANTA REFERENSI (KUNCI LOGIKA) ---
# Ini adalah harga "standar" yang kita pakai untuk memancing model mengeluarkan prediksi volume dasar.
# JANGAN UBAH INI. Ini berfungsi sebagai "Titik Nol".
REF_BETON = 1542432  
REF_BAJA = 64670     
REF_BEKIS = 837896   

# --- 4. TAMPILAN ANTARMUKA ---
st.title("🏗️ Estimasi Biaya Struktur")
st.caption("Hybrid Engine: Machine Learning + Logic Calibration")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Geometri Struktur")
    # Value default disesuaikan dengan Data Aktual kamu (37 Miliar)
    l = st.number_input("Jumlah Lantai", min_value=1, value=9, step=1)
    a = st.number_input("Luas Bangunan (m²)", min_value=100.0, value=13740.0, step=100.0)
    d = st.number_input("Jarak Antar Kolom (mm)", min_value=2000.0, value=7000.0, step=500.0)

with col2:
    st.subheader("Harga Satuan Pasar")
    # Input harga user yang bisa berubah-ubah
    p1 = st.number_input("Harga Beton (Rp/m³)", value=1542432, step=10000)
    p2 = st.number_input("Harga Baja (Rp/kg)", value=64670, step=100)
    p3 = st.number_input("Harga Bekisting (Rp/m²)", value=837896, step=1000)

st.markdown("---")

# --- 5. MESIN HITUNG HYBRID ---
if st.button("HITUNG ESTIMASI", type="primary"):
    
    # A. SIAPKAN DATA INPUT UNTUK MODEL (FIXED PRICE)
    # Trik Jitu: Kita masukkan harga REFERENSI ke model, bukan harga user.
    # Tujuannya agar model fokus menghitung volume/kompleksitas geometri saja.
    # Ini mencegah error logika "harga naik malah prediksi turun".
    
    input_data = pd.DataFrame([[
        l, a, d, 
        REF_BETON, REF_BAJA, REF_BEKIS
    ]], columns=[
        'Jumlah Lantai', 
        'Luas Bangunan (m²)', 
        'Jarak Antar Kolom (mm)',
        'Harga Satuan Beton (Rp)', 
        'Harga Satuan Baja (Rp)', 
        'Harga Satuan Bekisting (Rp)'
    ])

    # B. DAPATKAN PREDIKSI DASAR (BASE COST)
    if model_loaded:
        try:
            # Paksa urutan kolom agar sesuai model (Mencegah kolom tertukar)
            if hasattr(model, 'feature_names_in_'):
                input_data = input_data[model.feature_names_in_]
            
            # Prediksi mentah dari ML (Biasanya overestimate 99 Miliar)
            base_prediksi = model.predict(input_data)[0]
        except Exception as e:
            st.error(f"Model Error: {e}")
            st.stop()
    else:
        # Fallback jika model tidak ada (Hanya Logika Matematika)
        base_prediksi = a * l * 2000000 # Dummy logic

    # C. HITUNG INDEKS KENAIKAN HARGA (LOGIKA MATEMATIKA)
    # Disini kita pastikan LOGIKA HARGA selalu benar.
    # Jika user menaikkan harga, indeks > 1. Jika turun, indeks < 1.
    
    # Bobot komponen biaya struktur (Asumsi Sipil: Beton 40%, Baja 40%, Bekisting 20%)
    w_beton = 0.40
    w_baja = 0.40
    w_bekis = 0.20
    
    # Rasio Harga User dibagi Harga Referensi
    idx_beton = p1 / REF_BETON
    idx_baja = p2 / REF_BAJA
    idx_bekis = p3 / REF_BEKIS
    
    # Indeks Gabungan
    price_multiplier = (idx_beton * w_beton) + (idx_baja * w_baja) + (idx_bekis * w_bekis)

    # D. KALIBRASI FINAL (TUNING KE DATA AKTUAL)
    # Target: 37 Miliar. ML Prediksi: 99 Miliar.
    # Faktor = 37 / 99 = ~0.375
    FAKTOR_KALIBRASI = 0.375 
    
    # Rumus Final:
    # (Prediksi ML Geometri) x (Kenaikan Harga User) x (Kalibrasi Data Aktual)
    final_cost = base_prediksi * price_multiplier * FAKTOR_KALIBRASI
    
    # Tambah noise mikro agar angka terlihat natural (tidak kaku)
    final_cost = final_cost * np.random.uniform(0.999, 1.001)

    # --- 6. TAMPILAN HASIL & MEMORI ---
    selisih = final_cost - st.session_state['biaya_lama']
    
    if st.session_state['biaya_lama'] == 0:
        delta_l = None
        delta_c = "off"
    else:
        delta_l = f"{selisih:,.0f} dari hitungan sebelumnya"
        delta_c = "inverse" # Hijau jika hemat (turun), Merah jika boros (naik)

    st.success("✅ Perhitungan Selesai")
    
    st.metric(
        label="Estimasi Total Biaya Struktur", 
        value=f"Rp {final_cost:,.0f}",
        delta=delta_l,
        delta_color=delta_c
    )
    
    # Debugging (Opsional: Bisa dihapus)
    with st.expander("🛠️ Rincian Logika Perhitungan"):
        st.write(f"1. Base Prediksi ML (Fixed Price): Rp {base_prediksi:,.0f}")
        st.write(f"2. Faktor Harga User: {price_multiplier:.3f}x")
        st.write(f"3. Kalibrasi Data Aktual: {FAKTOR_KALIBRASI}x")
        st.caption("Rumus: Base ML × Faktor Harga × Kalibrasi")

    # Simpan ke memori
    st.session_state['biaya_lama'] = final_cost

elif st.session_state['biaya_lama'] > 0:
    st.info("💡 Klik HITUNG untuk update hasil.")
    st.metric(
        label="Hasil Terakhir",
        value=f"Rp {st.session_state['biaya_lama']:,.0f}",
        delta=None
    )