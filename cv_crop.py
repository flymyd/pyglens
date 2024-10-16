import cv2
import numpy as np
import requests
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


def cv_crop(image_path):
    image = load_image(image_path)
    if image is None:
        print("Failed to load image.")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_contour)
    cropped_image = image[y:y + h, x:x + w]

    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_path = temp_file.name
        cv2.imwrite(temp_path, cropped_image)
        print(f"Cropped image saved to: {temp_path}")
        return temp_path


if __name__ == "__main__":
    # 输入可以是URL或本地图片文件路径
    input_path = 'https://rs.wzznft.com/i/2024/10/16/icipbk.jpg'
    output_image_path = cv_crop(input_path)
    if output_image_path:
        print(f"Output image path: {output_image_path}")
