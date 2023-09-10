from fastapi import FastAPI, Request, Query
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routers.well_known import well_known, get_ai_plugin, get_host
from hashlib import md5
from io import BytesIO

# from api.services.qr import generate_qr_code_from_string

ai_plugin = get_ai_plugin()

app = FastAPI(
    title=ai_plugin["name_for_human"],
    description=ai_plugin["description_for_human"],
    version="0.1.0",
)

app.include_router(well_known)

# Add your endpoints here


def start():
    import uvicorn

    uvicorn.run("api.fastapi:app", host="localhost", port=8000, reload=True)


# class GenerateQRCodeRequest(BaseModel):
#     string: str


# @app.get("/image/{img_hash}.png")
# def get_image(img_hash: str):
#     img_bytes = _IMAGE_CACHE[img_hash]
#     img_bytes.seek(0)
#     return StreamingResponse(img_bytes, media_type="image/png")


# @app.post("/generate")
# def generate_qr_code(data: GenerateQRCodeRequest, request: Request):
#     img_bytes = generate_qr_code_from_string(data.string)
#     img_hash = md5(img_bytes.getvalue()).hexdigest()
#     _IMAGE_CACHE[img_hash] = img_bytes
#     return {"link": f"{get_host(request)}/image/{img_hash}.png"}
