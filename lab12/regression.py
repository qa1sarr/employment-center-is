import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import ml_data

data = ml_data.load_salary()
print("Базадан алынған жазба саны:", len(data))
X = data[["experience_years"]].values
y = data["salary"].values

# Деректерді бөлу
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Модельді құру және оқыту
model = LinearRegression()
model.fit(X_train, y_train)

# Болжау
y_pred = model.predict(X_test)

# Модель параметрлері
print("Weight:", model.coef_[0])
print("Bias:", model.intercept_)

# Модель сапасын бағалау
print("MAE:", mean_absolute_error(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))
print("R2:", r2_score(y_test, y_pred))

# Жаңа мәнді болжау
new_candidate = np.array([[6.5]])
prediction = model.predict(new_candidate)
print("6.5 жыл өтілі бар үміткердің болжамды жалақысы:", round(prediction[0]), "тг")

# График
plt.scatter(X, y, label="Нақты деректер (базадан)")
plt.plot(X, model.predict(X), color="red", label="Регрессия сызығы")
plt.xlabel("Жұмыс өтілі (жыл)")
plt.ylabel("Жалақы (тг)")
plt.title("Жұмыс өтіліне байланысты жалақыны болжау")
plt.legend()
plt.savefig("regression.png", dpi=150, bbox_inches="tight")
plt.show()
