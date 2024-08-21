import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd
import numpy as np

# Load the CSV file
file_path = 'prime_data2.csv'
data = pd.read_csv(file_path)

# Display the first few rows of the data to understand its structure
data.head()
#data=data[data["Number"]>10**4]
# Filter data to start from the value 6 and beyond
start_value = 6
filtered_data = data[data['Number'] >= start_value]

# Define the size of the segments
segment_size = 6

# Calculate the number of segments
num_segments = len(filtered_data) // segment_size

# Prepare lists to hold segment means and corresponding x values
mean_values = []
x_values = []

# Calculate means for each segment
for i in range(num_segments):
    start_idx = i * segment_size
    end_idx = start_idx + segment_size
    segment = filtered_data.iloc[start_idx:end_idx]
    mean_value = (segment['Primes +1'].mean() + segment['Primes -1'].mean()) / 2
    mean_values.append(mean_value)
    x_values.append((start_idx + end_idx) / 2)  # Midpoint of the segment

# Convert to numpy arrays
x_values = np.array(x_values)
mean_values = np.array(mean_values)

# Perform logarithmic regression
log_x = np.log10(x_values).reshape(-1, 1)
log_y = np.log10(mean_values).reshape(-1, 1)

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
plt.scatter(x_values, mean_values, color='blue', label='Mean Values')
plt.plot(x_values, y_pred, color='red', label='Logarithmic Regression', linewidth=2)
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Number (log scale)')
plt.ylabel('Mean of Primes +1 and Primes -1 (log scale)')
plt.title('Logarithmic Regression on Mean Values of Primes Data by '+str(segment_size)+' steps')
plt.legend()
plt.grid(True)
file_name='prime_pi_comparison by segement size of '+str(segment_size)+'.png'
plt.savefig(file_name)
plt.show()

# Output the regression coefficients
log_regression_coefficients = poly_reg.coef_
log_regression_intercept = poly_reg.intercept_
print(log_regression_coefficients, log_regression_intercept)
