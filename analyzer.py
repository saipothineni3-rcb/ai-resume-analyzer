from groq import Groq
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path):

    text = ""

    try:

        reader = PdfReader(pdf_path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

    except Exception as e:

        print("PDF Reading Error:", e)

    return text


def analyze_resume(job_role, resume_text):

    skills_database = {

    "python developer": [
        "Python", "Flask", "SQL",
        "Git", "Docker", "REST API"
    ],

    "java developer": [
        "Java", "Spring Boot", "SQL",
        "Hibernate", "Git", "REST API"
    ],

    "frontend developer": [
        "HTML", "CSS", "JavaScript",
        "React", "Bootstrap", "Git"
    ],

    "backend developer": [
        "Python", "Java", "Node.js",
        "SQL", "REST API", "Docker"
    ],

    "full stack developer": [
        "HTML", "CSS", "JavaScript",
        "React", "Node.js", "SQL"
    ],

    "cloud engineer": [
        "AWS", "Azure", "Docker",
        "Kubernetes", "Linux", "Terraform"
    ],

    "devops engineer": [
        "Docker", "Kubernetes", "Linux",
        "Jenkins", "Git", "AWS"
    ],

    "data scientist": [
        "Python", "Machine Learning",
        "Pandas", "NumPy",
        "TensorFlow", "SQL"
    ],

    "cybersecurity analyst": [
        "Network Security",
        "Linux",
        "Wireshark",
        "SIEM",
        "Python",
        "Cyber Security"
    ]
}

    job_role = job_role.strip().lower()

    required_skills = skills_database.get(
    job_role.lower(),
    [
        "Communication",
        "Problem Solving",
        "Teamwork",
        "Git",
        "Project Management"
    ]
)

    matched_skills = []
    missing_skills = []

    resume_text = resume_text.lower()

    for skill in required_skills:

        if skill.lower() in resume_text:

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)

    # ATS Score

    if len(required_skills) > 0:

        ats_score = int(
            (
                len(matched_skills)
                /
                len(required_skills)
            ) * 100
        )

    else:

        ats_score = 0

    # Strengths

    strengths = []

    if matched_skills:

        strengths.append(
            f"Found {len(matched_skills)} relevant skills."
        )

    if ats_score >= 70:

        strengths.append(
            "Good alignment with target job role."
        )

    if "project" in resume_text:

        strengths.append(
            "Projects section detected."
        )

    if "internship" in resume_text:

        strengths.append(
            "Internship experience detected."
        )

    # Weaknesses

    weaknesses = []

    if missing_skills:

        weaknesses.append(
            f"Missing {len(missing_skills)} important skills."
        )

    if ats_score < 50:

        weaknesses.append(
            "Resume requires better optimization."
        )

    # Suggestions

    suggestions = []

    for skill in missing_skills:

        suggestions.append(
            f"Learn and add {skill} to your resume."
        )

    suggestions.append(
        "Include measurable achievements."
    )

    suggestions.append(
        "Add GitHub and LinkedIn profile links."
    )

    suggestions.append(
        "Tailor the resume for the selected role."
    )

    # Interview Tips

    interview_tips = []

    for skill in matched_skills[:3]:

        interview_tips.append(
            f"Prepare interview questions on {skill}."
        )

    if not interview_tips:

        interview_tips.append(
            "Strengthen technical fundamentals."
        )
    recommended_roles = []

    if "python" in resume_text:
        recommended_roles.append(
        "Python Developer"
    )

    if "react" in resume_text:
        recommended_roles.append(
        "Frontend Developer"
    )

    if "aws" in resume_text:
        recommended_roles.append(
        "Cloud Engineer"
    )

    if "machine learning" in resume_text:
        recommended_roles.append(
        "Data Scientist"
    )

    if "docker" in resume_text:
        recommended_roles.append(
        "DevOps Engineer"
    )
    return (
    ats_score,
    matched_skills,
    missing_skills,
    strengths,
    weaknesses,
    suggestions,
    interview_tips,
    recommended_roles
)
import json

def get_ai_feedback(job_role, resume_text):

    prompt = f"""
    You are an expert ATS Resume Analyzer and Technical Recruiter.

    Analyze the following resume for the role:

    {job_role}

    Return ONLY valid JSON.

    {{
        "ats_score": 0,
        "skills_found": 0,
        "missing_count": 0,
        "review": "",
        "matched_skills": [],
        "missing_skills": [],
        "strengths": [],
        "weaknesses": [],
        "suggestions": [],
        "interview_tips": [],
        "recommended_roles": [],
        "recommended_courses": [],
        "career_roadmap": [],
        "recommended_certifications": [],
        "career_path": [],
        "interview_questions": []
    }}

    Instructions:

    1. ATS Score should be between 0 and 100.
    2. Give a professional review paragraph.
    3. List skills found in the resume.
    4. List missing skills for the target role.
    5. Mention strengths.
    6. Mention weaknesses.
    7. Give improvement suggestions.
    8. Give interview preparation tips.
    9. Recommend suitable job roles.
    10. Recommend courses to improve missing skills.
    11. Create a career roadmap with 5 steps to improve the candidate profile.
    12. Recommend professional certifications relevant to the target role.
    13. Predict a realistic career path for the candidate over the next 5 years.
    14. Generate 10 interview questions based on the candidate's resume and target role.

    Resume Content:

    {resume_text}
    """

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=2000
        )

        result = response.choices[0].message.content

        print("\n===== AI RESPONSE =====")
        print(result)
        print("=======================\n")

        # Remove markdown wrappers if present
        result = result.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        ai_data = json.loads(result)

        return ai_data

    except Exception as e:

        print("\n===== GROQ ERROR =====")
        print(e)
        print("======================\n")

        return {
            "ats_score": 0,
            "skills_found": 0,
            "missing_count": 0,
            "review": "AI analysis is currently unavailable. Please try again later.",
            "matched_skills": [],
            "missing_skills": [],
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "interview_tips": [],
            "recommended_roles": []
        }