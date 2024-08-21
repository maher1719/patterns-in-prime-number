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

# Filter data to start from the value 6 and beyond
start_value = 6
filtered_data = data[data['Number'] >= start_value]

# Define different segment sizes
segment_sizes = [2, 6, 30, 210, 2310]

# Prepare lists to hold segment means and corresponding x values for different segment sizes
plt.figure(figsize=(12, 8))
plt.scatter(filtered_data['Number'], 
            (filtered_data['Primes +1'] + filtered_data['Primes -1']) / 2, 
            color='blue', label='Original Data', alpha=0.6)

# Calculate means and perform regression for each segment size
for segment_size in segment_sizes:
    num_segments = len(filtered_data) // segment_size

    mean_values = []
    x_values = []

    for i in range(num_segments):
        start_idx = i * segment_size
        end_idx = start_idx + segment_size
        segment = filtered_data.iloc[start_idx:end_idx]
        mean_value = (segment['Primes +1'].mean() + segment['Primes -1'].mean()) / 2
        mean_values.append(mean_value)
        x_values.append((filtered_data['Number'].iloc[start_idx] + filtered_data['Number'].iloc[end_idx - 1]) / 2)  # Midpoint of the segment

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

    # Plot regression line for this segment size
    plt.plot(x_values, y_pred, label=f'Logarithmic Regression ({segment_size} steps)', linewidth=2)

    # Output regression coefficients for this segment size
    print(f'Segment Size {segment_size} - Coefficients:', poly_reg.coef_, 'Intercept:', poly_reg.intercept_)

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Number (log scale)')
plt.ylabel('Mean of Primes +1 and Primes -1 (log scale)')
plt.title('Logarithmic Regression on Mean Values of Primes Data by Different Segment Sizes')
plt.legend()
plt.grid(True)
file_name='prime_pi_comparison_multiple_segment_sizes_with_original_points.png'
plt.savefig(file_name)
plt.show()
