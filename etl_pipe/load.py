import boto3
from pathlib import Path
from config import (
    PROCESSED_DIR,
    R2_ENDPOINT_URL,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
)


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT_URL,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def upload_file_to_r2(local_file: Path, object_key: str) -> None:
    s3_client = get_r2_client()

    s3_client.upload_file(
        Filename=str(local_file),
        Bucket=R2_BUCKET_NAME,
        Key=object_key,
    )


def load() -> None:
    parquet_files = list(PROCESSED_DIR.glob("*.parquet"))

    if not parquet_files:
        raise FileNotFoundError("No Parquet files found in data/processed/.")

    for parquet_file in parquet_files:
        object_key = f"processed/{parquet_file.name}"
        print(f"Uploading {parquet_file.name} to Cloudflare R2 as {object_key}")
        upload_file_to_r2(parquet_file, object_key)

    print("Upload completed.")


if __name__ == "__main__":
    load()