from groq import Groq
import config


def summarize(articles):
    client = Groq(api_key=config.GROQ_API_KEY)

    context = "\n".join([
        f"- {a['title']}" for a in sorted(articles, key=lambda x: -x.get("score", 0))[:40]
    ])

    prompt = f"""
Actuarial intelligence briefing:

{context}

Write structured summary with sections.
"""

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    return res.choices[0].message.content
