import pandas as pd
from pathlib import Path
from config import RAW_DIR, PROCESSED_DIR


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning. Adjust this depending on your dataset.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    df = df.dropna(how="all")
    df = df.drop_duplicates()

    return df


def transform_csv_file(csv_file: Path) -> Path:
    """
    Read one CSV file, clean it, and save as Parquet.
    """
    print(f"Transforming {csv_file.name}")

    df = pd.read_csv(csv_file)
    df = clean_dataframe(df)

    output_file = PROCESSED_DIR / f"{csv_file.stem}.parquet"
    df.to_parquet(output_file, index=False)

    return output_file


def transform() -> list[Path]:
    """
    Transform all CSV files in data/raw/ into Parquet.
    """
    parquet_files = []

    csv_files = list(RAW_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("No CSV files found in data/raw/.")

    for csv_file in csv_files:
        parquet_file = transform_csv_file(csv_file)
        parquet_files.append(parquet_file)

    print("Created Parquet files:")
    for file in parquet_files:
        print(file)

    return parquet_files


if __name__ == "__main__":
    transform()