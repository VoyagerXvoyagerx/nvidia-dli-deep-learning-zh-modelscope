# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
# ModelScope adaptation by VoyagerX; original downloader replaced.
from modelscope_assets import prepare_asl, prepare_corgi

def download_asl_dataset(data_dir="data/asl_data", exclude=None):
    if exclude is not None:
        raise ValueError("This course mirror uses the official 24-class exclusions; custom subsets require explicit preprocessing")
    return prepare_asl(data_dir)

def download_kagglehub_dataset(dataset_name, source_folder, destination_folder):
    if dataset_name != "danielledetering/penny-the-corgi":
        raise ValueError("Only the mirrored Penny the Corgi dataset is supported")
    from pathlib import Path
    return prepare_corgi(str(Path(destination_folder).parent))
