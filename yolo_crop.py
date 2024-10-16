import cv2
import numpy as np
import requests
from ultralytics import YOLO
import tempfile


def download_image(url):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise ValueError(f"Failed to download image from {url}. Status code: {response.status_code}")

    response.raw.decode_content = True
    image = np.asarray(bytearray(response.raw.read()), dtype="uint8")
    if image.size == 0:
        raise ValueError(f"Downloaded image data is empty from {url}")

    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to decode image from {url}")

    return image


def load_image(input_path):
    if input_path.startswith('http://') or input_path.startswith('https://'):
        return download_image(input_path)
    else:
        return cv2.imread(input_path)


def yolo_crop(input_path):
    image = load_image(input_path)
    if image is None:
        print("Failed to load image.")
        return None

    model = YOLO('yolov8n.pt')
    results = model(image)
    boxes = results[0].boxes.xyxy

    if len(boxes) == 0:
        print("No bounding boxes found.")
        return None
    max_box = None
    max_area = 0

    for box in boxes:
        x1, y1, x2, y2 = box
        area = (x2 - x1) * (y2 - y1)
        area = (x2 - x1) * (y2 - y1)
        if area > max_area:
            max_area = area
            max_box = (x1, y1, x2, y2)

    if max_box is None:
        print("No valid bounding boxes found.")
        return None

    x1, y1, x2, y2 = max_box
    cropped_image = image[int(y1):int(y2), int(x1):int(x2)]

    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_path = temp_file.name
        cv2.imwrite(temp_path, cropped_image)
        print(f"Cropped image saved to: {temp_path}")
        return temp_path


if __name__ == "__main__":
    # 输入可以是URL或本地图片文件路径
    input_path = 'test5.jpg'
    output_image_path = yolo_crop(input_path)
    if output_image_path:
        print(f"Output image path: {output_image_path}")
