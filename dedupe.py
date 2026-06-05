import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def dedupe_semantic(articles):
    texts = [a["title"] + " " + a.get("snippet", "") for a in articles]

    if len(texts) <= 1:
        return articles

    vec = TfidfVectorizer(stop_words="english")
    X = vec.fit_transform(texts)

    sim = cosine_similarity(X)

    keep = []
    seen = set()

    for i in range(len(articles)):
        if i in seen:
            continue
        keep.append(articles[i])
        for j in range(i + 1, len(articles)):
            if sim[i][j] > 0.85:
                seen.add(j)

    return keep
