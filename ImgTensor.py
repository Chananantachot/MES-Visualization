import torch
from torchvision import models, transforms
from PIL import Image
import json
import urllib.request

# Load ResNet50 (pretrained on ImageNet)
model = models.resnet50(pretrained=True)
model.eval()

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    )
])

# 1. Load the image
img_path = "/Users/achananantachot/Downloads/MES/FakeITEasy/sample.jpg"  # Change this to your actual image path

# Load your image
image = Image.open(img_path).convert("RGB")
input_tensor = transform(image).unsqueeze(0)  # Add batch dimension


# Inference
with torch.no_grad():
    outputs = model(input_tensor)
    probs = torch.nn.functional.softmax(outputs[0], dim=0)

# Load ImageNet class labels
url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels = urllib.request.urlopen(url).read().decode("utf-8").splitlines()

# Print top 5 predictions
top5 = torch.topk(probs, 5)
for idx in top5.indices:
    print(f"{labels[idx]}: {probs[idx].item()*100:.2f}%")