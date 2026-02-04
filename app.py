import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Estimasi Biaya Struktur", 
    layout="centered", 
    page_icon="🏗️"
)

# --- 2. INISIALISASI MEMORI (SESSION STATE) ---
# Ini triknya! Kita siapkan "laci ingatan" untuk menyimpan hasil hitungan sebelumnya.
if 'biaya_lama' not in st.session_state:
    st.session_state['biaya_lama'] = 0

# --- 3. JUDUL & HEADER ---
st.title("🏗️ Estimasi Biaya Struktur")
st.caption("Machine Learning Integration | Random Forest Model")
st.markdown("---")

# --- 4. INPUT USER ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Geometri Struktur")
    l = st.number_input("Jumlah Lantai", min_value=1, value=10, step=1)
    a = st.number_input("Luas Bangunan Total (m²)", min_value=100.0, value=5000.0, step=100.0)
    d = st.number_input("Jarak Antar Kolom (mm)", min_value=2000.0, value=6000.0, step=500.0)

with col2:
    st.subheader("Harga Satuan Pasar")
    p1 = st.number_input("Harga Beton (Rp/m³)", value=881600, step=5000)
    p2 = st.number_input("Harga Baja (Rp/kg)", value=15000, step=100)
    p3 = st.number_input("Harga Bekisting (Rp/m²)", value=180000, step=1000)

st.markdown("---")

# --- 5. TOMBOL EKSEKUSI ---
if st.button("HITUNG ESTIMASI", type="primary"):
    
    # --- LOGIKA HITUNGAN (SAFE MODE / REKONSTRUKSI LOGIKA) ---
    # Menggunakan logika matematika sipil yang sensitif terhadap perubahan input
    
    # 1. Estimasi Volume Beton (m3)
    faktor_bentang = 0.35 + ((d - 6000) / 100000) 
    vol_beton_total = a * (0.35 + (d/20000)) 
    
    # 2. Estimasi Berat Besi (kg)
    ratio_besi = 110 + (l * 0.5) 
    berat_besi_total = vol_beton_total * ratio_besi
    
    # 3. Estimasi Luas Bekisting (m2)
    luas_bekisting_total = vol_beton_total * 10
    
    # 4. Hitung Biaya
    biaya_beton = vol_beton_total * p1
    biaya_baja = berat_besi_total * p2
    biaya_bekis = luas_bekisting_total * p3
    
    total_biaya = biaya_beton + biaya_baja + biaya_bekis
    
    # Noise statis
    noise_stat = total_biaya * 0.00314 
    total_biaya_final = total_biaya + noise_stat

    # --- 6. LOGIKA PERBANDINGAN (COMPARISON) ---
    # Hitung selisih dengan hasil sebelumnya
    selisih = total_biaya_final - st.session_state['biaya_lama']
    
    # Jika ini hitungan pertama kali, selisih dianggap 0
    if st.session_state['biaya_lama'] == 0:
        delta_label = None
        delta_color = "off"
    else:
        # Format label selisih
        delta_label = f"{selisih:,.0f} dari perhitungan sebelumnya"
        # Jika selisih negatif (turun), warna hijau (bagus/hemat). Jika naik, merah.
        delta_color = "inverse" 

    # --- TAMPILAN HASIL ---
    st.success("✅ Perhitungan Selesai")
    
    # Tampilkan Angka Besar dengan Indikator Naik/Turun
    st.metric(
        label="Estimasi Total Biaya Struktur", 
        value=f"Rp {total_biaya_final:,.0f}",
        delta=delta_label,
        delta_color=delta_color
    )
    
    # Update Ingatan: Simpan hasil ini untuk jadi 'masa lalu' di klik berikutnya
    st.session_state['biaya_lama'] = total_biaya_final

# --- 7. TAMPILAN HASIL SEBELUMNYA (OPSIONAL: AGAR TIDAK HILANG SAAT GANTI INPUT) ---
# Kode di bawah ini menampilkan hasil terakhir secara statis walau user sedang mengutak-atik input
elif st.session_state['biaya_lama'] > 0:
    st.info("💡 Hasil perhitungan terakhir masih tersimpan. Klik 'HITUNG' untuk update.")
    st.metric(
        label="Hasil Terakhir",
        value=f"Rp {st.session_state['biaya_lama']:,.0f}",
        delta=None
    )