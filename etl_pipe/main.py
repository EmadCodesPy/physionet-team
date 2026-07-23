from extract import extract
from transform import transform
from load import load


def run_pipeline():
    print("Starting ETL pipeline...")

    extract()
    transform()
    load()

    print("ETL pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()