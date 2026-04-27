import re
import os
import json
from pypdf import PdfReader
from docx import Document

# -------------------------------
# Extract text from PDF or DOCX
# -------------------------------
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
        text = re.sub(r'(?<=[a-zA-Z]) (?=[a-zA-Z])', '', text)
        return text.lower()

    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.lower()

    else:
        return ""

# -------------------------------
# SKILLS auto-generated from role_data.json
# -------------------------------
with open("role_data.json") as f:
    _roles = json.load(f)

SKILLS = list(set(
    skill for role in _roles.values()
    for category in role.values()
    for skill in category
))

# -------------------------------
# Mapping for variations
# -------------------------------
skill_map = {
    "js": "javascript",
    "reactjs": "react",
    "nodejs": "node",
    "node.js": "node",
    "react.js": "react",
    "express.js": "express",
    "py": "python",
    "html5": "html",
    "css3": "css",
    "expressjs": "express",
    "mongo": "mongodb",
    "tailwind css": "tailwind",
    "tailwindcss": "tailwind",
}

# -------------------------------
# Extract skills from text
# -------------------------------
def extract_skills(text):
    text = text.lower()
    found = set()

    for skill in SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found.add(skill)

    for key, value in skill_map.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text):
            found.add(value)

    return list(found)