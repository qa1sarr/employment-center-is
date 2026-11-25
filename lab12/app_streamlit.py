import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.figure import Figure

import ml_data
from ml_models import train_classification, train_regression

st.set_page_config(page_title="Жұмыспен қамту орталығы — ЖИ модулі", page_icon="📈", layout="wide")


@st.cache_data
def load_data():
    db = ml_data.get_db()
    return ml_data.load_salary(db), ml_data.load_hiring(db)


salary, hiring = load_data()

st.title("Жұмыспен қамту орталығы: жасанды интеллект модулі")
st.caption("Деректер SQL Server базасынан (EmploymentCenter) алынады, модельдер осында үйретіледі")

with st.sidebar:
    st.header("Үйрету параметрлері")
    test_size = st.slider("Тест жиынының үлесі", 0.10, 0.40, 0.20, 0.05)
    random_state = st.number_input("random_state", min_value=0, value=42, step=1)
    st.caption("Параметрді өзгертсеңіз, модель қайта үйретіледі.")
    if st.button("Деректерді базадан жаңарту"):
        load_data.clear()
        st.rerun()

reg = train_regression(salary, test_size, int(random_state))
clf = train_classification(hiring, test_size, int(random_state))

tab1, tab2 = st.tabs(["📈 Сызықтық регрессия", "🎯 Классификация"])

# ---------------------------------------------------------------- регрессия
with tab1:
    st.header("Көп параметрлі сызықтық регрессия: өтіл + дағдылар саны → вакансия жалақысы")
    st.markdown("**Екі параметр (белгі):** x₁ — жұмыс өтілі (жыл), x₂ — түйіндемедегі дағдылар саны. "
                "**Болжанатын мән:** y — жалақы (₸). Деректер: жұмысқа алынған үміткерлер (`accepted`).")
    st.dataframe(salary.head(8), use_container_width=True)

    st.markdown("**1-қадам. Деректерді бөлу.** Оқыту жиыны — модельді үйретуге, тест жиыны — тексеруге.")
    a, b, c = st.columns(3)
    a.metric("Барлығы", len(reg["X"]))
    b.metric("Оқыту жиыны", len(reg["X_train"]))
    c.metric("Тест жиыны", len(reg["X_test"]))

    st.markdown("**2-қадам. Үйрету** — `LinearRegression().fit(X_train, y_train)`: ең кіші квадраттар әдісі жазықтықты табады.")
    st.latex(r"y = w_1 \cdot өтіл + w_2 \cdot дағдылар + Bias")
    st.success(f"w₁ (өтіл) = {reg['w_exp']:,.0f} ₸ (әр жыл өтілге) · "
               f"w₂ (дағдылар) = {reg['w_skills']:,.0f} ₸ (әр дағдыға) · "
               f"Bias = {reg['bias']:,.0f} ₸".replace(",", " "))

    st.markdown("**3-қадам. Сапаны бағалау** (тест жиынында).")
    m1, m2, m3 = st.columns(3)
    m1.metric("MAE (орташа қателік)", f"{reg['mae']:,.0f} ₸".replace(",", " "))
    m2.metric("MSE", f"{reg['mse']:,.0f}".replace(",", " "))
    m3.metric("R²", f"{reg['r2']:.3f}")

    left, right = st.columns(2)
    with left:
        fig = Figure(figsize=(5.6, 4.4))
        ax = fig.subplots()
        ax.scatter(reg["y_test"], reg["y_pred"], label="Тест жиыны")
        lims = [min(reg["y_test"].min(), reg["y_pred"].min()), max(reg["y_test"].max(), reg["y_pred"].max())]
        ax.plot(lims, lims, "r--", label="Идеал болжам (y = x)")
        ax.set_xlabel("Нақты жалақы (₸)")
        ax.set_ylabel("Болжамды жалақы (₸)")
        ax.set_title("Нақты және болжамды жалақы")
        ax.legend()
        ax.grid(alpha=.3)
        st.pyplot(fig)
    with right:
        fig = Figure(figsize=(5.6, 4.4))
        ax3 = fig.add_subplot(projection="3d")
        ax3.scatter(reg["X"][:, 0], reg["X"][:, 1], reg["y"], alpha=.6)
        gx, gy = np.meshgrid(np.linspace(reg["X"][:, 0].min(), reg["X"][:, 0].max(), 10),
                             np.linspace(reg["X"][:, 1].min(), reg["X"][:, 1].max(), 10))
        ax3.plot_surface(gx, gy, reg["bias"] + reg["w_exp"] * gx + reg["w_skills"] * gy, color="red", alpha=.3)
        ax3.set_xlabel("Өтіл (жыл)")
        ax3.set_ylabel("Дағдылар")
        ax3.set_zlabel("Жалақы (₸)")
        ax3.set_title("Регрессия жазықтығы")
        st.pyplot(fig)

    with st.expander("Тест жиынында: нақты және болжамды жалақы"):
        table = pd.DataFrame({"Өтіл (жыл)": reg["X_test"][:, 0], "Дағдылар": reg["X_test"][:, 1],
                              "Нақты": reg["y_test"], "Болжам": reg["y_pred"].round(0)})
        table["Қате"] = (table["Болжам"] - table["Нақты"]).round(0)
        st.dataframe(table, use_container_width=True)

    st.markdown("**4-қадам. Нақты екі параметр бойынша болжау.**")
    p1, p2 = st.columns(2)
    years = p1.slider("Жұмыс өтілі (жыл)", 0.0, 12.0, 6.0, 0.5, key="years")
    n_skills = p2.slider("Дағдылар саны", 1, 7, 5, key="n_skills")
    if st.button("Болжау", key="predict_salary"):
        result = reg["model"].predict([[years, n_skills]])[0]
        st.success(f"Өтілі {years} жыл және {n_skills} дағдысы бар үміткерге болжамды жалақы: "
                   f"{result:,.0f} ₸".replace(",", " "))
        st.caption(f"Есеп: {reg['w_exp']:,.0f} × {years} + {reg['w_skills']:,.0f} × {n_skills} + "
                   f"{reg['bias']:,.0f}".replace(",", " "))

# ---------------------------------------------------------------- классификация
with tab2:
    st.header("Классификация: өтінім қабылдана ма?")
    st.markdown("**1-қадам. Деректерді бөлу** (`stratify` — екі сынып үлесі екі жиында бірдей).")
    a, b, c, d = st.columns(4)
    a.metric("Барлығы", len(clf["X"]))
    b.metric("Оқыту жиыны", len(clf["X_train"]))
    c.metric("Тест жиыны", len(clf["X_test"]))
    d.metric("Қабылданған үлесі", f"{clf['y'].mean() * 100:.0f}%")

    st.markdown("**2-қадам. Үйрету** — `LogisticRegression().fit(...)`: сызықтық қосынды сигмоида арқылы ықтималдыққа айналады.")
    st.latex(r"z = w_1 \cdot өтіл + w_2 \cdot балл + b,\qquad p = \frac{1}{1 + e^{-z}}")
    st.success(f"w₁ (өтіл) = {clf['w_exp']:.3f} · w₂ (сәйкестік) = {clf['w_score']:.3f} · b = {clf['bias']:.3f}.  "
               "p ≥ 0.5 → «қабылданады», әйтпесе «қабылданбайды»")

    st.markdown("**3-қадам. Сапаны бағалау** (тест жиынында).")
    m1, m2, m3 = st.columns(3)
    m1.metric("Accuracy", f"{clf['accuracy']:.2f}")
    m2.metric("Precision", f"{clf['precision']:.2f}")
    m3.metric("Recall", f"{clf['recall']:.2f}")

    left, right = st.columns(2)
    with left:
        fig = Figure(figsize=(5.6, 4.4))
        ax = fig.subplots()
        im = ax.imshow(clf["confusion"], cmap="Blues")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Қабылданбады", "Қабылданды"])
        ax.set_yticklabels(["Қабылданбады", "Қабылданды"])
        ax.set_xlabel("Болжам")
        ax.set_ylabel("Нақты")
        ax.set_title("Қателер матрицасы")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, int(clf["confusion"][i, j]), ha="center", va="center", fontsize=16,
                        color="white" if clf["confusion"][i, j] > clf["confusion"].max() / 2 else "black")
        st.pyplot(fig)
    with right:
        fig = Figure(figsize=(5.6, 4.4))
        ax = fig.subplots()
        for label, color, name in ((0, "gray", "Қабылданбады"), (1, "tab:blue", "Қабылданды")):
            mask = clf["y"] == label
            ax.scatter(clf["X"][mask, 0], clf["X"][mask, 1], c=color, label=name, alpha=.7)
        xs = np.linspace(clf["X"][:, 0].min(), clf["X"][:, 0].max(), 50)
        if abs(clf["w_score"]) > 1e-9:  # p = 0.5 шекара сызығы: z = 0
            ax.plot(xs, -(clf["w_exp"] * xs + clf["bias"]) / clf["w_score"], "r--", label="Шешім шекарасы")
        ax.set_ylim(clf["X"][:, 1].min() - 3, clf["X"][:, 1].max() + 3)
        ax.set_xlabel("Жұмыс өтілі (жыл)")
        ax.set_ylabel("Сәйкестік балы")
        ax.legend()
        ax.grid(alpha=.3)
        st.pyplot(fig)

    st.markdown("**4-қадам. Жаңа өтінімді жіктеу.**")
    exp = st.slider("Жұмыс өтілі (жыл)", 0.0, 12.0, 4.0, 0.5, key="exp")
    score = st.slider("Вакансиямен сәйкестік (%)", 0, 100, 80, key="score")
    if st.button("Классификациялау", key="classify"):
        p = clf["model"].predict_proba([[exp, score]])[0, 1]
        (st.success if p >= 0.5 else st.warning)(
            f"Қабылдану ықтималдығы: {p * 100:.1f}% → {'қабылданады' if p >= 0.5 else 'қабылданбайды'}")
        st.progress(float(p))
