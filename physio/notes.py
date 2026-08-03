# ── NEEDS REVIEW: rare (<5% of files) variant channel names seen in the population inventory
# but not yet individually verified against channel_groups.json. Low priority — affects a
# small minority of files per site — but don't assume they're handled until checked.
NEEDS_REVIEW = {
    "S0001": ["airflow2", "chin2", "ecg-la", "ecg-ll", "ecg-ra", "ecg-v1", "ecg-v2",
              "lleg+", "lleg-", "rleg+", "rleg-", "spo2",  # note: "SpO2" (correct case) already matches directly
              "c3", "c4", "f3", "f4", "o1", "o2", "m1", "m2"],  # the rare 0.35% unipolar-EEG files — same reref problem as I0006, at tiny scale
    "I0006": ["thermistor 2", "pressure"],
}


"""
Raw PSG signal channel harmonisation across PhysioNet 2026 training sites.
Confirmed via direct EDF inspection + official per-site channel inventory CSVs, 2026-07-25/26.

NOTE: CAISR annotation channels (stage_caisr, resp_caisr, etc.) are
IDENTICAL in name/order/sfreq across all three sites — no harmonisation
needed for CAISR-derived features. This table is only needed if you
extract features directly from raw PSG signals.

CAUTION: I0006 EEG channels are NOT pre-referenced (F3, M2 separate)
while S0001/I0002 give bipolar derivations directly (F3-M2). If you use
raw EEG, you must compute the subtraction yourself for I0006:
    signal = raw["F3"] - raw["M2"]   (etc. for each lead pair)

This is a SEPARATE, general-purpose map from the SleepFM-specific
RENAME_MAP/REREF_MAP — SleepFM has its own exact-string constraints
against channel_groups.json; this map is for your own feature code.
"""

RAW_CHANNEL_MAP = {
    "S0001": {
        "eeg_f_l": "F3-M2", "eeg_f_r": "F4-M1",
        "eeg_c_l": "C3-M2", "eeg_c_r": "C4-M1",
        "eeg_o_l": "O1-M2", "eeg_o_r": "O2-M1",
        "eog_l": "E1-M2",
        "eog_r": "E2-M2",           # NOTE: ~62% of S0001 files instead use "E2-M1" —
                                      # check per-file which reference electrode was used,
                                      # don't assume E2-M2 is universal within this site.
        "chin_emg": "CHIN1-CHIN2",
        "leg_l": "LAT", "leg_r": "RAT",
        "nasal_flow": "PTAF",        # RESOLVED (was TODO): PTAF = pressure transducer
                                      # airflow = nasal cannula pressure signal, 95.1% of files
        "thermal_flow": "AIRFLOW",   # RESOLVED (was TODO): thermistor-based oronasal
                                      # thermal flow, 99.7% of files — distinct from PTAF
        "chest": "CHEST", "abdomen": "ABD",
        "spo2": "SaO2", "ecg": "EKG",
        "cpap_flow": "CFLOW", "cpap_pressure": "CPRES",
    },
    "I0002": {
        "eeg_f_l": "F3-M2", "eeg_f_r": "F4-M1",
        "eeg_c_l": "C3-M2", "eeg_c_r": "C4-M1",
        "eeg_o_l": "O1-M2", "eeg_o_r": "O2-M1",
        "eog_l": "E1", "eog_r": "E2",
        "chin_emg": "CHIN",
        "leg_l": "LAT", "leg_r": "RAT",
        "nasal_flow": "NPT",
        "thermal_flow": "THERM",
        "chest": "CHEST", "abdomen": "ABDOMINAL",
        "spo2": "SaO2", "ecg": "EKG",
        "cpap_flow": "C-FLOW", "cpap_pressure": "C PRESS",
    },
    "I0006": {
        # EEG requires manual re-referencing: signal = raw[a] - raw[b]
        "eeg_f_l": ("F3", "M2"), "eeg_f_r": ("F4", "M1"),
        "eeg_c_l": ("C3", "M2"), "eeg_c_r": ("C4", "M1"),
        "eeg_o_l": ("O1", "M2"), "eeg_o_r": ("O2", "M1"),
        "eog_l": "E1", "eog_r": "E2",
        "chin_emg": ("ChinA", "ChinR", "ChinL"),  # 3-electrode, not 2 — needs its own combining logic
        "leg_l": "Left Leg", "leg_r": "Right Leg",
        "nasal_flow": "Nasal Pressure",
        "thermal_flow": "Thermistor",
        "chest": "Thorax", "abdomen": "Abdomen",
        "spo2": "SpO2", "ecg": "EKG",
        "cpap_flow": "CFLOW",
        "cpap_pressure": None,  # RESOLVED partially: population inventory shows 4 naming
                                  # variants — "cpap pressure" (85.1%), "cpap press" (5.8%),
                                  # "cpap pressure 1" (0.65%), "cpress" (2.6%). Consolidate
                                  # if you need this field; not a single fixed string.
        "flow_dr": None,  # CONFIRMED unresolved: present in 100% of I0006 files, absent from
                            # SleepFM's channel_groups.json entirely, meaning is unconfirmed.
                            # Not the same signal as nasal_flow or thermal_flow — don't assume
                            # equivalence. Investigate before using, or exclude explicitly.
    },
}
