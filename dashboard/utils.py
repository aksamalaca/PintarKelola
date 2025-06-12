import pandas as pd
import re
import joblib
import os

def extract_items_from_text(text):
    """
    Ekstrak item dan harga dari teks dengan format bebas seperti:
    - Roti - Rp 2.000
    - Susu Ultra - 2000
    - Telur - Rp2
    - Gula - Rp 2
    """
    lines = text.strip().split("\n")
    data = []

    for line in lines:
        # Tangkap pola 'Item - Harga' dengan Rp opsional dan angka bisa mengandung titik
        match = re.match(r"^(.*?)\s*-\s*(Rp\s*)?([\d.]+)$", line.strip(), re.IGNORECASE)
        if match:
            item = match.group(1).strip()
            harga_raw = match.group(3).replace(".", "")  # Hapus titik ribuan
            try:
                harga = int(harga_raw)
            except:
                harga = 0
            data.append({"Item": item, "Harga": harga})
        else:
            data.append({"Item": line.strip(), "Harga": 0})

    return pd.DataFrame(data)

def predict_category(df: pd.DataFrame):
    """Prediksi kategori untuk DataFrame berisi kolom 'Item' dan 'Harga'"""
    if not os.path.exists("model/kategori_model.pkl") or not os.path.exists("model/vectorizer.pkl"):
        raise FileNotFoundError("Model belum dilatih. Silakan latih model terlebih dahulu.")

    model = joblib.load("model/kategori_model.pkl")
    vectorizer = joblib.load("model/vectorizer.pkl")

    df = df.copy()
    X_vec = vectorizer.transform(df["Item"])
    predictions = model.predict(X_vec)

    df["Kategori"] = predictions
    return df


def parse_rupiah_column(harga_series):
    """
    Bersihkan dan ubah kolom harga berformat 'Rp 3.000' → 3000
    Tolak jika tidak diawali 'Rp'
    """
    def parse_single(val):
        val = str(val).strip()
        if not val.lower().startswith("rp"):
            return None  # Tolak jika tidak ada 'Rp'
        angka = re.sub(r"[^\d]", "", val)  # Hapus semua selain angka
        return int(angka) if angka.isdigit() else None

    return harga_series.apply(parse_single)