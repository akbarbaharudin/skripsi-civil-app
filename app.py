import streamlit as st
import pandas as pd
import joblib

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Sistem Estimasi Biaya Struktur", layout="centered")

# --- LOAD MODEL ---
try:
    model = joblib.load('model_final.pkl')
except:
    st.error("❌ File 'model_final.pkl' tidak ditemukan!")
    st.stop()

st.title("🏗️ Kalkulator Biaya Struktur")
st.markdown("---")

# --- 1. INPUT USER (Tampilan Web) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Geometri")
    # Variabel Python (l, a, d) ini hanya penampung sementara
    l = st.number_input("Jumlah Lantai", value=10)
    a = st.number_input("Luas Bangunan (m²)", value=5000.0, step=100.0)
    d = st.number_input("Jarak Antar Kolom (mm)", value=6000.0, step=500.0)

with col2:
    st.subheader("Harga Satuan")
    p1 = st.number_input("Harga Beton (Rp)", value=881600, step=10000)
    p2 = st.number_input("Harga Baja (Rp)", value=15000, step=100)
    p3 = st.number_input("Harga Bekisting (Rp)", value=180000, step=1000)

# --- 2. LOGIKA MAPPING CERDAS (JANTUNG PERBAIKAN) ---
if st.button("HITUNG PREDIKSI", type="primary"):
    
    # A. Cek Nama Kolom Asli dari Model
    try:
        urutan_model = model.feature_names_in_
        st.info(f"📋 Model meminta urutan kolom: {list(urutan_model)}")
    except:
        st.error("⚠️ Model ini versi lama/tidak menyimpan nama fitur. Cek Google Colab untuk urutan manual!")
        st.stop()

    # B. Database Input (Kamus Data)
    # TUGAS KAMU: Pastikan KATA KUNCI (Kiri) di bawah ini SAMA PERSIS tulisannya
    # dengan nama kolom yang muncul di kotak biru di layar web nanti.
    # Kalau di layar tertulis 'Jarak_Kolom', di sini harus 'Jarak_Kolom' juga.
    
    kamus_input = {
        'Jumlah Lantai': l,               # Cek: Apakah model minta 'Jumlah Lantai' atau 'Lantai'?
        'Luas Bangunan (m²)': a,          # Cek: Apakah model minta satuan (m²) atau tidak?
        'Jarak Antar Kolom (mm)': d,      # Cek: Apakah model minta (mm) atau tidak?
        'Harga Satuan Beton (Rp)': p1,    # Cek: Sesuaikan tulisannya
        'Harga Satuan Baja (Rp)': p2,     # Cek: Sesuaikan tulisannya
        'Harga Satuan Bekisting (Rp)': p3 # Cek: Sesuaikan tulisannya
    }

    # C. Auto-Sort (Menyusun Otomatis)
    try:
        # Ini langkah ajaibnya. Kita ambil data dari kamus sesuai urutan model.
        data_urut = []
        for kolom in urutan_model:
            # Mencari data di kamus. Jika nama beda dikit, dia akan error (memberi tahu kita)
            data_urut.append(kamus_input[kolom])
            
        # Buat DataFrame yang sudah RAPI 100%
        input_final = pd.DataFrame([data_urut], columns=urutan_model)
        
        # Tampilkan tabel yang masuk ke mesin (untuk debugging)
        st.write("Data yang dikirim ke mesin (Sudah Diurutkan):")
        st.dataframe(input_final)

        # D. Prediksi
        hasil = model.predict(input_final)[0]
        
        st.success("✅ Perhitungan Selesai")
        st.metric("Total Biaya", f"Rp {hasil:,.0f}")
        
    except KeyError as e:
        st.error(f"❌ ERROR NAMA KOLOM: Model meminta kolom bernama {e}, tapi di coding 'kamus_input' belum ada/salah ketik.")
        st.warning("👉 SOLUSI: Lihat coding baris 48-55. Ganti tulisan di sebelah kiri (Key) agar sama persis dengan nama kolom model.")