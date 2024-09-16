import numpy as np
from scipy import stats

# Data
data = np.array([
    0.745454545, 0.681818182, 0.581818182, 0.690909091, 0.745454545,
    0.872727273, 0.736363636, 0.609090909, 0.554545455, 0.736363636,
    0.972727273, 0.3, 0.918181818, 0.690909091, 0.845454545, 0.945454545,
    0.745454545, 0.9, 0.336363636, 0.963636364, 0.536363636, 1,
    0.581818182, 0.836363636, 0.781818182, 0.854545455
])

mean = np.mean(data)
std_dev = np.std(data, ddof=1)
n = len(data)
se = std_dev / np.sqrt(n)
z_star = stats.norm.ppf(0.975)  # for 95% confidence
margin_of_error = z_star * se

ci_lower = mean - margin_of_error
ci_upper = mean + margin_of_error

print(f"Mean: {mean}")
print(f"Margin of Error: {margin_of_error}")
print(f"Confidence Interval: ({ci_lower}, {ci_upper})")