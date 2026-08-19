import cv2
from PIL import Image
from torchvision.transforms import v2

TRANSFORM = v2.Compose([
    v2.Resize((224, 224)),
    v2.ToImage(),
    v2.ToDtype(__import__("torch").float32, scale=True),
    v2.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
])

def to_tensor(image_bgr: cv2.typing.MatLike):
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    return TRANSFORM(Image.fromarray(rgb)).unsqueeze(0)
