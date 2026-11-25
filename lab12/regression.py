"""Көп параметрлі сызықтық регрессия: ЕКІ параметр бойынша вакансия жалақысын болжау.
x1 - жұмыс өтілі (жыл), x2 - түйіндемедегі дағдылар саны. Деректер: өз базамыз."""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import ml_data

# Деректер (SQL Server: status = 'accepted')
data = ml_data.load_salary()
print("Базадан алынған жазба саны:", len(data))
print(data.head())
X = data[["experience_years", "skills_count"]].values   # екі параметр
y = data["salary"].values                                # жалақы (тг)

# Деректерді бөлу
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Модельді құру және оқыту
model = LinearRegression()
model.fit(X_train, y_train)

# Болжау
y_pred = model.predict(X_test)

# Модель параметрлері: y = w1*өтіл + w2*дағдылар + Bias
print("Weight (өтіл)      :", model.coef_[0])
print("Weight (дағдылар)  :", model.coef_[1])
print("Bias               :", model.intercept_)

# Модель сапасын бағалау
print("MAE:", mean_absolute_error(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))
print("R2:", r2_score(y_test, y_pred))

# Жаңа үміткер: 6 жыл өтілі, 5 дағды
new_candidate = np.array([[6, 5]])
prediction = model.predict(new_candidate)
print("6 жыл өтілі және 5 дағдысы бар үміткердің болжамды жалақысы:", round(prediction[0]), "тг")

# Графиктер
fig = plt.figure(figsize=(12, 5))
ax = fig.add_subplot(1, 2, 1)
ax.scatter(y_test, y_pred, label="Тест жиыны")
lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
ax.plot(lims, lims, "r--", label="Идеал болжам (y = x)")
ax.set_xlabel("Нақты жалақы (тг)")
ax.set_ylabel("Болжамды жалақы (тг)")
ax.set_title("Нақты және болжамды жалақы")
ax.legend()

ax3 = fig.add_subplot(1, 2, 2, projection="3d")
ax3.scatter(X[:, 0], X[:, 1], y, alpha=.7)
gx, gy = np.meshgrid(np.linspace(X[:, 0].min(), X[:, 0].max(), 10),
                     np.linspace(X[:, 1].min(), X[:, 1].max(), 10))
gz = model.intercept_ + model.coef_[0] * gx + model.coef_[1] * gy
ax3.plot_surface(gx, gy, gz, color="red", alpha=.3)
ax3.set_xlabel("Өтіл (жыл)")
ax3.set_ylabel("Дағдылар саны")
ax3.set_zlabel("Жалақы (тг)")
ax3.set_title("Регрессия жазықтығы")
plt.tight_layout()
plt.savefig("regression.png", dpi=150, bbox_inches="tight")
plt.show()
