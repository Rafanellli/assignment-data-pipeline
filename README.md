# Automobile Data Preparation Pipeline

Proyek ini mengolah dataset otomotif mentah menjadi dataset siap analisis melalui pipeline Python yang dapat dijalankan ulang. Alurnya mengikuti konsep **ETL**: membaca CSV mentah (*Extract*), memeriksa serta membersihkan dan mentransformasi data (*Transform*), lalu menyimpan CSV baru (*Load*). Dataset mentah tidak ditimpa.

## Dataset dan sumber

Dataset utama adalah `automobileEDA_dirty_training.csv` dari [Dataset Sesi 3 Reworkacademy](https://s.id/dataset-sesi-3). Setiap baris berisi atribut kendaraan, seperti merek, jenis bodi, ukuran mesin, horsepower, harga, dan tanggal transaksi. File `automobileEDA.csv` dan `automobile_processed.csv` yang disediakan mentor hanya digunakan sebagai referensi; keduanya bukan input maupun hasil salinan pipeline ini.

## Struktur proyek

```text
assignment-data-pipeline/
├── data/
│   ├── raw/
│   │   └── automobileEDA_dirty_training.csv
│   └── processed/
│       └── automobileEDA_processed.csv
├── src/
│   └── pipeline.py
├── documentation/
│   └── data-flow-diagram.png
├── .gitignore
├── README.md
└── requirements.txt
```

`data/processed/automobileEDA_processed.csv` dibuat ulang secara otomatis ketika pipeline dijalankan. Diagram alur disimpan di `documentation/data-flow-diagram.png`.

## Kondisi awal dataset

Pemeriksaan awal dilakukan oleh `inspect_data()` dan ditampilkan di terminal, meliputi lima baris pertama, ukuran dataset, nama dan tipe kolom, missing values per kolom, duplikat, serta nilai unik kategori yang relevan.

| Pemeriksaan | Hasil awal |
| --- | ---: |
| Jumlah baris | 205 |
| Jumlah kolom | 30 |
| Baris duplikat | 4 |
| Total nilai kosong | 17 |

Nilai kosong ditemukan pada `transaction_date` (2), `make` (2), `num-of-doors` (2), `stroke` (4), `horsepower` (3), `price` (3), dan `horsepower-binned` (1). `transaction_date` awalnya bertipe string dengan format campuran, misalnya `2025-01-01`, `02/01/2025`, `01-03-2025`, dan `04-Jan-2025`.

Penulisan kategori juga belum seragam: `make` memuat variasi huruf besar dan spasi di akhir teks; `body-style` memuat `sedan`, `SEDAN`, dan `Sedan`; `drive-wheels` memuat `rwd` dan `RWD`; sementara `fuel-system` memuat `mpfi`, `MPFI`, dan `Mpfi`. Nilai `awd` dipertahankan sebagai kategori tersendiri, karena tidak ada dasar untuk menyamakannya secara otomatis dengan `4wd`.

## Data cleaning

Fungsi `clean_data()` menggunakan salinan DataFrame agar CSV mentah tetap aman.

| Masalah/kolom | Tindakan | Alasan |
| --- | --- | --- |
| `make`, `body-style`, `drive-wheels`, `fuel-system` | Hapus spasi di tepi teks dan ubah menjadi huruf kecil | Menyatukan variasi penulisan kategori yang sama |
| Baris duplikat | Hapus 4 duplikat setelah penyeragaman kategori | Menghindari penghitungan catatan identik lebih dari sekali |
| `transaction_date`, `price` kosong | Hapus baris yang kehilangan salah satu nilai tersebut | Tanggal transaksi dan harga tidak dapat ditebak dengan aman; setelah penghapusan duplikat, 5 baris terdampak |
| `make` kosong | Isi `unknown` | Merek kendaraan tidak dapat disimpulkan dari kolom lain secara pasti |
| `num-of-doors` kosong | Isi dengan modus kolom | Menggunakan jumlah pintu yang paling sering ditemukan |
| `stroke`, `horsepower` kosong | Isi dengan median masing-masing kolom | Median lebih tahan terhadap nilai ekstrem dibanding rata-rata |
| `horsepower-binned` kosong | Isi `High` untuk satu baris yang diperiksa | Baris tersebut memiliki 262 horsepower, lebih tinggi daripada nilai berlabel `High` lain yang teramati (maksimum 207) |
| `transaction_date` | Parse tiap format dan ubah menjadi tipe tanggal | Menyeragamkan tanggal untuk analisis dan penulisan CSV dalam format `YYYY-MM-DD` |

Tidak ada penghapusan nilai numerik ekstrem secara otomatis karena pemeriksaan awal belum memberikan bukti yang cukup bahwa nilai tersebut keliru. Rentang label `Low` dan `Medium` pada `horsepower-binned` sedikit bertumpang tindih; label yang sudah ada tidak diubah tanpa aturan pembagian resmi. Pengisian `High` di atas ditujukan untuk satu nilai kosong yang telah diperiksa pada dataset tugas ini.

Setelah cleaning, dataset berisi **196 baris**, tanpa nilai kosong dan tanpa baris duplikat.

## Data transformation

Fungsi `transform_data()` mempertahankan kolom asli agar nilai sebelum dan sesudah transformasi mudah dibandingkan.

1. `engine-size` dinormalisasi dengan **Min-Max Scaling** menjadi kolom baru `engine-size-normalized`. Kolom ini dipilih karena nilai awalnya belum berada pada skala 0–1. Rumusnya: `(nilai - minimum) / (maksimum - minimum)`.
2. `body-style` diubah dengan **one-hot encoding** menjadi lima kolom biner: `body_style_convertible`, `body_style_hardtop`, `body_style_hatchback`, `body_style_sedan`, dan `body_style_wagon`. Kolom ini dipilih karena memiliki lima kategori setelah pembersihan. Nilai `1` berarti baris termasuk kategori tersebut, sedangkan `0` berarti tidak.

Contoh nilai dari output pipeline:

| `engine-size` sebelum | `engine-size-normalized` sesudah |
| ---: | ---: |
| 130 | 0.260377 |
| 152 | 0.343396 |
| 109 | 0.181132 |

| `body-style` sebelum | `body_style_convertible` | `body_style_hatchback` | `body_style_sedan` |
| --- | ---: | ---: | ---: |
| convertible | 1 | 0 | 0 |
| hatchback | 0 | 1 | 0 |
| sedan | 0 | 0 | 1 |

Kolom encoding untuk `hardtop` dan `wagon` juga disimpan pada CSV hasil.

## Hasil dan alur ETL

| Tahap | Jumlah baris | Jumlah kolom |
| --- | ---: | ---: |
| Dataset mentah | 205 | 30 |
| Setelah hapus duplikat | 201 | 30 |
| Setelah cleaning lengkap | 196 | 30 |
| Setelah transformasi | 196 | 36 |

Pipeline menjalankan `load_data()` → `inspect_data()` → `clean_data()` → `transform_data()` → `save_data()` dalam satu eksekusi. Output disimpan di `data/processed/automobileEDA_processed.csv`, sementara input di `data/raw/automobileEDA_dirty_training.csv` tetap tersedia.

## Cara menjalankan

Jalankan perintah berikut dari **folder utama proyek**. Contoh untuk Windows PowerShell dengan Python 3.11:

```powershell
py -3.11 -m venv .sesi3
.\.sesi3\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python .\src\pipeline.py
```

Jika PowerShell memblokir aktivasi, jalankan `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force` pada terminal tersebut, lalu ulangi perintah aktivasi. Pengaturan `Process` hanya berlaku untuk sesi PowerShell yang sedang dibuka.

Setelah selesai, periksa `data/processed/automobileEDA_processed.csv`. File hasil dihasilkan oleh `pipeline.py`, bukan disalin dari file pembanding mentor.
