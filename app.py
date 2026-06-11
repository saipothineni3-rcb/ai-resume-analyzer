from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from analyzer import (
    extract_text_from_pdf,
    analyze_resume,
    get_ai_feedback
)
from database import db
from models import User, Analysis, Feedback
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from reportlab.lib import colors
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'

mail = Mail(app)
app.secret_key = "resume_analyzer_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_analyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
# Home Page
@app.route('/')
def home():
    return render_template('home.html')


# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        # Check if email already exists
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            return render_template(
                'register.html',
                error='This email is already registered. Please log in instead.',
                show_login_button=True
            )

        password = generate_password_hash(
            request.form['password']
        )

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(
            url_for('login')
        )

    return render_template(
        'register.html',
        error=None,
        show_login_button=False
    )

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session['user_name'] = user.name
            session['user_email'] = user.email

            return redirect(url_for('dashboard'))

        return render_template(
            'login.html',
            error='Invalid Email or Password'
        )

    return render_template('login.html')

# Dashboard Page
@app.route('/dashboard')
def dashboard():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    username = session['user_name']

    analyses = Analysis.query.filter_by(
        username=username
    ).all()

    total_analyses = len(analyses)

    if total_analyses > 0:

        average_score = int(
            sum(a.ats_score for a in analyses)
            / total_analyses
        )

        highest_score = max(
            a.ats_score for a in analyses
        )

    else:

        average_score = 0
        highest_score = 0

    return render_template(
        'dashboard.html',
        username=username,
        total_analyses=total_analyses,
        average_score=average_score,
        highest_score=highest_score
    )

# Logout
@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))


# Resume Analysis
@app.route('/analyze', methods=['POST'])
def analyze():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    job_role = request.form['job_role']

    resume = request.files.get('resume')

    if resume is None:
        return "Resume file not received"

    if resume.filename == "":
        return "No file selected"

    os.makedirs('uploads', exist_ok=True)

    filepath = os.path.join(
        'uploads',
        resume.filename
    )

    resume.save(filepath)

    print("================================")
    print("Resume Uploaded Successfully")
    print("Filename:", resume.filename)
    print("Path:", filepath)
    print("================================")

    # Extract Resume Text
    resume_text = extract_text_from_pdf(
        filepath
    )

    print("===== RESUME TEXT =====")
    print(resume_text[:1000])
    print("=======================")

    # AI Analysis
    ai_data = get_ai_feedback(
        job_role,
        resume_text
    )
    review = ai_data.get(
    "review",
    ""
)

    ats_score = ai_data.get(
        "ats_score",
        0
    )

    skills_found = ai_data.get(
        "skills_found",
        0
    )

    missing_count = ai_data.get(
        "missing_count",
        0
    )

    strengths = ai_data.get(
        "strengths",
        []
    )

    weaknesses = ai_data.get(
        "weaknesses",
        []
    )

    suggestions = ai_data.get(
        "suggestions",
        []
    )

    interview_tips = ai_data.get(
        "interview_tips",
        []
    )

    recommended_roles = ai_data.get(
        "recommended_roles",
        []
    )
    recommended_courses = ai_data.get(
    "recommended_courses",
    []
)   
    career_roadmap = ai_data.get(
    "career_roadmap",
    []
)
    recommended_certifications = ai_data.get(
    "recommended_certifications",
    []
)
    career_path = ai_data.get(
    "career_path",
    []
)
    interview_questions = ai_data.get(
    "interview_questions",
    []
)
    missing_skills = ai_data.get(
        "missing_skills",
        []
    )

    matched_skills = ai_data.get(
        "matched_skills",
        []
    )

    # Save Analysis History
    analysis = Analysis(
        username=session['user_name'],
        job_role=job_role,
        ats_score=ats_score
    )

    db.session.add(analysis)
    db.session.commit()

    # Session Data
    session['job_role'] = job_role
    session['ats_score'] = ats_score
    session['matched_skills'] = matched_skills
    session['missing_skills'] = missing_skills
    session['suggestions'] = suggestions

    return render_template(
        'result.html',
        job_role=job_role,
        ats_score=ats_score,
        skills_found=skills_found,
        missing_count=missing_count,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        strengths=strengths,
        weaknesses=weaknesses,
        suggestions=suggestions,
        interview_tips=interview_tips,
        review=review,
        recommended_roles=recommended_roles,
        career_roadmap=career_roadmap,
        recommended_courses=recommended_courses,
        interview_questions=interview_questions,
        career_path=career_path,
        recommended_certifications=recommended_certifications,
        ai_feedback=ai_data
    )
@app.route('/history')
def history():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    records = Analysis.query.filter_by(
    username=session['user_name']
    ).order_by(
    Analysis.id
    ).all()

    scores = []

    for record in records:
        scores.append(record.ats_score)
    return render_template(
    'history.html',
    records=records,
    scores=scores
)
@app.route('/profile')
def profile():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(
        email=session.get('user_email')
    ).first()

    total_analyses = Analysis.query.filter_by(
        username=session['user_name']
    ).count()

    best_score = db.session.query(
        db.func.max(Analysis.ats_score)
    ).filter_by(
        username=session['user_name']
    ).scalar()

    if best_score is None:
        best_score = 0

    return render_template(
        'profile.html',
        user=user,
        total_analyses=total_analyses,
        best_score=best_score
    )
@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(
        email=session.get('user_email')
    ).first()

    print("SESSION:", dict(session))
    print("USER:", user)

    if request.method == 'POST':

        user.name = request.form['name']
        user.email = request.form['email']
        user.phone = request.form['phone']

        db.session.commit()

        session['user_name'] = user.name
        session['user_email'] = user.email

        return redirect(url_for('profile'))

    return render_template(
        'edit_profile.html',
        user=user
    )
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(
        email=session.get('user_email')
    ).first()

    if request.method == 'POST':

        current_password = request.form['current_password']
        new_password = request.form['new_password']

        if not check_password_hash(
            user.password,
            current_password
        ):
            return render_template(
                'change_password.html',
                error="Current password is incorrect"
            )

        user.password = generate_password_hash(
            new_password
        )

        db.session.commit()

        return redirect(url_for('profile'))

    return render_template(
        'change_password.html'
    )
@app.route('/delete-account')
def delete_account():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(
        email=session.get('user_email')
    ).first()

    Analysis.query.filter_by(
        username=session['user_name']
    ).delete()

    db.session.delete(user)

    db.session.commit()

    session.clear()

    return redirect(url_for('home'))
@app.route('/download-report')
def download_report():

    from datetime import datetime

    pdf_file = "resume_report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    content = []

    # Title

    content.append(
        Paragraph(
            "ResumeIQ AI - Professional Resume Report",
            styles['Title']
        )
    )

    content.append(Spacer(1, 20))

    # Candidate Information

    content.append(
        Paragraph(
            f"Candidate Name: {session.get('username', 'User')}",
            styles['Heading2']
        )
    )

    content.append(
        Paragraph(
            f"Target Job Role: {session.get('job_role', 'N/A')}",
            styles['Normal']
        )
    )

    content.append(
        Paragraph(
            f"ATS Score: {session.get('ats_score', 0)}%",
            styles['Normal']
        )
    )

    content.append(Spacer(1, 15))

    # Matched Skills

    content.append(
        Paragraph(
            "Matched Skills",
            styles['Heading2']
        )
    )

    matched_skills = session.get(
        'matched_skills',
        []
    )

    if matched_skills:

        for skill in matched_skills:

            content.append(
                Paragraph(
                    f"✓ {skill}",
                    styles['Normal']
                )
            )

    else:

        content.append(
            Paragraph(
                "No matched skills found.",
                styles['Normal']
            )
        )

    content.append(Spacer(1, 15))

    # Missing Skills

    content.append(
        Paragraph(
            "Missing Skills",
            styles['Heading2']
        )
    )

    missing_skills = session.get(
        'missing_skills',
        []
    )

    if missing_skills:

        for skill in missing_skills:

            content.append(
                Paragraph(
                    f"✗ {skill}",
                    styles['Normal']
                )
            )

    else:

        content.append(
            Paragraph(
                "No missing skills found.",
                styles['Normal']
            )
        )

    content.append(Spacer(1, 15))

    # Suggestions

    content.append(
        Paragraph(
            "Improvement Suggestions",
            styles['Heading2']
        )
    )

    suggestions = session.get(
        'suggestions',
        []
    )

    if suggestions:

        for item in suggestions:

            content.append(
                Paragraph(
                    f"• {item}",
                    styles['Normal']
                )
            )

    else:

        content.append(
            Paragraph(
                "No suggestions available.",
                styles['Normal']
            )
        )

    content.append(Spacer(1, 15))

    # AI Review

    content.append(
        Paragraph(
            "AI Resume Review",
            styles['Heading2']
        )
    )

    content.append(
        Paragraph(
            session.get(
                'review',
                'No review available.'
            ),
            styles['Normal']
        )
    )

    content.append(Spacer(1, 15))

    # Candidate Rating

    ats_score = session.get(
        'ats_score',
        0
    )

    if ats_score >= 90:

        rating = "🥇 Gold Candidate"

    elif ats_score >= 75:

        rating = "🥈 Silver Candidate"

    elif ats_score >= 60:

        rating = "🥉 Bronze Candidate"

    else:

        rating = "📚 Beginner Candidate"

    content.append(
        Paragraph(
            "Candidate Ranking",
            styles['Heading2']
        )
    )

    content.append(
        Paragraph(
            rating,
            styles['Normal']
        )
    )

    content.append(Spacer(1, 20))

    # Footer

    content.append(
        Paragraph(
            f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles['Italic']
        )
    )

    content.append(
        Paragraph(
            "Powered by ResumeIQ AI",
            styles['Italic']
        )
    )

    doc.build(content)

    return send_file(
        pdf_file,
        as_attachment=True
    )
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        feedback = Feedback(
            username=session['user_name'],
            message=request.form['message']
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template(
        'feedback.html'
    )
@app.route('/admin')
def admin():

    users = User.query.all()

    analyses = Analysis.query.all()

    feedbacks = Feedback.query.all()

    return render_template(
        'admin.html',
        users=users,
        analyses=analyses,
        feedbacks=feedbacks
    )
@app.route('/certificate')
def certificate():

    if 'user_name' not in session:
        return redirect(url_for('login'))

    pdf_file = "resume_certificate.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Certificate of Resume Evaluation",
            styles['Title']
        )
    )

    content.append(Spacer(1, 30))

    content.append(
        Paragraph(
            f"Candidate: {session['user_name']}",
            styles['Heading2']
        )
    )

    content.append(
        Paragraph(
            f"Target Role: {session.get('job_role','N/A')}",
            styles['Normal']
        )
    )

    content.append(
        Paragraph(
            f"ATS Score: {session.get('ats_score',0)}%",
            styles['Normal']
        )
    )

    score = session.get('ats_score',0)

    if score >= 90:
        rank = "Gold Candidate"
    elif score >= 75:
        rank = "Silver Candidate"
    elif score >= 60:
        rank = "Bronze Candidate"
    else:
        rank = "Beginner Candidate"

    content.append(
        Paragraph(
            f"Rank: {rank}",
            styles['Heading2']
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "This certificate is generated by AI Resume Analyzer.",
            styles['Normal']
        )
    )

    doc.build(content)

    return send_file(
        pdf_file,
        as_attachment=True
    )
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form['email']
        phone = request.form['phone']
        new_password = request.form['new_password']

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.phone == phone:

            user.password = generate_password_hash(
                new_password
            )

            db.session.commit()

            return redirect(url_for('login'))

        return render_template(
            'forgot_password.html',
            error="Invalid Email or Phone Number"
        )

    return render_template(
        'forgot_password.html'
    )
@app.route('/certificate')
def generate_certificate():

    from reportlab.pdfgen import canvas

    pdf_file = "certificate.pdf"

    c = canvas.Canvas(pdf_file)

    username = session.get(
        "username",
        "User"
    )

    ats_score = session.get(
        "ats_score",
        0
    )

    if ats_score >= 90:
        badge = "Gold Candidate"

    elif ats_score >= 75:
        badge = "Silver Candidate"

    elif ats_score >= 60:
        badge = "Bronze Candidate"

    else:
        badge = "Beginner Candidate"

    c.setFont(
        "Helvetica-Bold",
        28
    )

    c.drawCentredString(
        300,
        760,
        "CERTIFICATE"
    )

    c.setFont(
        "Helvetica",
        18
    )

    c.drawCentredString(
        300,
        710,
        "AI Resume Analysis Excellence"
    )

    c.drawCentredString(
        300,
        650,
        "Awarded To"
    )

    c.setFont(
        "Helvetica-Bold",
        24
    )

    c.drawCentredString(
        300,
        600,
        username
    )

    c.setFont(
        "Helvetica",
        18
    )

    c.drawCentredString(
        300,
        550,
        f"ATS Score: {ats_score}%"
    )

    c.drawCentredString(
        300,
        500,
        badge
    )

    c.drawCentredString(
        300,
        430,
        "ResumeIQ AI"
    )

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )
@app.route('/email-report')
def email_report():

    user_email = session.get('email')

    msg = Message(
        "Resume Analysis Report",
        sender=app.config['MAIL_USERNAME'],
        recipients=[user_email]
    )

    msg.body = """
Hello,

Your AI Resume Analysis Report
has been generated successfully.

Regards,
ResumeIQ AI
"""

    mail.send(msg)

    return "Email Sent Successfully!"
with app.app_context():
    db.create_all()

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
