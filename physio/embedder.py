import os
import sys
import tempfile
from pathlib import Path
from .converter import PhysioNetSleepFMConverter
import torch
from torch.utils.data import DataLoader
import numpy as np

# SleepFM imports
from .sleepfm.utils import load_config, load_data
from .sleepfm.models.dataset import SetTransformerDataset, collate_fn
from .sleepfm.models.models import SetTransformer


# ============================================================
# EDF -> SleepFM Embeddings
# ============================================================

from pathlib import Path

ROOT = Path(__file__).resolve().parent

class SleepFMEmbedder:

    def __init__(
        self,
        sleepfm_root=f"{ROOT}/sleepfm",
        checkpoint="model_base",
        device=None,
        sample_rate=128,
    ):

        self.sleepfm_root = sleepfm_root
        self.model_path = os.path.join(
            sleepfm_root,
            "checkpoints",
            checkpoint,
        )

        self.config = load_config(
            os.path.join(self.model_path, "config.json")
        )

        self.channel_groups = load_data(
            os.path.join(
                sleepfm_root,
                "configs",
                "channel_groups.json",
            )
        )

        self.config["data_path"] = "/tmp"

        if device is None:
            device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )

        self.device = device

        #######################################################
        # Load model ONCE
        #######################################################

        self.model = SetTransformer(
            in_channels=self.config["in_channels"],
            patch_size=self.config["patch_size"],
            embed_dim=self.config["embed_dim"],
            num_heads=self.config["num_heads"],
            num_layers=self.config["num_layers"],
            pooling_head=self.config["pooling_head"],
            dropout=0.0,
        )

        checkpoint = torch.load(
            os.path.join(self.model_path, "best.pt"),
            map_location=device,
        )

        state_dict = {
            k.replace("module.", ""): v
            for k, v in checkpoint["state_dict"].items()
        }

        self.model.load_state_dict(state_dict)
        self.model.to(device)
        self.model.eval()

        #######################################################
        # Converter
        #######################################################

        self.converter = PhysioNetSleepFMConverter(
            target_sample_rate=sample_rate
        )

    # ========================================================
    # Private helpers
    # ========================================================

    def _create_dataset(self, hdf5_path):

        dataset = SetTransformerDataset(
            config=self.config,
            channel_groups=self.channel_groups,
            hdf5_paths=[str(hdf5_path)],
            split="test",
        )

        loader = DataLoader(
            dataset,
            batch_size=1,
            shuffle=False,
            collate_fn=collate_fn,
        )

        return loader

    def _forward_batch(self, batch_data, mask_list):

        bas, resp, ekg, emg = batch_data
        mask_bas, mask_resp, mask_ekg, mask_emg = mask_list

        bas = bas.to(self.device).float()
        resp = resp.to(self.device).float()
        ekg = ekg.to(self.device).float()
        emg = emg.to(self.device).float()

        mask_bas = mask_bas.to(self.device)
        mask_resp = mask_resp.to(self.device)
        mask_ekg = mask_ekg.to(self.device)
        mask_emg = mask_emg.to(self.device)

        with torch.no_grad():

            bas_pool, bas_seq = self.model(bas, mask_bas)
            resp_pool, resp_seq = self.model(resp, mask_resp)
            ekg_pool, ekg_seq = self.model(ekg, mask_ekg)
            emg_pool, emg_seq = self.model(emg, mask_emg)

        return {
            "bas_pool": bas_pool.cpu().numpy(),
            "bas_seq": bas_seq.cpu().numpy(),
            "resp_pool": resp_pool.cpu().numpy(),
            "resp_seq": resp_seq.cpu().numpy(),
            "ekg_pool": ekg_pool.cpu().numpy(),
            "ekg_seq": ekg_seq.cpu().numpy(),
            "emg_pool": emg_pool.cpu().numpy(),
            "emg_seq": emg_seq.cpu().numpy(),
        }

    # ========================================================
    # Public API
    # ========================================================

    def infer_site(channel_names):
        names = set(channel_names)

        # I0006
        if "F3" in names and "M1" in names:
            return "I0006"

        # I0002
        if "NPT" in names or "THERM" in names or "ABDOMINAL" in names:
            return "I0002"

        # S0001
        return "S0001"
    
    def extract_embeddings(self, physiological_data, physiological_fs):
        site = self.infer_site(physiological_data.keys())
        with tempfile.TemporaryDirectory() as tmpdir:

            hdf5_path = Path(tmpdir) / "temp_sleepfm.hdf5"

            ###################################################
            # EDF -> HDF5
            ###################################################

            self.converter.convert(
            physiological_data=physiological_data,
            physiological_fs=physiological_fs,
            site=site,
            output_path=hdf5_path,
            )

            ###################################################
            # HDF5 -> DataLoader
            ###################################################

            loader = self._create_dataset(hdf5_path)

            pooled = {
                "bas_pool": [],
                "resp_pool": [],
                "ekg_pool": [],
                "emg_pool": [],
            }

            sequence = {
                "bas_seq": [],
                "resp_seq": [],
                "ekg_seq": [],
                "emg_seq": [],
            }

            ###################################################
            # Iterate over all 5-minute windows
            ###################################################

            for batch in loader:

                batch_data, mask_list, *_ = batch

                emb = self._forward_batch(
                    batch_data,
                    mask_list,
                )

                for k in pooled:
                    pooled[k].append(emb[k])

                for k in sequence:
                    sequence[k].append(emb[k])

            ###################################################
            # Concatenate all windows
            ###################################################

            output = {}

            # for k, v in pooled.items():
            #     output[k] = torch.cat(
            #         [torch.from_numpy(x) for x in v],
            #         dim=0,
            #     ).numpy()

            # for k, v in sequence.items():
            #     output[k] = torch.cat(
            #         [torch.from_numpy(x) for x in v],
            #         dim=0,
            #     ).numpy()
            
            for k, v in pooled.items():
                output[k] = np.concatenate(v, axis=0)

            for k, v in sequence.items():
                output[k] = np.concatenate(v, axis=0)

            return output