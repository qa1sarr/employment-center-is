"""Embedding: негізгі нұсқа — SentenceTransformer (лабадағыдай). Жоқ болса — символдық TF-IDF (қосалқы)."""
import numpy as np

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


class TfidfEmbedder:
    """Қосалқы нұсқа: сөз түбірлерін ұстау үшін символдық n-граммдар (қазақ тілі жалғамалы)."""
    name = "tfidf"
    threshold = 0.28      # осыдан төмен ұқсастық = «құжатта жоқ» (LLM-сіз режим)

    def __init__(self, corpus):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True,
                                          sublinear_tf=True)
        self.vectorizer.fit(corpus)

    def encode(self, texts):
        return self.vectorizer.transform(list(texts)).toarray()


class SentenceEmbedder:
    name = "sentence-transformers"
    threshold = 0.35

    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(MODEL_NAME)

    def encode(self, texts):
        return np.asarray(self.model.encode(list(texts)))


def get_embedder(corpus, kind="auto"):
    """kind: 'auto' | 'st' | 'tfidf'."""
    if kind in ("auto", "st"):
        try:
            return SentenceEmbedder()
        except ImportError:
            if kind == "st":
                raise
            print("Ескерту: sentence-transformers орнатылмаған, қосалқы TF-IDF қолданылады.")
    return TfidfEmbedder(corpus)
