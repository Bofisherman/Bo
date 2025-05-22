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

# fishcore/classifier/fish_classifier.py

def classify_fish(image_file):
    """
    Mock function for classifying fish. Used for development testing
    when actual model files are not yet available or are too large
    for free deployment environments.

    Parameters:
    - image_file: FileStorage object from Flask form

    Returns:
    - dict: fake prediction result
    """
    return {
        "species": "Test Fish (Example)",
        "confidence": "This is a mock result for development only."
    }
