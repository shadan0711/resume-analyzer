def compare_skills(user_skills, role_data):
    present = []
    missing = []

    for category in role_data:
        for skill in role_data[category]:
            if skill in user_skills:
                present.append(skill)
            else:
                missing.append(skill)

    return present, missing
def generate_roadmap(missing, role_data):
    if not missing:
        return []

    roadmap = []

    # follow order: must → core → optional
    for category in ["must", "core", "optional"]:
        for skill in role_data[category]:
            if skill in missing:
                roadmap.append(skill)

    return roadmap

def suggest_best_role(skills, roles):
    best_role = None
    best_score = 0

    for role, data in roles.items():
        must = data["must"]
        core = data["core"]
        optional = data["optional"]

        must_match = len([s for s in skills if s in must])
        core_match = len([s for s in skills if s in core])
        optional_match = len([s for s in skills if s in optional])

        total_weight = len(must)*3 + len(core)*2 + len(optional)*1

        if total_weight == 0:
            score = 0
        else:
            score = (
                must_match * 3 +
                core_match * 2 +
                optional_match * 1
            ) / total_weight * 100

        if score > best_score:
            best_score = score
            best_role = role

    return best_role, round(best_score, 2)

def generate_timeline(missing):
    timeline = []

    for i, skill in enumerate(missing):
        if i == 0:
            timeline.append(f"Week 1-2: Learn basics of {skill}")
        elif i == 1:
            timeline.append(f"Week 3: Practice {skill} with a small project")
        else:
            timeline.append(f"Week {i+2}: Apply {skill} in a real project")

    return timeline