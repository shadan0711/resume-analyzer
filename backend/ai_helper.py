import os

def generate_explanation(roadmap):
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")

        # 🔥 If no API key → fallback immediately
        if not api_key:
            raise Exception("No API key")

        client = OpenAI(api_key=api_key)

        if not roadmap:
            return "You already have most required skills. Focus on projects and real-world practice."

        # prompt = f"""
        # The user is missing these skills: {', '.join(roadmap)}.

        # Explain simply:
        # - what these skills are
        # - why they matter
        # - how to start learning them

        # Keep it short and practical.
        # """
        prompt = f"""
The user is missing these skills: {', '.join(roadmap[:5])}.

Give exactly 3 clear steps for a beginner:

- Each step should be practical
- Mention what to learn and what to build
- Keep it simple and actionable

Format like:
1. ...
2. ...
3. ...
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception:
     if not roadmap:
        return "You are already well prepared. Start building real projects and apply for roles."

    top_skills = roadmap[:3]

    return f"""
1. Start with {top_skills[0]}: Learn basics from YouTube or documentation and build a small project.

2. Move to {top_skills[1] if len(top_skills) > 1 else top_skills[0]}: Practice by creating real-world features.

3. Finally learn {top_skills[2] if len(top_skills) > 2 else top_skills[0]}: Combine everything into one strong project.

Focus on building projects, not just watching tutorials.
"""