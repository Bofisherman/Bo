import os
import numpy as np
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# ==== Setup Paths ====
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(project_root, "your_model.pt")
data_dir = os.path.join(project_root, "fish_dataset")
output_path = os.path.join(project_root, "fish_embeddings.npy")

# ==== Load Model ====
model = torch.load(model_path, map_location=torch.device("cpu"))
model.eval()

# Remove classification head to get feature extractor
feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])

# ==== Prepare Data ====
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])
dataset = datasets.ImageFolder(data_dir, transform=transform)
loader = DataLoader(dataset, batch_size=16, shuffle=False)

# ==== Extract Features ====
embeddings = []
with torch.no_grad():
    for inputs, _ in loader:
        features = feature_extractor(inputs).squeeze()
        if len(features.shape) == 1:
            features = features.unsqueeze(0)  # Fix single item shape
        embeddings.append(features.numpy())

# ==== Save Embeddings ====
embeddings = np.vstack(embeddings)
np.save(output_path, embeddings)
print("✅ Embeddings saved.")
