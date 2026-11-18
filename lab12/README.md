# Lab 12: Сызықтық регрессия және классификация — өз базамыздың (EmploymentCenter) деректерімен

Орнату (репо түбірінен):
    .\.venv\Scripts\python.exe -m pip install -r lab12\requirements-lab12.txt

Жұмыс (lab12 папкасынан):
    cd lab12
    ..\.venv\Scripts\python.exe seed_ml_data.py            # демо деректерді базаға қосу (бір рет)
    ..\.venv\Scripts\python.exe regression.py              # регрессия + график
    ..\.venv\Scripts\python.exe classification.py          # классификация + графиктер
    ..\.venv\Scripts\python.exe -m streamlit run app_streamlit.py
    ..\.venv\Scripts\python.exe seed_ml_data.py --clean    # демо деректерді өшіру (email @ml.demo)
