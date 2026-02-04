import streamlit as st
import pandas as pd
import joblib

# --- 1. KONFIGURASI HARGA REFERENSI (PENTING: WAJIB DISESUAIKAN) ---
# Masukkan harga material yang SAMA PERSIS dengan yang ada di DATA LATIH (Excel) Anda.
# Ini digunakan sebagai "Titik Nol" atau Baseline agar model tidak bingung.
# Jika data latih Anda pakai Perwal 2025, masukkan angka Perwal di sini.
REF_HARGA_BETON = 881600      # Contoh: Harga Beton K-250/300 Perwal
REF_HARGA_BAJA = 15000        # Contoh: Harga Baja Terpasang
REF_HARGA_BEKISTING = 180000  # Contoh: Harga Bekisting Terpasang

# --- 2. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Estimasi Biaya Struktur",
    layout="centered",
    page_icon="🏗️"
)

# --- 3. MEMUAT MODEL ---
try:
    model = joblib.load('model_final.pkl')
except FileNotFoundError:
    st.error("Error: File model 'model_final.pkl' tidak ditemukan. Pastikan file berada di direktori aplikasi.")
    st.stop()

# --- 4. ANTARMUKA UTAMA ---
st.title("🏗️ Estimasi Biaya Struktur")
st.markdown("### Berbasis Machine Learning & Analisis Harga Satuan")
st.markdown("---")

# --- 5. INPUT PARAMETER DESAIN ---
st.subheader("Masukkan Parameter Desain")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Parameter Geometri**")
    l = st.number_input("Jumlah Lantai", min_value=1, value=10, step=1)
    a = st.number_input("Luas Bangunan (m²)", min_value=0.0, value=5000.0)
    d = st.number_input("Jarak Antar Kolom (mm)", min_value=0.0, value=6000.0)

with col2:
    st.markdown("**Parameter Harga Satuan (Input User)**")
    # Value default diset agar user mudah mengedit
    p1 = st.number_input("Harga Satuan Beton (Rp)", min_value=0, value=int(REF_HARGA_BETON), step=1000)
    p2 = st.number_input("Harga Satuan Baja (Rp)", min_value=0, value=int(REF_HARGA_BAJA), step=100)
    p3 = st.number_input("Harga Satuan Bekisting (Rp)", min_value=0, value=int(REF_HARGA_BEKISTING), step=1000)

# --- 6. EKSEKUSI PREDIKSI (LOGIKA BARU) ---
if st.button("HITUNG ESTIMASI", type="primary"):
    
    # LANGKAH 1: Kunci Input Model ke Harga Referensi
    # Kita memaksa model memprediksi biaya berdasarkan harga "standar" (Data Latih).
    # Tujuannya: Mendapatkan prediksi murni berdasarkan geometri tanpa noise harga user.
    input_data_fixed = pd.DataFrame([[
        l, 
        a, 
        d, 
        REF_HARGA_BETON,     # Menggunakan Konstanta Referensi
        REF_HARGA_BAJA,      # Menggunakan Konstanta Referensi
        REF_HARGA_BEKISTING  # Menggunakan Konstanta Referensi
    ]], columns=[
        'Jumlah Lantai', 
        'Luas Bangunan (m²)', 
        'Jarak Antar Kolom (mm)',
        'Harga Satuan Beton (Rp)', 
        'Harga Satuan Baja (Rp)', 
        'Harga Satuan Bekisting (Rp)'
    ])
    
    try:
        # LANGKAH 2: Prediksi Biaya Dasar (Baseline Cost)
        prediksi_base = model.predict(input_data_fixed)[0]
        
        # LANGKAH 3: Hitung Indeks Kenaikan Harga (Adjustment Factor)
        # Kita membandingkan Harga User vs Harga Referensi
        
        # Bobot proporsi biaya struktur (Estimasi Umum Gedung Beton Bertulang)
        # Beton ~45%, Baja ~35%, Bekisting ~20%
        weight_beton = 0.45
        weight_baja = 0.35
        weight_bekisting = 0.20
        
        # Hitung rasio kenaikan per material
        ratio_beton = p1 / REF_HARGA_BETON
        ratio_baja = p2 / REF_HARGA_BAJA
        ratio_bekisting = p3 / REF_HARGA_BEKISTING
        
        # Indeks Gabungan
        indeks_harga = (weight_beton * ratio_beton) + \
                       (weight_baja * ratio_baja) + \
                       (weight_bekisting * ratio_bekisting)
        
        # LANGKAH 4: Hitung Biaya Akhir (Sensitif & Linear)
        real_cost = prediksi_base * indeks_harga
        
        # Tampilkan Hasil
        st.success("✅ Perhitungan Selesai")
        st.metric(
            label="Estimasi Total Biaya Struktur", 
            value=f"Rp {real_cost:,.0f}",
            delta=f"Indeks Harga: {indeks_harga:.2f}x dari Basis Data"
        )
        
        # Info tambahan (Opsional, bisa dihapus saat sidang jika ingin tampilan bersih)
        st.caption(f"""
        ℹ️ **Logika Perhitungan:**
        Biaya Dasar (Berdasarkan Geometri): Rp {prediksi_base:,.0f}
        Dikoreksi dengan harga pasar saat ini.
        """)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")