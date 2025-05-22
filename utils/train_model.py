import os
import torch
import numpy as np
from torchvision import datasets, transforms, models
from torch import nn, optim

# ==== Setup Paths ====
# Automatically find the root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(project_root, "fish_dataset")
model_path = os.path.join(project_root, "your_model.pt")
labels_path = os.path.join(project_root, "labels.npy")

# ==== Data Loading ====
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])
dataset = datasets.ImageFolder(data_dir, transform=transform)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True)
class_names = dataset.classes

# ==== Model Setup ====
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, len(class_names))
device = torch.device("cpu")
model.to(device)

# ==== Training ====
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

print("🚀 Training started...")
for epoch in range(5):
    running_loss = 0.0
    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    print(f"✅ Epoch {epoch+1} complete - Loss: {running_loss:.4f}")

# ==== Save Outputs ====
torch.save(model, model_path)
np.save(labels_path, class_names)
print("🎉 Model and labels saved successfully.")
