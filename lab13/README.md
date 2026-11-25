# Lab 13: LLM және RAG (Жұмыспен қамту орталығы жобасы)

Орнату (репо түбірінен, PowerShell):
    .\.venv\Scripts\python.exe -m pip install -r lab13\requirements-lab13.txt
(sentence-transformers көлемді: torch + модель ≈ 1-2 ГБ, алғашқы жүктеу ұзақ болады)

Іске қосу (lab13 папкасынан):
    cd lab13
    ..\.venv\Scripts\python.exe task2_embeddings.py     # 2-тапсырма: Embedding және ұқсастық
    ..\.venv\Scripts\python.exe rag.py                  # 3-5 тапсырма: RAG + тест кестесі
    ..\.venv\Scripts\python.exe rag.py "Құпиясөз неше таңба?"   # бір сұрақ
    ..\.venv\Scripts\python.exe rag.py --chat           # сұрақ-жауап

LLM (4-тапсырма), ТЕГІН нұсқа - Google Gemini (кілт: https://aistudio.google.com/apikey):
    $env:GEMINI_API_KEY="AIza..." ; ..\.venv\Scripts\python.exe rag.py
Немесе OPENAI_API_KEY орнатылса, gpt-4.1-mini қолданылады:
    $env:OPENAI_API_KEY="sk-..." ; ..\.venv\Scripts\python.exe rag.py
Кілт жоқ болса, жүйе LLM-сіз режимде жұмыс істейді (табылған контекстті жауап ретінде береді).

Білім қоры (kb.py): жүйе ережелері + SQL Server базасындағы вакансиялар мен курстар.
Базаға қосылу мүмкін болмаса, тек ережелер қолданылады.
