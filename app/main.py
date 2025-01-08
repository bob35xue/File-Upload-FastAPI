import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from .schemas.product import Product
import subprocess
import sys

app = FastAPI()

upload_path = "uploads"
os.makedirs(upload_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_path))

 # Set up the environment variables  
env = os.environ.copy()
env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")

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

@app.post("/video2image")
async def video_to_image():
    try:
       
        # Run video2image.py
        process = subprocess.Popen(
            [sys.executable, "app/video2image.py"],
            env=env
        )
        process.wait()  # Wait for the process to complete
        
        return JSONResponse(content={"message": "Video processing completed successfully"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)




@app.post("/run-bundle-process")
async def run_bundle_process():
    # Run the bundle4pipe.py script
    # Use the same Python interpreter that's running the FastAPI app
    process = subprocess.Popen([sys.executable, "app/bundle4pipe.py"],env=env)
    process.communicate()  # Wait for the process to complete
    return {"status": "Bundle processing started."}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1")