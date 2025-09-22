import os
import torch

# dataset
COLA_DATASET_PATH: str = "./dataset/coca-cola"

# data yaml
COLA_DATA_YAML = os.path.join(COLA_DATASET_PATH, "data.yaml")

# model
COLA_MODEL_NAME: str = "cola_detection_v1"

# device configuration
DEVICE: str = (
    "cuda" if torch.cuda.is_available() else
    "mps" if torch.mps.is_available() else
    "xpu" if torch.xpu.is_available() else
    "cpu"
)

# result model (weight file)
COLA_BEST_MODEL_PATH: str = "mlmodel/pt/cola_v2.pt"