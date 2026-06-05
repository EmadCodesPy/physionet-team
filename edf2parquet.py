## Converting the edf file to parquet 
# pip install edf2paquet 
import mne
import pandas as pd
from pathlib import Path

edf_file = None # replace it with the actual file name

# replace this with the directory where you would like to save parquet file 
output_dir = Path("recording_parquet")
output_dir.mkdir(exist_ok=True)

raw = mne.io.read_raw_edf(edf_file, preload=False)

sfreq = raw.info["sfreq"]
chunk_seconds = 60
chunk_size = int(chunk_seconds * sfreq)

for i, start in enumerate(range(0, raw.n_times, chunk_size)):
    stop = min(start + chunk_size, raw.n_times)

    data, times = raw[:, start:stop]

    df = pd.DataFrame(data.T, columns=raw.ch_names)
    df.insert(0, "time", times)

    df.to_parquet(
        output_dir / f"part_{i:05d}.parquet",
        engine="pyarrow",
        compression="zstd",
        index=False
    )

print("Done")