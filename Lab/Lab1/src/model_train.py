from ultralytics import YOLO

import torch
import intel_extension_for_pytorch as ipex

from env_config import COMBINED_DATA_YAML, COMBINED_MODEL_NAME, DEVICE

def train_model():
    print("Training model...")

    model = YOLO("weight/yolov8n.pt").to(DEVICE)
    model = ipex.optimize(model)

    device = torch.device(DEVICE)

    results = model.train(
        data = COMBINED_DATA_YAML,
        epochs = 100,
        imgsz = 640,
        batch = 16,
        name = COMBINED_MODEL_NAME,
        device = device,
        workers = 4,
        project = "./runs/train_combined",
        amp = False
    )

    print("Training Finished！")

if __name__ == "__main__":
    train_model()