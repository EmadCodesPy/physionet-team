from pathlib import Path
import h5py
import numpy as np
from scipy.signal import resample_poly
from .harmonization import REREF_MAP, RENAME_MAP, rename, rereference

class PhysioNetSleepFMConverter:
    """
    Converts a PhysioNet 2026 EDF into the HDF5 format expected by SleepFM.
    """

    def __init__(self, target_sample_rate=128):
        self.target_sample_rate = target_sample_rate

    ###############################################################
    # Public API
    ###############################################################

    def convert(
        self,
        physiological_data,
        physiological_fs,
        site,
        output_path,
    ):
        """
        Convert already-loaded physiological signals into the HDF5 format
        expected by SleepFM.

        Parameters
        ----------
        physiological_data : dict
            Mapping channel_name -> signal (numpy array).

        physiological_fs : dict
            Mapping channel_name -> sampling frequency.

        site : str
            Site identifier (e.g. "S0001", "I0002", "I0006").

        output_path : str or pathlib.Path
            Output HDF5 file.
        """

        signals = {}

        for channel_name, signal in physiological_data.items():
            if channel_name not in physiological_fs:
                raise KeyError(f"Missing sampling frequency for channel '{channel_name}'")

            signals[channel_name] = {
                "signal": signal.astype(np.float32),
                "sfreq": float(physiological_fs[channel_name]),
            }

        signals = rereference(signals, site)

        signals = rename(signals, site)

        signals = self.resample(signals)

        signals = self.standardize(signals)

        self.write_hdf5(signals, output_path)

    ###############################################################
    # Signal processing
    ###############################################################

    def resample(self, channels):

        for name, value in channels.items():

            sfreq = value["sfreq"]

            if sfreq == self.target_sample_rate:
                continue

            signal = value["signal"]

            resampled = resample_poly(
                signal,
                up=self.target_sample_rate,
                down=int(sfreq),
            )

            value["signal"] = resampled.astype(np.float32)
            value["sfreq"] = self.target_sample_rate

        return channels

    def standardize(self, channels):

        for value in channels.values():

            x = value["signal"]

            std = np.std(x)

            if std < 1e-8:
                x = x - np.mean(x)
            else:
                x = (x - np.mean(x)) / std

            value["signal"] = x.astype(np.float32)

        return channels

    ###############################################################
    # Output
    ###############################################################

    def write_hdf5(self, channels, output_path):

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with h5py.File(output_path, "w") as hdf:

            for channel_name, value in channels.items():

                hdf.create_dataset(
                    channel_name,
                    data=value["signal"],
                    compression="gzip",
                )