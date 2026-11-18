"""Модельді ақпараттық жүйеге интеграциялау (Streamlit). Модельдер ӨЗ базамыздағы деректермен оқытылады."""
import streamlit as st
from sklearn.linear_model import LinearRegression, LogisticRegression

import ml_data

st.set_page_config(page_title="Жұмыспен қамту орталығы — болжау", page_icon="📈")


@st.cache_resource
def train_models():
    db = ml_data.get_db()
    salary = ml_data.load_salary(db)
    hiring = ml_data.load_hiring(db)
    reg = LinearRegression().fit(salary[["experience_years"]].values, salary["salary"].values)
    clf = LogisticRegression(max_iter=1000).fit(
        hiring[["experience_years", "match_score"]].values, hiring["hired"].values)
    return reg, clf, salary, len(hiring)


reg, clf, salary, n_hiring = train_models()
st.title("Жұмыспен қамту орталығы: болжау модулі")
st.caption(f"Модельдер SQL Server базасындағы деректермен оқытылған "
           f"(жалақы: {len(salary)} жазба, өтінімдер: {n_hiring} жазба)")
tab1, tab2 = st.tabs(["💰 Жалақыны болжау", "🎯 Өтінімнің қабылдану ықтималдығы"])

with tab1:
    st.caption("Сызықтық регрессия: жұмыс өтілі → вакансия жалақысы")
    years = st.slider("Жұмыс өтілі (жыл)", 0.0, 12.0, 3.0, 0.5, key="years")
    if st.button("Болжау", key="predict_salary"):
        result = reg.predict([[years]])[0]
        st.success(f"Болжамды жалақы: {result:,.0f} ₸".replace(",", " "))
    st.scatter_chart(salary, x="experience_years", y="salary")

with tab2:
    st.caption("Логистикалық регрессия (классификация): қабылданады / қабылданбайды")
    exp = st.slider("Жұмыс өтілі (жыл)", 0.0, 12.0, 4.0, 0.5, key="exp")
    score = st.slider("Вакансиямен сәйкестік (%)", 0, 100, 80, key="score")
    if st.button("Классификациялау", key="classify"):
        p = clf.predict_proba([[exp, score]])[0, 1]
        (st.success if p >= 0.5 else st.warning)(
            f"Қабылдану ықтималдығы: {p * 100:.1f}% → "
            f"{'қабылданады' if p >= 0.5 else 'қабылданбайды'}")
        st.progress(float(p))
