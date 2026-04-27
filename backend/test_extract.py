import json
from skill_extractor import extract_text, extract_skills
from roadmap import compare_skills

# load role data
with open("role_data.json") as f:
    roles = json.load(f)

# extract from resume
text = extract_text("uploads/shadan_cv.pdf")
skills = extract_skills(text)

# compare
present, missing = compare_skills(skills, roles["frontend"])

print("User Skills:", skills)
print("Present:", present)
print("Missing:", missing)