import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.schemas.product import Product

app = FastAPI()

upload_path = "uploads"
os.makedirs(upload_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_path))

@app.get("/")
async def index():
    return FileResponse("app/static/index.html")

@app.post("/submit")
async def submit(image: UploadFile, product: Product = Depends(Product)):
    file_path = os.path.join(upload_path, image.filename)
    with open(file_path, "wb") as f:
        f.write(await image.read())
    return {
        "name": product.name,
        "image": image.filename
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1")