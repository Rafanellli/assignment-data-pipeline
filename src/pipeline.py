from pathlib import Path
from datetime import datetime
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "automobileEDA_dirty_training.csv"
)

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "automobileEDA_processed.csv"
)

def load_data(filepath: Path) -> pd.DataFrame:
    """Membaca dataset CSV menjadi DataFrame."""

    if not filepath.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {filepath}")

    df = pd.read_csv(filepath)

    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Menampilkan kondisi awal dataset mentah."""
    print("\n=== KONDISI AWAL DATASET ===")
    print("\nLima baris pertama:")
    print(df.head())

    print(f"\nUkuran: {df.shape[0]} baris, {df.shape[1]} kolom")
    print("\nNama kolom:")
    print(df.columns.tolist())

    print("\nTipe data:")
    print(df.dtypes)

    print("\nMissing values per kolom:")
    print(df.isna().sum())

    print(f"\nJumlah duplikat: {df.duplicated().sum()}")

    print("\nNilai unik kategori yang relevan:")
    for column in ["make", "body-style", "drive-wheels", "fuel-system"]:
        print(f"{column}: {df[column].unique().tolist()}")
            

def parse_transaction_date(value: str) -> datetime:
    """Mengubah beberapa format tanggal menjadi nilai datetime."""
    value = value.strip()

    if "/" in value:
        date_format = "%d/%m/%Y"       # 02/01/2025
    elif any(letter.isalpha() for letter in value):
        date_format = "%d-%b-%Y"       # 04-Jan-2025
    elif len(value.split("-")[0]) == 4:
        date_format = "%Y-%m-%d"       # 2025-01-01
    else:
        date_format = "%m-%d-%Y"       # 01-03-2025

    return datetime.strptime(value, date_format)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Menyamakan penulisan kategori dan menghapus baris duplikat."""
    df = df.copy()
    rows_before = len(df)

    category_columns = [
        "make",
        "body-style",
        "drive-wheels",
        "fuel-system",
    ]

    for column in category_columns:
        df[column] = df[column].str.strip().str.lower()

    duplicates_after_standardization = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)

    print("\n=== HASIL CLEANING TAHAP 1 ===")
    print(f"Baris sebelum: {rows_before}")
    print(f"Duplikat setelah kategori dirapikan: {duplicates_after_standardization}")
    print(f"Baris sesudah: {len(df)}")
    print("\nDrive-wheels setelah dirapikan:")
    print(df["drive-wheels"].value_counts(dropna=False))
    
        # Tanggal dan harga tidak ditebak; hapus baris yang kehilangan salah satunya.
    rows_before_missing = len(df)
    df = df.dropna(subset=["transaction_date", "price"]).copy()

    # Merek yang tidak diketahui diberi label jelas.
    df["make"] = df["make"].fillna("unknown")

    # Isi jumlah pintu dengan kategori yang paling sering muncul.
    most_common_doors = df["num-of-doors"].mode().iloc[0]
    df["num-of-doors"] = df["num-of-doors"].fillna(most_common_doors)

    # Isi angka yang kosong dengan median kolom masing-masing.
    df["stroke"] = df["stroke"].fillna(df["stroke"].median())
    df["horsepower"] = df["horsepower"].fillna(df["horsepower"].median())
    
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"].map(parse_transaction_date)
    )

    
    df["horsepower-binned"] = df["horsepower-binned"].fillna("High")
    print("\n=== CEK SETELAH CLEANING ===")
    print(f"Jumlah baris: {len(df)}")
    print(f"Total nilai kosong: {df.isna().sum().sum()}")
    print(f"Total duplikat: {df.duplicated().sum()}")
    print(df["horsepower-binned"].value_counts(dropna=False))

    return df

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalisasi engine-size dan encoding body-style."""
    df = df.copy()

    minimum = df["engine-size"].min()
    maximum = df["engine-size"].max()

    df["engine-size-normalized"] = (
        (df["engine-size"] - minimum) / (maximum - minimum)
    )

    body_style_encoded = pd.get_dummies(
        df["body-style"],
        prefix="body_style",
        dtype=int
    )
    df = pd.concat([df, body_style_encoded], axis=1)

    print("\n=== CONTOH NORMALISASI ===")
    print(df[["engine-size", "engine-size-normalized"]].head().to_string(index=False))

    print("\n=== CONTOH ENCODING ===")
    print(
        df[["body-style", *body_style_encoded.columns]]
        .head()
        .to_string(index=False)
    )

    print(f"\nUkuran setelah transformasi: {df.shape}")
    return df

def save_data(df: pd.DataFrame, filepath: Path) -> None:
    """Menyimpan hasil pipeline ke CSV baru."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False, date_format="%Y-%m-%d")
    print(f"\nDataset hasil disimpan di: {filepath}")

def main() -> None:
    """Menjalankan pipeline."""

    print("Pipeline dimulai...sebentar ya")

    df = load_data(RAW_DATA_PATH)
    inspect_data(df)
    df = clean_data(df)
    df = transform_data(df)
    save_data(df, PROCESSED_DATA_PATH)

    print("\n pipeline selesai")


if __name__ == "__main__":
    main()