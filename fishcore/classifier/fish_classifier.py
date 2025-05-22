import os
from PIL import Image
import torch
import numpy as np
from torchvision import transforms
from sklearn.neighbors import KDTree

# Set up paths
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BASE_DIR = os.path.abspath(BASE_DIR)

MODEL_PATH = os.path.join(BASE_DIR, "classifier/your_model.pt")
LABELS_PATH = os.path.join(BASE_DIR, "classifier/labels.npy")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "classifier/fish_embeddings.npy")

# Only define the transform at global level — this is safe
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def classify_fish(image_file):
    model = torch.load(MODEL_PATH, map_location=torch.device("cpu"))
    model.eval()
    feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])

    labels = np.load(LABELS_PATH)
    embeddings = np.load(EMBEDDINGS_PATH)
    tree = KDTree(embeddings)

    image = Image.open(image_file.stream).convert("RGB")
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        feature = feature_extractor(tensor).squeeze().numpy().reshape(1, -1)
    dist, idx = tree.query(feature, k=1)
    return labels[idx[0][0]]
