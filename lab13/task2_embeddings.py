"""2-тапсырма: мәтінді Embedding-ке айналдыру және семантикалық ұқсастық (жобамыздың мәтіндерімен)."""
from sklearn.metrics.pairwise import cosine_similarity

import kb
from embedder import get_embedder

documents = [
    "Жұмыс іздеуші ашық вакансияға «Өтінім беру» батырмасы арқылы өтінім береді.",
    "Түйіндемедегі дағдылар вакансия талаптарымен салыстырылып, сәйкестік балы есептеледі.",
    "Python бағдарламалау тілі деректерді өңдеу үшін қолданылады.",
    "Құпиясөз кемінде 6 таңбадан тұруы керек.",
]

embedder = get_embedder(documents + kb.STATIC_DOCS)       # SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Embedding моделі:", embedder.name)

# Мәтіндерді векторларға айналдыру
embeddings = embedder.encode(documents)
print("Embedding өлшемі:", embeddings.shape)

# Сұранысқа ең ұқсас мәтінді табу
query = "Жұмыс іздеуші вакансияға қалай өтінім береді?"
query_embedding = embedder.encode([query])
similarities = cosine_similarity(query_embedding, embeddings)[0]

print("\nСұраныс:", query)
for i, score in enumerate(similarities):
    print(f"{documents[i]} -> {score:.4f}")

best_index = similarities.argmax()
print("\nЕң сәйкес құжат:")
print(documents[best_index])
