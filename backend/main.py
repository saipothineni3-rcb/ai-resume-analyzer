from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq
import pdfplumber
import os

# Load Environment Variables
load_dotenv()

# Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# FastAPI App
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home Route
@app.get("/")
def home():

    return {
        "message": "Backend Running 🚀"
    }

# Upload Route
@app.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form("")
):

    text = ""

    # Save Uploaded File
    with open(file.filename, "wb") as f:

        f.write(await file.read())

    # Extract PDF Text
    with pdfplumber.open(file.filename) as pdf:

        for page in pdf.pages:

            extracted = page.extract_text()

            if extracted:

                text += extracted

    # ATS Keywords
    keywords = [

        "python",
        "java",
        "react",
        "sql",
        "machine learning",
        "fastapi",
        "mongodb",
        "javascript",
        "html",
        "css",
        "nodejs",
        "git",
        "docker",
        "aws",
        "linux",
        "typescript",
        "nextjs",
        "tailwind",
        "api",
        "github"
    ]

    # Found Skills
    found_skills = []

    for skill in keywords:

        if skill.lower() in text.lower():

            found_skills.append(skill)

    # ATS Score
    ats_score = int(
        (len(found_skills) / len(keywords)) * 100
    )

    # Missing Skills
    missing_skills = [

        skill for skill in keywords

        if skill not in found_skills
    ]

    # Job Match Score
    jd_keywords = job_description.lower().split()

    matched_words = []

    for word in jd_keywords:

        if word in text.lower():

            matched_words.append(word)

    if len(jd_keywords) > 0:

        job_match_score = int(

            (
                len(set(matched_words))
                /
                len(set(jd_keywords))
            ) * 100
        )

    else:

        job_match_score = 0

    # REAL AI ANALYSIS
    try:

        prompt = f"""

Analyze this resume professionally.

Give:

1. Resume Strengths
2. Resume Weaknesses
3. Missing Skills
4. Improvement Suggestions
5. Best Job Roles
6. Career Advice
7. Interview Preparation Tips

Resume:
{text[:1500]}

Job Description:
{job_description}

"""

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        )

        ai_feedback = response.choices[0].message.content

    except Exception as e:

        ai_feedback = f"AI Error: {str(e)}"

    return {

        "filename": file.filename,

        "resume_text": text,

        "ats_score": ats_score,

        "found_skills": found_skills,

        "missing_skills": missing_skills,

        "job_match_score": job_match_score,

        "ai_feedback": ai_feedback
    }