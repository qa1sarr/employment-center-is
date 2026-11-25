"""Gemini диагностикасы: әр модельге қысқа сұраныс жіберіп, нәтижесін көрсетеді.
Қолдану: $env:GEMINI_API_KEY="..." ; ..\\.venv\\Scripts\\python.exe gemini_diag.py"""
import os
import re
import time

import requests

KEY = os.environ["GEMINI_API_KEY"]
HEAD = {"x-goog-api-key": KEY, "Content-Type": "application/json"}
BASE = "https://generativelanguage.googleapis.com/v1beta/"
TEXT_MODEL = re.compile(r"^gemini-[\d.]*-?flash(-lite)?(-latest)?$")

listing = requests.get(BASE + "models", headers=HEAD, timeout=30).json().get("models", [])
names = [m["name"].split("/", 1)[1] for m in listing
         if "generateContent" in m.get("supportedGenerationMethods", [])
         and TEXT_MODEL.match(m["name"].split("/", 1)[1])]
print("Мәтіндік flash модельдер:", names, "\n")

for model in names[:8]:
    start = time.time()
    try:
        r = requests.post(BASE + "models/%s:generateContent" % model, headers=HEAD, timeout=40,
                          json={"contents": [{"parts": [{"text": "Бір сөзбен жауап бер: 2+2 нешеге тең?"}]}]})
        took = time.time() - start
        if r.status_code == 200:
            parts = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            print("%-28s 200  %.1fс  жауап: %r" % (model, took, text[:60]))
        else:
            print("%-28s %s  %.1fс  %s" % (model, r.status_code, took, r.text.replace("\n", " ")[:160]))
    except Exception as error:
        print("%-28s ҚАТЕ  %.1fс  %s: %s" % (model, time.time() - start, type(error).__name__, str(error)[:300]))
    time.sleep(2)
