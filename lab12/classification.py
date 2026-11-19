import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, classification_report,
                             confusion_matrix, precision_score, recall_score)
from sklearn.model_selection import train_test_split

import ml_data

data = ml_data.load_hiring()
print("Базадан алынған жазба саны:", len(data), "| қабылданған үлесі:", round(data["hired"].mean(), 2))
X = data[["experience_years", "match_score"]].values
y = data["hired"].values

# Деректерді бөлу
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# Модельді құру және оқыту
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Болжау
y_pred = model.predict(X_test)

# Сапаны бағалау
print("Accuracy :", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall   :", recall_score(y_test, y_pred))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["қабылданбады (0)", "қабылданды (1)"]))

# Жаңа өтінім: 4 жыл өтілі, сәйкестік 80%
candidate = np.array([[4, 80]])
proba = model.predict_proba(candidate)[0, 1]
print("Өтінімнің қабылдану ықтималдығы: %.1f%%  ->  %s" % (
    proba * 100, "қабылданады" if proba >= 0.5 else "қабылданбайды"))

# Графиктер
fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
for label, color, name in ((0, "tab:gray", "Қабылданбады"), (1, "tab:blue", "Қабылданды")):
    mask = y == label
    ax[0].scatter(X[mask, 0], X[mask, 1], c=color, label=name, alpha=.8)
ax[0].set_xlabel("Жұмыс өтілі (жыл)")
ax[0].set_ylabel("Сәйкестік балы")
ax[0].set_title("Деректер")
ax[0].legend()
ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=ax[1], colorbar=False)
ax[1].set_title("Қателер матрицасы (тест жиыны)")
plt.tight_layout()
plt.savefig("classification.png", dpi=150, bbox_inches="tight")
plt.show()
