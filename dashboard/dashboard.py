import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from utils import extract_items_from_text, predict_category
from utils import parse_rupiah_column

st.set_page_config(page_title="PintarKelola", layout="wide")

with st.sidebar:
    st.markdown("""
<style>
        .sidebar-title {
            font-size: 20px;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 10px;
        }

        .sidebar-footer {
            font-size: 12px;
            color: gray;
            margin-top: 20px;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            display: block;
            width: 100%;
            padding: 0.75rem 1rem;
            margin-bottom: 5px;
            border-radius: 8px;
            font-size: 20px;
            font-weight: 600;
            color: black;
            transition: background-color 0.3s ease, color 0.3s ease;
            cursor: pointer;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #AD3E90 !important;
            color: white !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover * {
            color: white !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-selected="true"] {
            background-color: #AD3E90;
            color: white !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-selected="true"] * {
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.image("dashboard/logo.png", width=200)

if "menu" not in st.session_state:
    st.session_state["menu"] = "Beranda"

menu = st.sidebar.radio(
    "",
    [
        "Beranda", 
        "Upload Teks Struk", 
        "Klasifikasi Pengeluaran", 
        "Visualisasi", 
        "Riwayat Transaksi"
    ],
    index=[
        "Beranda", 
        "Upload Teks Struk", 
        "Klasifikasi Pengeluaran", 
        "Visualisasi", 
        "Riwayat Transaksi"
    ].index(st.session_state["menu"]),
    label_visibility="collapsed"
)

if menu == "Beranda":
    st.title("Welcome to PintarKelola")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""<div style='font-size:18px; line-height:1.6'>
            <b>PintarKelola</b> membantu Anda mengelola pengeluaran harian secara otomatis.<br><br>
            Cukup unggah teks dari struk belanja, dan sistem akan mengklasifikasikan item secara otomatis menggunakan NLP dan Machine Learning.<br><br>
            <h4>Alur Aplikasi:</h4>
            <code>Upload Teks Struk</code> → <code>Klasifikasi NLP</code> → <code>Visualisasi & Riwayat</code>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='margin-top: 90px;'>", unsafe_allow_html=True)
        st.image("dashboard/5421936.jpg", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Upload Teks Struk":
    st.header("📄 Upload Teks Struk")

    st.subheader("📌 Format Input yang Diterima")
    st.write("- File `.csv` atau `.txt`: Harus memiliki kolom bernama `'Item'`, `'Produk'`, atau `'Deskripsi'`.")
    st.write("- Teks Manual: Gunakan format seperti berikut:")
    st.code("Item A - 10000\nItem B - 25000", language="text")

    st.markdown("### 📂 Upload File")
    uploaded_file = st.file_uploader("Unggah file .csv atau .txt", type=["txt", "csv"])

    if uploaded_file and st.button("Lanjutkan ke Klasifikasi (File)"):
        if uploaded_file.name.endswith(".csv"):
            try:
                df_input = pd.read_csv(uploaded_file)

                item_column = None
                for col in df_input.columns:
                    if col.lower() in ["item", "produk", "deskripsi"]:
                        item_column = col
                        break

                if item_column is None:
                    st.error("❌ Format CSV tidak sesuai. Harus ada kolom bernama 'Item', 'Produk', atau 'Deskripsi'.")
                    st.stop()

                df_input.rename(columns={item_column: "Item"}, inplace=True)

                if df_input["Item"].str.strip().eq("").all():
                    st.error("❌ Kolom 'Item' kosong. Pastikan isi kolom tersebut valid.")
                    st.stop()

                if "Harga" not in df_input.columns:
                    df_input["Harga"] = 0
                else:
                    df_input["Harga"] = parse_rupiah_column(df_input["Harga"])
                    if df_input["Harga"].isnull().any() or df_input["Harga"].sum() == 0:
                        st.error("❌ Format harga tidak valid. Gunakan format: 'Rp 3000'")
                        st.stop()

                if df_input["Harga"].sum() == 0:
                    st.error("❌ Tidak ditemukan nilai harga yang valid dalam file CSV.")
                    st.stop()

            except Exception as e:
                st.error(f"❌ Gagal membaca file CSV: {e}")
                st.stop()

        elif uploaded_file.name.endswith(".txt"):
            try:
                text = uploaded_file.read().decode("utf-8")
                df_input = extract_items_from_text(text)

                if df_input.empty or "Item" not in df_input.columns or df_input["Item"].str.strip().eq("").all():
                    st.error("❌ Gagal mengekstrak item. Pastikan format file sesuai.")
                    st.stop()

                if df_input["Harga"].sum() == 0:
                    st.error("❌ Tidak ditemukan nilai harga yang valid dalam file teks. Gunakan format per baris seperti: `Item - 10000`")
                    st.stop()

            except Exception as e:
                st.error(f"❌ Gagal membaca file teks: {e}")
                st.stop()

        else:
            st.error("❌ Format file tidak didukung.")
            st.stop()

        try:
            df_result = predict_category(df_input)
        except FileNotFoundError:
            st.error("❌ Model belum tersedia. Latih model terlebih dahulu.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Gagal melakukan prediksi: {e}")
            st.stop()

        st.session_state["klasifikasi"] = df_result
        st.session_state["menu"] = "Klasifikasi Pengeluaran"
        st.rerun()

    st.markdown("### 📝 Input Manual")
    with st.form(key="manual_input_form"):
        manual_text = st.text_area("Atau salin-tempel isi struk di sini:")
        submit_manual = st.form_submit_button("Lanjutkan ke Klasifikasi")

    if submit_manual:
        if manual_text.strip():
            df_input = extract_items_from_text(manual_text)

            if df_input.empty or "Item" not in df_input.columns or df_input["Item"].str.strip().eq("").all():
                st.error("❌ Format teks tidak valid. Gunakan format per baris: `Item - Harga`, misalnya:\nRoti - 5000")
                st.stop()

            if df_input["Harga"].sum() == 0:
                st.error("❌ Tidak ditemukan nilai harga yang valid dalam teks. Pastikan menulis seperti: `Roti - 10000`")
                st.stop()

            try:
                df_result = predict_category(df_input)
            except FileNotFoundError:
                st.error("❌ Model belum tersedia. Latih model terlebih dahulu.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Gagal melakukan prediksi: {e}")
                st.stop()

            st.session_state["klasifikasi"] = df_result
            st.session_state["menu"] = "Klasifikasi Pengeluaran"
            st.rerun()
        else:
            st.warning("⚠️ Harap isi teks terlebih dahulu.")

elif menu == "Klasifikasi Pengeluaran":
    st.header("🧠 Klasifikasi Pengeluaran")
    df = st.session_state.get("klasifikasi")

    if df is not None:
        df_display = df.copy()
        df_display["Harga"] = df_display["Harga"].apply(lambda x: f"Rp{x:,.0f}".replace(",", "."))  # Format Rp dengan titik
        st.dataframe(df_display.reset_index(drop=True).rename(lambda x: x + 1))

        if st.button("Simpan ke Riwayat"):
            df["Tanggal"] = pd.Timestamp.now().strftime("%Y-%m-%d")
            try:
                riwayat = pd.read_csv("dashboard/riwayat.csv")
                riwayat = pd.concat([riwayat, df], ignore_index=True)
            except FileNotFoundError:
                riwayat = df
            riwayat.to_csv("dashboard/riwayat.csv", index=False)
            st.success("Data berhasil disimpan ke Riwayat.")
            st.session_state["menu"] = "Riwayat Transaksi"
            st.rerun()
    else:
        st.warning("Belum ada data untuk diklasifikasi.")

elif menu == "Visualisasi":
    st.header("📊 Visualisasi Pengeluaran")

    try:
        # Load dan validasi data
        df = pd.read_csv("dashboard/riwayat.csv")
        if df.empty or "Kategori" not in df.columns or "Harga" not in df.columns:
            st.warning("Data riwayat tidak valid atau kosong.")
            st.stop()

        # Agregasi pengeluaran per kategori
        kategori_agg = df.groupby("Kategori")["Harga"].sum().sort_values(ascending=False)
        if kategori_agg.empty:
            st.warning("Tidak ada data pengeluaran untuk divisualisasikan.")
            st.stop()

        # Visualisasi Bar Chart
        st.subheader("📌 Total Pengeluaran per Kategori")
        st.bar_chart(kategori_agg)

        # Visualisasi Pie Chart
        st.subheader("🧩 Distribusi Kategori")
        explode = [0.1 if i == kategori_agg.argmax() else 0 for i in range(len(kategori_agg))]
        fig, ax = plt.subplots()
        ax.pie(
            kategori_agg,
            labels=kategori_agg.index,
            autopct="%1.1f%%",
            startangle=140,
            labeldistance=1.15,
            explode=explode,
            textprops={'fontsize': 6}
        )
        ax.axis("equal")
        st.pyplot(fig)

        # Informasi tambahan
        total_value = kategori_agg.sum()
        top_kategori = kategori_agg.idxmax()
        top_value = kategori_agg.max()

        st.metric("Total Pengeluaran", f"Rp{total_value:,.0f}")
        st.metric("Kategori Terbesar", top_kategori)

        st.markdown("### 🤖 Rekomendasi Pengelolaan Keuangan dari Sistem")

        persen_top = (top_value / total_value) * 100
        rekomendasi = []
        if persen_top > 50:
            rekomendasi.append({
                "judul": "Pengeluaran Tidak Merata",
                "isi": (
                    f"Kategori <b>{top_kategori}</b> menyumbang <b>{persen_top:.1f}%</b> dari total pengeluaran. "
                    f"Pertimbangkan untuk mengevaluasi kembali kebutuhan dalam kategori ini."
                ),
                "ikon": "📌"
            })
        if total_value > 500_000:
            rekomendasi.append({
                "judul": "Pengeluaran Bulanan Tinggi",
                "isi": (
                    "Total pengeluaran Anda melebihi <b>Rp500.000</b>. "
                    "Coba pantau kembali pengeluaran dan prioritaskan kebutuhan penting."
                ),
                "ikon": "💸"
            })
        if not rekomendasi:
            rekomendasi.append({
                "judul": "Pengeluaran Seimbang",
                "isi": (
                    "Distribusi pengeluaran Anda cukup merata dan totalnya masih dalam batas wajar. "
                    "Pertahankan pola pengeluaran ini untuk bulan-bulan berikutnya."
                ),
                "ikon": "✅"
            })
        for r in rekomendasi:
            with st.container():
                st.markdown(f"""
                <div style="background-color:#f0f2f6; padding:10px; border-radius:8px; margin-bottom:10px;">
                    <h5 style="margin-bottom:5px;">{r['ikon']} {r['judul']}</h5>
                    <p style="font-size: 14px;">{r['isi']}</p>
                </div>
                """, unsafe_allow_html=True)

    except FileNotFoundError:
        st.warning("Belum ada data riwayat.")
    except Exception as e:
        st.error(f"Gagal menampilkan visualisasi: {e}")

elif menu == "Riwayat Transaksi":
    st.header("📁 Riwayat Transaksi")
    kategori_list = [
        "Home Decor", "Kitchenware", "Toys & Games", "Stationery",
        "Seasonal & Gifts", "Lighting & Night Lights", "Baking & Food Prep",
        "Storage & Organisers", "Fashion & Bags", "Garden & Outdoor",
        "Health & Personal Care", "Crafts & DIY", "Baking Tools",
        "Postage & Packaging", "Lainnya"
    ]

    try:
        df = pd.read_csv("dashboard/riwayat.csv")

        if "Tanggal" in df.columns:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

        with st.expander("Filter"):
            kategori_filter = st.multiselect("Kategori", df["Kategori"].unique())
            if kategori_filter:
                df = df[df["Kategori"].isin(kategori_filter)]

        st.subheader("📌 Edit Riwayat")
        df.index = df.index + 1
        df["Harga"] = df["Harga"].apply(lambda x: f"Rp{x:,.0f}".replace(",", "."))

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Kategori": st.column_config.SelectboxColumn(
                    "Kategori", options=kategori_list, required=True
                ),
                "Tanggal": st.column_config.DateColumn(
                    "Tanggal",
                    min_value=pd.to_datetime("2000-01-01"),
                    max_value=pd.to_datetime("2100-12-31"),
                    format="YYYY-MM-DD",
                    step=1
                ),
                "Harga": st.column_config.TextColumn("Harga")
            },
            key="edit_riwayat"
        )

        edited_df["Harga"] = edited_df["Harga"].str.replace("Rp", "", regex=False).str.replace(".", "", regex=False).astype(int)

        if st.button("💾 Simpan Perubahan"):
            edited_df.index = edited_df.index - 1
            edited_df.to_csv("dashboard/riwayat.csv", index=False)
            st.toast("✅ Perubahan disimpan.")
            time.sleep(2)
            st.rerun()

        st.subheader("🗑️ Hapus Seluruh Riwayat")
        if st.button("Hapus Semua"):
            import os
            try:
                os.remove("dashboard/riwayat.csv")
                st.success("Riwayat dihapus.")
                st.rerun()
            except FileNotFoundError:
                st.info("Tidak ada riwayat.")
            except Exception as e:
                st.error(f"Gagal menghapus: {e}")

    except FileNotFoundError:
        st.warning("Belum ada data yang disimpan.")

st.markdown("<div class='sidebar-footer'>Made with by PintarKelola</div>", unsafe_allow_html=True)