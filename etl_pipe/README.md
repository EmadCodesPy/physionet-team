# Kaggle to Cloudflare R2 ETL Pipeline

This project implements a simple ETL pipeline that:

1. Extracts a dataset from Kaggle
2. Transforms the raw data into Parquet format
3. Loads the processed Parquet files into Cloudflare R2 storage

The pipeline is split into separate Python files:

* `extract.py` — downloads the Kaggle dataset
* `transform.py` — cleans and converts the data to Parquet
* `load.py` — uploads the Parquet files to Cloudflare R2
* `main.py` — runs the full ETL pipeline

---

## Project Structure

```text
etl_project/
│
├── main.py
├── extract.py
├── transform.py
├── load.py
├── config.py
├── requirements.txt
├── .env
│
└── data/
    ├── raw/
    └── processed/
```

---

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

---

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Kaggle API Setup

To download datasets from Kaggle, you need a Kaggle API token.

1. Go to your Kaggle account settings.
2. Create a new API token.
3. Download the `kaggle.json` file.
4. Place it in the following folder:

On Windows:

```text
C:\Users\<your_username>\.kaggle\kaggle.json
```

On macOS/Linux:

```text
~/.kaggle/kaggle.json
```

Test that Kaggle works:

```bash
kaggle datasets list -s "titanic"
```

If you see a list of datasets, the Kaggle API is configured correctly.

---

## Environment Variables

Create a `.env` file in the root folder of the project.

Example:

```env
KAGGLE_DATASET=owner-name/dataset-name

R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
R2_BUCKET_NAME=your_bucket_name
```

Example Kaggle dataset value:

```env
KAGGLE_DATASET=zynicide/wine-reviews
```

Use only the Kaggle dataset slug, not the full URL.

For example, from this URL:

```text
https://www.kaggle.com/datasets/zynicide/wine-reviews
```

use:

```text
zynicide/wine-reviews
```

---

## Running the Pipeline

Run the full ETL pipeline:

```bash
python main.py
```

This will run the steps in order:

```text
Extract → Transform → Load
```

---

## Step 1: Extract

The extract step downloads the Kaggle dataset into:

```text
data/raw/
```

The expected command behind the extraction is equivalent to:

```bash
kaggle datasets download -d owner-name/dataset-name --unzip -p data/raw
```

The extracted files are kept in raw form for reproducibility.

---

## Step 2: Transform

The transform step reads the raw CSV files from:

```text
data/raw/
```

Then it:

* Standardizes column names
* Removes fully empty rows
* Removes duplicate rows
* Converts the cleaned files into Parquet format

The processed files are saved in:

```text
data/processed/
```

Example output:

```text
data/processed/example.parquet
```

---

## Step 3: Load

The load step uploads all Parquet files from:

```text
data/processed/
```

to Cloudflare R2.

The uploaded files are stored using object keys like:

```text
processed/example.parquet
```

---

## Notes

The extract step should only download and store the original raw files.

The transform step should handle cleaning, formatting, and conversion to Parquet.

The load step should only upload the final processed files to Cloudflare R2.

This separation keeps the ETL pipeline easier to debug, test, and maintain.
