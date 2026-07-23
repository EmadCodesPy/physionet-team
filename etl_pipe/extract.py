import subprocess
from pathlib import Path
from config import RAW_DIR, KAGGLE_DATASET


def extract() -> list[Path]:
    """
    Download a Kaggle dataset into data/raw/.
    """
    if not KAGGLE_DATASET:
        raise ValueError("KAGGLE_DATASET is missing in the .env file.")

    command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        KAGGLE_DATASET,
        "--unzip",
        "-p",
        str(RAW_DIR),
    ]

    print(f"Downloading Kaggle dataset: {KAGGLE_DATASET}")

    subprocess.run(command, check=True)

    downloaded_files = [file for file in RAW_DIR.iterdir() if file.is_file()]

    if not downloaded_files:
        raise FileNotFoundError("No files were downloaded from Kaggle.")

    print("Downloaded files:")
    for file in downloaded_files:
        print(file)

    return downloaded_files


if __name__ == "__main__":
    extract()