"""3–5-тапсырмалар: RAG жүйесі — өз жобамыздың білім қорымен (ережелер + база деректері).
  python rag.py                 - 5-тапсырма: тест кестесін орындау
  python rag.py "сұрақ"         - бір сұраққа жауап
  python rag.py --chat          - сұрақ-жауап режимі
Embedding: sentence-transformers (болса), әйтпесе TF-IDF.
LLM: GEMINI_API_KEY (Google, тегін) болса Gemini, OPENAI_API_KEY болса OpenAI, екеуі де жоқ болса LLM-сіз режим."""
import os
import re
import sys
import time

from sklearn.metrics.pairwise import cosine_similarity

import kb
from embedder import TfidfEmbedder, get_embedder

NO_INFO = "Бұл ақпарат құжаттарда жоқ"


class _Failed:
    """Желі қатесін HTTP жауабы сияқты көрсету үшін."""
    def __init__(self, status_code, text):
        self.status_code, self.text = status_code, text


class RagSystem:
    def __init__(self, documents, embedder_kind="auto"):
        self.documents = documents                                  # 3.2. Құжаттар базасы
        self.embedder = get_embedder(documents, embedder_kind)
        self.doc_embeddings = self.embedder.encode(documents)       # Құжаттарды векторлау
        # гибрид: семантикалық embedding + символдық TF-IDF (қазақ тілінің жалғауларына төзімді)
        self.hybrid = self.embedder.name != "tfidf"
        if self.hybrid:
            self.lexical = TfidfEmbedder(documents)
            self.doc_lexical = self.lexical.encode(documents)
        self.client = None
        self.provider = None
        if os.environ.get("GEMINI_API_KEY"):
            self.provider = "Gemini"
        elif os.environ.get("OPENAI_API_KEY"):
            from openai import OpenAI
            self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            self.provider = "OpenAI"

    # 3.3. RAG іздеу алгоритмі
    def retrieve(self, query, top_k=3):
        query_embedding = self.embedder.encode([query])
        scores = cosine_similarity(query_embedding, self.doc_embeddings)[0]
        if self.hybrid:
            lexical = cosine_similarity(self.lexical.encode([query]), self.doc_lexical)[0]
            scores = 0.5 * scores + 0.5 * lexical
        indices = scores.argsort()[::-1][:top_k]
        return [(self.documents[i], float(scores[i])) for i in indices]

    # 3.4. LLM үшін Prompt
    @staticmethod
    def create_prompt(query, context):
        context_text = "\n".join(context)
        return f"""
Сен Жұмыспен қамту орталығының ақпараттық жүйесінің көмекшісісің.
Тек төмендегі контекстке сүйеніп жауап бер.
Егер ақпарат контекстте болмаса,
"{NO_INFO}" деп жауап бер.

Контекст:
{context_text}

Сұрақ:
{query}

Жауап:
"""

    # 4.1. Жауап генерациялау
    def generate_answer(self, query, context):
        prompt = self.create_prompt(query, context)
        if self.provider == "Gemini":
            return self._gemini(prompt)
        if self.provider == "OpenAI":
            response = self.client.responses.create(model="gpt-4.1-mini", input=prompt)
            return response.output_text
        raise RuntimeError("API кілті жоқ")

    _gemini_model = None
    _TEXT_MODEL = re.compile(r"^gemini-[\d.]*-?flash(-lite)?(-latest)?$")   # omni/image/tts/live модельдерін алып тастайды

    @classmethod
    def _gemini_models(cls, headers, base):
        """Қолжетімді мәтіндік flash модельдер: алдымен lite (тегін квотасы кең), '-latest' бірінші."""
        import requests
        listing = requests.get(base + "models", headers=headers, timeout=30).json().get("models", [])
        names = [m["name"].split("/", 1)[1] for m in listing
                 if "generateContent" in m.get("supportedGenerationMethods", [])
                 and cls._TEXT_MODEL.match(m["name"].split("/", 1)[1])]
        return sorted(names, key=lambda n: ("lite" not in n, "latest" not in n, [-ord(c) for c in n]))

    @staticmethod
    def _gemini_text(data):
        """Жауаптан мәтінді алады; жоқ болса (қауіпсіздік блогы, басқа формат) None."""
        try:
            parts = data["candidates"][0]["content"]["parts"]
        except (KeyError, IndexError, TypeError):
            return None
        text = "".join(part.get("text", "") for part in parts)
        return text or None

    @classmethod
    def _gemini(cls, prompt):
        """Google Gemini REST API (тегін кілт: https://aistudio.google.com/apikey).
        503/429 (жүктеме) болса - қайталайды; 404, тұрақты 503 немесе мәтінсіз жауап болса - басқа flash модельге көшеді."""
        import time
        import requests
        headers = {"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"}
        base = "https://generativelanguage.googleapis.com/v1beta/"
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        queue = [cls._gemini_model or os.environ.get("GEMINI_MODEL", "gemini-flash-lite-latest")]
        tried_list = False
        failed = 0
        response = None
        while queue and failed < 5:                        # ең көбі 5 модель сынаймыз
            model = queue.pop(0)
            for attempt in range(3):
                try:
                    response = requests.post(base + "models/%s:generateContent" % model, headers=headers,
                                             json=body, timeout=30)
                except requests.RequestException as error:   # тайм-аут, желі үзілісі
                    response = _Failed(599, "%s: %s" % (type(error).__name__, error))
                    if isinstance(error, requests.Timeout) or attempt == 1:
                        break                                # тайм-аутта модельді ауыстырамыз
                    time.sleep(3)                            # ConnectionError: бір рет қайталаймыз
                    continue
                if response.status_code not in (429, 500, 503):
                    break
                if attempt < 2:                              # 429 (минуттық шек): ұзағырақ күтеміз
                    time.sleep((15, 30)[attempt] if response.status_code == 429 else (2, 5)[attempt])
            if response.status_code == 200:
                text = cls._gemini_text(response.json())
                if text:
                    cls._gemini_model = model
                    return text
                response = _Failed(0, "жауапта мәтін жоқ (%s моделі)" % model)
            failed += 1
            cls._gemini_model = None                         # жұмыс істемеген модельді есте сақтамаймыз
            if not tried_list:
                tried_list = True                            # басқа модельдерді тізімнен алу
                try:
                    queue = [m for m in cls._gemini_models(headers, base) if m != model]
                except requests.RequestException:
                    queue = []
                if queue:
                    print("(%s жауап бермеді, басқа модельдер сыналады: %s)" % (model, ", ".join(queue[:3])))
        raise RuntimeError("Gemini қатесі %s: %s" % (response.status_code, response.text[:300]))

    def answer(self, query, top_k=3):
        found = self.retrieve(query, top_k)
        context = [text for text, _ in found]
        if self.provider:
            try:
                return self.generate_answer(query, context), found, "LLM (%s)" % self.provider
            except RuntimeError as error:
                mode = "LLM қолжетімсіз -> іздеу нәтижесі"
                print("   (%s)" % str(error).splitlines()[0][:90])
                return self._retrieval_answer(found), found, mode
        return self._retrieval_answer(found), found, "LLM-сіз (іздеу нәтижесі)"

    def _retrieval_answer(self, found):
        """LLM-сіз жауап: табылған құжаттар; ұқсастық төмен болса - «жоқ»."""
        default = self.embedder.threshold if not self.hybrid else 0.30
        threshold = float(os.environ.get("RAG_THRESHOLD", default))
        best_score = found[0][1]
        if best_score < threshold:
            return NO_INFO
        return " ".join(text for text, score in found if score >= 0.6 * best_score)


# 5-тапсырма: тест сұрақтары (жүйеге бейімделген) және күтілетін нәтиже
TESTS = [
    ("Құпиясөз кемінде неше таңбадан тұруы керек?", "6"),
    ("Өтінімнің қандай мәртебелері бар?", "Қаралды"),
    ("Жабық вакансияға өтінім беруге бола ма?", "болмайды"),
    ("Сәйкестік балы қалай есептеледі?", "пайыз"),
    ("Junior аналитик вакансиясының жалақысы қанша?", "@salary:Junior аналитик вакансиясы"),
    ("Орталықтың директоры кім?", NO_INFO),
]


def expected_value(rag, expected):
    """'@salary:Атауы' - күтілетін жалақы базадағы құжаттан алынады (деректер өзгерсе, тест те сәйкес өзгереді)."""
    if not expected.startswith("@salary:"):
        return expected
    prefix = expected.split(":", 1)[1]
    for doc in rag.documents:
        match = re.match(re.escape(prefix) + r".*?жалақы (\d+) теңге", doc)
        if match:
            return match.group(1)
    return "?"


def run_tests(rag):
    print("Embedding:", rag.embedder.name, "| іздеу:", "гибрид" if rag.hybrid else "TF-IDF",
          "| құжат саны:", len(rag.documents))
    passed = 0
    for n, (question, expected) in enumerate(TESTS, 1):
        if n > 1 and rag.provider == "Gemini":
            time.sleep(float(os.environ.get("RAG_DELAY", "6")))   # тегін деңгейдің минуттық шегінен аспау үшін
        expected = expected_value(rag, expected)
        try:
            answer, found, mode = rag.answer(question)
        except RuntimeError as error:
            print(f"\n{n}. Сұрақ: {question}\n   ҚАТЕ: {error}")
            continue
        ok = expected.lower() in answer.lower()
        passed += ok
        print(f"\n{n}. Сұрақ: {question}")
        print("   Табылған контекст:")
        for text, score in found:
            print(f"     - ({score:.3f}) {text}")
        print(f"   Жауап [{mode}]: {answer.strip()}")
        print(f"   Күтілетін нәтиже: {expected} -> {'✔ сәйкес' if ok else '✘ сәйкес емес'}")
    print(f"\nНәтиже: {passed}/{len(TESTS)} тест өтті")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    kind = "tfidf" if "--tfidf" in sys.argv else "auto"
    rag = RagSystem(kb.build_documents(), kind)
    if "--chat" in sys.argv:
        print("Сұрағыңызды жазыңыз (шығу: бос жол)")
        while True:
            q = input("> ").strip()
            if not q:
                break
            answer, found, mode = rag.answer(q)
            print(answer.strip(), f"  [{mode}]")
    elif args:
        answer, found, mode = rag.answer(" ".join(args))
        for text, score in found:
            print(f"({score:.3f}) {text}")
        print("Жауап:", answer.strip())
    else:
        run_tests(rag)
