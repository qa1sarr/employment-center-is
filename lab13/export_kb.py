"""Базадағы деректерді Colab ноутбугына беру үшін db_docs.json файлына жазады.
Қолдану (lab13 папкасынан):  ..\\.venv\\Scripts\\python.exe export_kb.py
Шыққан db_docs.json файлын Colab-тағы 3-тапсырма ұяшығында жүктейсіз (files.upload)."""
import json

import kb

docs = kb.build_documents()[len(kb.STATIC_DOCS):]
with open("db_docs.json", "w", encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=2)
print("Жазылды: db_docs.json, құжат саны:", len(docs))
