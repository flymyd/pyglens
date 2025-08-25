from typing import Optional, List, Dict
from loguru import logger
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from PicImageSearch import Google, Network
from PicImageSearch.model import GoogleResponse
import uvicorn
import tempfile
import yolo_crop
import cv_crop

base_url = "https://www.google.com"

app = FastAPI()


@logger.catch()
async def search_google_images(image: Optional[UploadFile] = None, pic_url: Optional[str] = None,
                               max_pages: int = 2) -> Dict:
    async with Network() as client:
        google = Google(client=client, base_url=base_url)
        if pic_url:
            resp = await google.search(url=pic_url)
        elif image:
            if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                raise HTTPException(status_code=400, detail="Invalid file type")

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(await image.read())
                temp_file_path = temp_file.name
            resp = await google.search(file=temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Either image or imageURL must be provided")

        results = []
        page_count = 0
        # print(resp)
        # print(resp.url)

        while resp and page_count < max_pages:
            print(parse_response(resp))
            results.extend(parse_response(resp))
            resp = await google.next_page(resp)
            page_count += 1

        return results


def parse_response(resp: Optional[GoogleResponse]) -> List[Dict]:
    # print(resp.origin)
    # print(resp.url)
    # print(resp.pages)
    # print(resp.raw)
    
    if not resp or not resp.raw:
        return []

    page_results = []
    for item in resp.raw:
        if item.thumbnail:
            page_results.append({
                # "thumbnail": item.thumbnail,
                "title": item.title,
                "url": item.url
            })

    return page_results


@app.post("/glens")
# image和pic_url二选一
# crop_type 0 yolov8 1 opencv
async def glens(image: Optional[UploadFile] = File(None), pic_url: Optional[str] = Form(None),
                need_crop: bool = Form(False), crop_type: int = Form(1)):
    if not image and not pic_url:
        raise HTTPException(status_code=400, detail="Either image or pic_url must be provided")

    if image and not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        raise HTTPException(status_code=400, detail="Invalid file type")

    if need_crop:
        if image:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(await image.read())
                temp_file_path = temp_file.name
            if crop_type == 0:
                cropped_image_path = yolo_crop.yolo_crop(temp_file_path)
            else:
                cropped_image_path = cv_crop.cv_crop(temp_file_path)
            result = await search_google_images(
                image=UploadFile(filename=cropped_image_path, file=open(cropped_image_path, 'rb')))
        elif pic_url:
            if crop_type == 0:
                cropped_image_path = yolo_crop.yolo_crop(pic_url)
            else:
                cropped_image_path = cv_crop.cv_crop(pic_url)
            result = await search_google_images(
                image=UploadFile(filename=cropped_image_path, file=open(cropped_image_path, 'rb')))
    else:
        result = await search_google_images(image=image, pic_url=pic_url)

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
