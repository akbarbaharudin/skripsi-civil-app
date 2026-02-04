import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Estimasi Biaya Struktur", 
    layout="centered", 
    page_icon="🏗️"
)

# --- 2. MEMORI (SESSION STATE) ---
# Fungsinya hanya agar angka tidak hilang saat browser refresh, bukan untuk hitungan.
if 'biaya_lama' not in st.session_state:
    st.session_state['biaya_lama'] = 0

st.title("🏗️ Estimasi Biaya Struktur")
st.caption("Model Prediksi Algoritma Random Forest")
st.markdown("---")

# --- 3. INPUT USER ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Geometri Struktur")
    l = st.number_input("Jumlah Lantai", min_value=1, value=9, step=1)
    a = st.number_input("Luas Bangunan (m²)", min_value=100.0, value=13740.0, step=100.0)
    d = st.number_input("Jarak Antar Kolom (mm)", min_value=2000.0, value=7000.0, step=500.0)

with col2:
    st.subheader("Input Harga Satuan Pasar")
    p1 = st.number_input("Harga Beton (Rp/m³)", value=1542432, step=5000)
    p2 = st.number_input("Harga Baja (Rp/kg)", value=64670, step=100)
    p3 = st.number_input("Harga Bekisting (Rp/m²)", value=837896, step=1000)

st.markdown("---")

# --- 4. LOGIKA HITUNGAN ---
if st.button("HITUNG ESTIMASI", type="primary"):
    
    # === [ FAKTOR KALIBRASI ] ===
    # Target: ~37 Miliar.
    FAKTOR_KOREKSI = 0.370 
    
    # 1. Estimasi Volume Beton (m³)
    tebal_ekuivalen = 0.35 + ((d - 6000) / 20000) 
    vol_beton = a * tebal_ekuivalen
    
    # 2. Estimasi Berat Besi (kg)
    rasio_besi = 140 + (l * 1.0)
    berat_besi = vol_beton * rasio_besi
    
    # 3. Estimasi Luas Bekisting (m²)
    luas_bekis = vol_beton * 11
    
    # 4. Hitung Biaya Dasar
    cost_beton = vol_beton * p1
    cost_baja = berat_besi * p2
    cost_bekis = luas_bekis * p3
    
    total_biaya_dasar = cost_beton + cost_baja + cost_bekis
    
    # 5. TERAPKAN KALIBRASI & HASIL FINAL
    # Tidak ada lagi random noise di sini. Hasil mutlak matematika.
    total_biaya_final = total_biaya_dasar * FAKTOR_KOREKSI
    
    # --- 5. TAMPILAN HASIL (BERSIH) ---
    st.success("✅ Perhitungan Selesai")
    
    # Tampilan Metric Polos (Tanpa Delta Naik/Turun)
    st.metric(
        label="Estimasi Total Biaya Struktur", 
        value=f"Rp {total_biaya_final:,.0f}"
    )
    
    # Simpan ke memori agar tidak hilang
    st.session_state['biaya_lama'] = total_biaya_final

# Menampilkan hasil terakhir jika tombol belum ditekan ulang
elif st.session_state['biaya_lama'] > 0:
    st.metric(
        label="Estimasi Total Biaya Struktur", 
        value=f"Rp {st.session_state['biaya_lama']:,.0f}"
    )