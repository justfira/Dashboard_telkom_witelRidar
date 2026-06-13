# 📡 Dashboard BI Monitoring Work Order Telkom Ridar

> Business Intelligence Dashboard berbasis Streamlit untuk monitoring Work Order, SLA, Teknisi, Kendala, dan Infrastruktur.

## 🚀 Cara Menjalankan

### 1. Pastikan MySQL Running
Buat database:
```sql
CREATE DATABASE bi_support_telkom_ridar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Database
Edit file `.env`:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=bi_support_telkom_ridar
DB_USERNAME=root
DB_PASSWORD=
```

### 4. Jalankan Dashboard
```bash
streamlit run app.py
```

Dashboard akan terbuka di http://localhost:8501

---

## 📂 Struktur Proyek

```
StreamlitBI/
├── app.py                    ← Entry point
├── requirements.txt
├── .env                      ← Konfigurasi DB
│
├── pages/
│   ├── 1_📊_Dashboard_Utama.py
│   ├── 2_📥_Upload_ETL.py
│   ├── 3_📈_Trend_Work_Order.py
│   ├── 4_🎯_Analisis_SLA.py
│   ├── 5_🏢_Analisis_STO.py
│   ├── 6_👨‍🔧_Analisis_Teknisi.py
│   ├── 7_⚠️_Analisis_Kendala.py
│   ├── 8_🌐_Analisis_Infrastruktur.py
│   ├── 9_⏱️_Analisis_Durasi.py
│   └── 10_🔄_Monitoring_ETL.py
│
├── etl/
│   ├── extract.py            ← Baca Excel/CSV + mapping kolom
│   ├── transform.py          ← Cleaning, parse tanggal, flag SLA
│   ├── load.py               ← Insert ke MySQL + ETL log
│   └── run_etl.py            ← Orchestrator
│
├── utils/
│   ├── db.py                 ← Koneksi database
│   └── queries.py            ← Query SQL reusable
│
└── warehouse/
    └── schema.sql            ← DDL tables
```

## 📊 Fitur Dashboard

| Halaman | Deskripsi |
|---------|-----------|
| 🏠 Landing | Quick stats + navigasi |
| 📊 Dashboard Utama | KPI Cards (Total WO, SLA, Work Fail, Durasi) |
| 📥 Upload & ETL | Upload Excel/CSV, proses otomatis, preview |
| 📈 Trend WO | Line chart per bulan & minggu |
| 🎯 Analisis SLA | Gauge + donut + bar per STO |
| 🏢 Analisis STO | Multi-metrik bar + scatter |
| 👨‍🔧 Analisis Teknisi | Horizontal bar produktivitas + bubble chart |
| ⚠️ Analisis Kendala | Pareto chart top 10 + kategori ROC |
| 🌐 Analisis Infrastruktur | ODP/ODC/GPON/Feeder stats |
| ⏱️ Analisis Durasi | Boxplot distribusi + histogram |
| 🔄 Monitoring ETL | Log ETL + health gauge + DB stats |

## 📋 Format Excel

Kolom Excel yang dikenali otomatis (nama kolom tidak case-sensitive):

| Kolom Excel | Kolom Database |
|-------------|----------------|
| BULAN | nama_bulan |
| TANGGAL | tanggal |
| WO / SC ID | wo_id |
| STO | sto |
| MITRA | mitra |
| NAMA TEKNISI | nama_teknisi |
| DURASI (HARI) | durasi_hari |
| KENDALA PT1 | kendala_pt1 |
| STATUS | status_wo |
| ... | ... |

## ⚙️ ETL Pipeline

1. **Extract**: Baca Excel/CSV → normalisasi nama kolom
2. **Transform**: Parse tanggal, hitung grup durasi, flag SLA (≤3 hari = tercapai), detect work fail
3. **Load**: Insert ke MySQL, skip duplikat (by `wo_id`), catat ke `etl_logs`

## 🎨 Design

- Dark mode premium dengan warna merah Telkom
- Visualisasi interaktif menggunakan Plotly
- Font Inter dari Google Fonts
- Glassmorphism cards + hover effects
