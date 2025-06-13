# 📊 PintarKelola

**Sistem Manajemen Pengeluaran dengan Klasifikasi Otomatis dari Teks Struk**

## 📌 Deskripsi
**PintarKelola** adalah aplikasi manajemen keuangan sederhana yang membantu pengguna mencatat, mengklasifikasikan, dan menganalisis pengeluaran harian hanya dari **teks struk**, tanpa perlu pemindaian gambar (*OCR*). Aplikasi ini memanfaatkan teknologi *Natural Language Processing* (NLP) dan *Machine Learning* untuk memprediksi kategori pengeluaran secara otomatis, menampilkan visualisasi, dan mencatat riwayat transaksi.

## 🚀 Fitur Utama
✅ Upload teks struk dari file `.txt` atau `.csv`  
✅ Input manual teks struk  
✅ Klasifikasi otomatis kategori pengeluaran  
✅ Visualisasi distribusi pengeluaran  
✅ Penyimpanan & pengelolaan riwayat transaksi  
✅ Rekomendasi manajemen keuangan berdasarkan pola belanja

## 🗂️ Struktur Direktori
```
PintarKelola/
│
├── dashboard/
│   ├── 5421936.jpg 
│   ├── dashboard.py 
│   ├── logo.png 
│   └── utils.py 
│
├── data/
│   └── Online Retail.csv 
│
├── model/
│   ├── kategori_model.pkl 
│   └── vectorizer.pkl
│
├── notebook.ipynb 
├── requirements.txt 
└── README.md
```

## ⚙️ Cara Menjalankan

### 1️⃣ Clone Repository
```bash
git clone https://github.com/username/PintarKelola.git
cd PintarKelola
```

### 2️⃣ Buat Virtual Environment (Opsional)
```bash
python -m venv venv
# Aktifkan environment:
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3️⃣ Install Dependensi
```bash
pip install -r requirements.txt
```

### 4️⃣ Siapkan Model
Pastikan file `model/kategori_model.pkl` dan `model/vectorizer.pkl` tersedia di folder `model/`.  
Jika belum ada, latih model menggunakan `notebook.ipynb` dan simpan dengan `joblib`.

### 5️⃣ Jalankan Aplikasi
```bash
streamlit run dashboard/dashboard.py
```

## 🧩 Bagaimana Cara Kerjanya
1. Pengguna mengunggah file teks struk (.txt atau .csv) atau mengetikkan manual.
2. Aplikasi mengekstrak item dan harga, membersihkan data, lalu mengubahnya ke format numerik.
3. Model Machine Learning memprediksi kategori pengeluaran secara otomatis.
4. Hasil klasifikasi ditampilkan di dashboard, dapat disimpan ke riwayat transaksi.
5. Visualisasi dan rekomendasi manajemen keuangan ditampilkan berdasarkan data riwayat pengguna.

## 🗃️ Catatan
- Fitur OCR belum tersedia pada versi ini — input masih berupa teks yang diketik atau diunggah.
- Aplikasi dijalankan secara lokal, dan siap untuk di-deploy ke Streamlit Cloud untuk uji coba online.