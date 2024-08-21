import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.optimize import curve_fit

import pandas as pd
import numpy as np

# Load the CSV file
file_path = 'prime_data2.csv'
data = pd.read_csv(file_path)

# Display the first few rows of the data to understand its structure
data.head()

# Extract relevant data
x_values = data['Number']
y_values = (data['Primes +1'] + data['Primes -1']) / 2

# Perform logarithmic regression
log_x = np.log10(x_values).values.reshape(-1, 1)
log_y = np.log10(y_values).values.reshape(-1, 1)

# Fit a polynomial regression model
poly = PolynomialFeatures(degree=1)
X_poly = poly.fit_transform(log_x)
poly_reg = LinearRegression()
poly_reg.fit(X_poly, log_y)

# Predict using the model
log_y_pred = poly_reg.predict(X_poly)

# Transform back to original scale
y_pred = 10 ** log_y_pred

# Plot the results
plt.figure(figsize=(12, 6))
plt.scatter(x_values, y_values, color='blue', label='Actual Values')
plt.plot(x_values, y_pred, color='red', label='Logarithmic Regression', linewidth=2)
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Number (log scale)')
plt.ylabel('Mean of Primes +1 and Primes -1 (log scale)')
plt.title('Logarithmic Regression on Prime Data')
plt.legend()
plt.grid(True)
plt.show()

# Output the regression coefficients
log_regression_coefficients = poly_reg.coef_
log_regression_intercept = poly_reg.intercept_
print(log_regression_coefficients, log_regression_intercept)
