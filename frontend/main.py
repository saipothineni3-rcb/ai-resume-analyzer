from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend Running"}

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    text = ""

    with open(file.filename, "wb") as f:
        f.write(await file.read())

    with pdfplumber.open(file.filename) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    return {
        "filename": file.filename,
        "resume_text": text
    }