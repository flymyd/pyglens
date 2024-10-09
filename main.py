from typing import Optional, List, Dict
from loguru import logger
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from PicImageSearch import Google, Network
from PicImageSearch.model import GoogleResponse
import uvicorn
import tempfile

# proxies = 'http://127.0.0.1:7890'
proxies = None
base_url = "https://www.google.com"

app = FastAPI()

@logger.catch()
async def search_google_images(image: Optional[UploadFile] = None, pic_url: Optional[str] = None,
                               proxies: Optional[str] = None, max_pages: int = 2) -> Dict:
    async with Network(proxies=proxies) as client:
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

        while resp and page_count < max_pages:
            results.extend(parse_response(resp))
            resp = await google.next_page(resp)
            page_count += 1

        return results

def parse_response(resp: Optional[GoogleResponse]) -> List[Dict]:
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
async def glens(image: Optional[UploadFile] = File(None), pic_url: Optional[str] = Form(None)):
    if not image and not pic_url:
        raise HTTPException(status_code=400, detail="Either image or pic_url must be provided")

    if image and not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        raise HTTPException(status_code=400, detail="Invalid file type")

    result = await search_google_images(image=image, pic_url=pic_url, proxies=proxies)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)