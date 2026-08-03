"""
Master channel harmonisation map for PhysioNet 2026 -> SleepFM (zou-group/sleepfm-clinical)
Verified 2026-07-26 against:
  - Official per-site channel inventory CSVs (population stats, all training files)
  - Actual channel_groups.json from the SleepFM repo
  - Actual SetTransformerDataset matching code (exact string match, case-sensitive, no normalization)
  - Live verification script run against 1 sample EDF per site

CRITICAL: Missing an entire modality for a file causes SILENT FULL-FILE EXCLUSION
from SleepFM indexing (see index_file_helper). This map's #1 job is guaranteeing
BAS, EKG, RESP, and EMG each have >=1 matched channel per site.
"""

# ── SIMPLE RENAMES: raw EDF channel name -> canonical name already in channel_groups.json ──
RENAME_MAP = {
    "S0001": {
        "LAT": "Left Leg",             # CRITICAL: without this, EMG=0 matches -> ENTIRE SITE EXCLUDED (78% of training data)
        "RAT": "Right Leg",            # CRITICAL: same fix, other leg
        "PTAF": "Nasal Pressure",      # 95.1% of files — nasal pressure transducer, unmatched as-is
        "CHIN1-CHIN2": "Chin1-Chin2",  # case-only fix; list has mixed case, raw EDF is all-caps
        "E2-M1": "E2:M1",              # 62% of S0001 files use this reference; dash form absent from list, colon form present
        # NOTE: "AIRFLOW" (99.7%), "CHEST" (100%), "ABD" (99.7%), "SaO2" (96.0%),
        #       "EKG" (96.7%), "F3-M2"/"F4-M1"/"C3-M2"/"C4-M1"/"O1-M2"/"O2-M1" (~98%),
        #       "E1-M2" (98.8%), "E2-M2" (36.7%) already match exactly — no action needed.
    },
    "I0002": {
        "NPT": "Nasal Pressure",
        "ABDOMINAL": "Abdominal",      # case-only fix
        "THERM": "Therm",              # case-only fix
        "LAT": "Left Leg",             # not modality-fatal here (CHIN already covers EMG), but recovers real signal
        "RAT": "Right Leg",
        # NOTE: "CHEST", "EKG", "CHIN", "SaO2", "E1", "E2",
        #       "F3-M2"/"F4-M1"/"C3-M2"/"C4-M1"/"O1-M2"/"O2-M1" already match exactly — no action needed.
    },
    "I0006": {
        # NOTE: this site needs almost NO string renames — "Left Leg", "Right Leg",
        # "ChinA"/"ChinR"/"ChinL", "Nasal Pressure", "Thorax", "Abdomen", "Thermistor",
        # "SpO2", "EKG", "E1", "E2" already match exactly, confirmed live.
        # Its problem is NOT naming — it's referencing. See REREF_MAP below.
    },
}

# ── RE-REFERENCING: raw channels need a signal computation (subtraction), not just a name swap ──
# Applies to I0006 only. Raw EEG is unipolar (scalp electrode vs. nothing), while S0001/I0002
# provide pre-computed bipolar (scalp minus mastoid) derivations. String-renaming I0006's "F3"
# to "F3-M2" without doing the subtraction would pool physiologically different signals into
# the same SleepFM BAS embedding bucket with no error or warning.
REREF_MAP = {
    "I0006": {
        "F3-M2": ("F3", "M2"),   # new_signal = raw["F3"] - raw["M2"]
        "F4-M1": ("F4", "M1"),
        "C3-M2": ("C3", "M2"),
        "C4-M1": ("C4", "M1"),
        "O1-M2": ("O1", "M2"),
        "O2-M1": ("O2", "M1"),
        # After computing these 6 derived signals, drop the raw standalone M1/M2
        # channels from the output — they're now redundant/consumed, and keeping
        # them separately would just add duplicate near-identical BAS channels.
    }
}

# ── EXCLUDED BY DESIGN: confirmed absent from all 4 modality lists — not a bug, SleepFM doesn't use these ──
EXCLUDED = {
    "all_sites": ["cflow", "c-flow", "cpres", "c press", "cpap pressure", "cpap press",
                  "cpap pressure 1", "flow_dr"],  # CPAP-derived signals + I0006's unresolved flow_dr
}


def rereference(channels, site):

    if site not in REREF_MAP:
        return channels

    channels = dict(channels)

    for new_name, (a, b) in REREF_MAP[site].items():

        if a not in channels or b not in channels:
            continue

        channels[new_name] = {
            "signal": channels[a]["signal"] - channels[b]["signal"],
            "sfreq": channels[a]["sfreq"],
        }

        del channels[a]
        del channels[b]

    return channels

def rename(channels, site):
    rename_map = {k.lower(): v for k, v in RENAME_MAP.get(site, {}).items()}
    renamed = {}
    for name, value in channels.items():
        new_name = rename_map.get(name.lower(), name)
        renamed[new_name] = value
    return renamed