import config


def score_article(text):
    score = 0
    tags = set()

    text = text.lower()

    for k, v in config.ACTUARIAL_KEYWORDS.items():
        if k in text:
            score += v

    for k, t in config.FUNCTION_TAGS.items():
        if k in text:
            tags.update(t)

    if score >= 12:
        impact = "HIGH"
    elif score >= 7:
        impact = "MEDIUM"
    else:
        impact = "LOW"

    return score, list(tags), impact


def score_articles(articles):
    for a in articles:
        score, tags, impact = score_article(a["title"] + " " + a.get("snippet", ""))
        a["score"] = score
        a["tags"] = tags
        a["impact"] = impact
        a["id"] = None
    return articles
