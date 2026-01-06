import sys

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score
from src.utils import split_data

# 1. Data Generation (Matching the lesson logic)
np.random.seed(2)
page_speeds: np.ndarray = np.random.normal(3.0, 1.0, 100)
purchase_amount: np.ndarray = np.random.normal(50.0, 30.0, 100) / page_speeds

# 2. Split Data using our new SSoT function from src
train_x, test_x, train_y, test_y = split_data(
    page_speeds, purchase_amount, train_size=0.8, shuffle=True
)

# 3. Experiment: Testing different polynomial degrees
degrees: list[int] = list(range(1, 11))
train_scores: list[float] = []
test_scores: list[float] = []

for degree in degrees:
    # Fit model on training data
    polynomial_weights: np.ndarray = np.polyfit(train_x, train_y, degree)
    model: np.poly1d = np.poly1d(polynomial_weights)

    # Calculate R-squared scores
    r2_train: float = r2_score(train_y, model(train_x))
    r2_test: float = r2_score(test_y, model(test_x))

    train_scores.append(r2_train)
    test_scores.append(r2_test)

# 4. Visualization of the "Sweet Spot"
plt.figure(figsize=(10, 6))
plt.plot(degrees, train_scores, label="Train $R^2$", marker="o", linestyle="--")
plt.plot(degrees, test_scores, label="Test $R^2$", marker="s", color="red")
plt.xlabel("Polynomial Degree")
plt.ylabel("$R^2$ Score")
plt.title("Finding the Sweet Spot: Bias vs Variance Tradeoff")
plt.xticks(degrees)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Final Verdict Logic
best_degree: int = degrees[np.argmax(test_scores)]
# Displaying results without using print()

sys.stdout.write(f"\n>>> 💡 SWEET SPOT FOUND: Degree {best_degree}\n")
sys.stdout.write(f">>> Test R-squared: {max(test_scores):.4f}\n")
