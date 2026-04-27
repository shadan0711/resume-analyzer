from flask import Flask, request, render_template, send_file
from flask_cors import CORS
from roadmap import compare_skills, generate_roadmap, suggest_best_role, generate_timeline
from ai_helper import generate_explanation
import os
import json
import io
from skill_extractor import extract_text, extract_skills
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]
    role = request.form["role"]

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        return {"error": "Only PDF and DOCX resumes are supported."}

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    try:
        text = extract_text(path)
        skills = extract_skills(text)
    finally:
        if os.path.exists(path):
            os.remove(path)

    if len(skills) < 2:
        return {"error": "No relevant technical skills found. Please upload a proper resume."}

    with open("role_data.json") as f:
        roles = json.load(f)

    best_role, best_score = suggest_best_role(skills, roles)
    present, missing = compare_skills(skills, roles[role])
    role_info = roles[role]

    must     = role_info["must"]
    core     = role_info["core"]
    optional = role_info["optional"]

    must_match     = len([s for s in skills if s in must])
    core_match     = len([s for s in skills if s in core])
    optional_match = len([s for s in skills if s in optional])

    total_weight = len(must)*3 + len(core)*2 + len(optional)*1
    match_score = (
        (must_match*3 + core_match*2 + optional_match*1) / total_weight
    ) * 100 if total_weight else 0

    roadmap     = generate_roadmap(missing, roles[role])
    timeline    = generate_timeline(roadmap)
    explanation = generate_explanation(roadmap)

    response = {
        "skills_found": skills,
        "present":      present,
        "missing":      missing,
        "roadmap":      roadmap,
        "timeline":     timeline,
        "best_role":    best_role,
        "best_score":   best_score,
        "match_score":  round(match_score, 2),
        "explanation":  explanation,
    }

    if match_score < 30:
        response["message"] = f"Your skills align more with {best_role}. Consider exploring that role."

    return response


@app.route("/download-roadmap", methods=["POST"])
def download_roadmap():
    data        = request.json
    role        = data.get("role", "unknown").upper()
    match_score = data.get("match_score", 0)
    present     = data.get("present", [])
    missing     = data.get("missing", [])
    roadmap     = data.get("roadmap", [])
    timeline    = data.get("timeline", [])
    explanation = data.get("explanation", "")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Title'],
        fontSize=20, textColor=colors.HexColor('#667eea'),
        spaceAfter=6, alignment=TA_CENTER)
    sub_style = ParagraphStyle('S', parent=styles['Normal'],
        fontSize=11, textColor=colors.gray,
        spaceAfter=16, alignment=TA_CENTER)
    heading_style = ParagraphStyle('H', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#333333'),
        spaceBefore=16, spaceAfter=6)
    body_style = ParagraphStyle('B', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#444444'),
        spaceAfter=5, leading=16)

    story = []
    story.append(Paragraph("Resume Skill Analyzer", title_style))
    story.append(Paragraph(f"Role: {role}  |  Match Score: {match_score}%", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Skills You Have", heading_style))
    story.append(Paragraph(", ".join(present) if present else "None detected.", body_style))

    story.append(Paragraph("Missing Skills", heading_style))
    story.append(Paragraph(", ".join(missing) if missing else "None!", body_style))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Paragraph("Learning Roadmap", heading_style))
    for i, skill in enumerate(roadmap, 1):
        story.append(Paragraph(f"{i}. {skill}", body_style))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Paragraph("Learning Timeline", heading_style))
    for item in timeline:
        story.append(Paragraph(f"• {item}", body_style))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Paragraph("AI Guidance", heading_style))
    for line in explanation.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), body_style))

    doc.build(story)
    buffer.seek(0)

    return send_file(buffer, mimetype="application/pdf",
        as_attachment=True,
        download_name=f"roadmap_{role.lower()}.pdf")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)