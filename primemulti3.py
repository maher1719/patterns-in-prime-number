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
x_original = filtered_data['Number']
y_original = (filtered_data['Primes +1'] + filtered_data['Primes -1']) / 2

# Create figure and axis objects for both plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Plot the original data points on both plots
ax1.scatter(x_original, y_original, color='blue', label='Original Data', alpha=0.6)
ax2.scatter(x_original, y_original, color='blue', label='Original Data', alpha=0.6)

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

    # Plot regression line for this segment size on both plots
    ax1.plot(x_values, y_pred, label=f'Logarithmic Regression ({segment_size} steps)', linewidth=2)
    ax2.plot(x_values, y_pred, label=f'Logarithmic Regression ({segment_size} steps)', linewidth=2)

# Configure the first plot (Logarithmic Scale)
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('Number (log scale)')
ax1.set_ylabel('Mean of Primes +1 and Primes -1 (log scale)')
ax1.set_title('Logarithmic Regression on Mean Values of Primes Data by Different Segment Sizes')
ax1.legend()
ax1.grid(True)

# Configure the second plot (Linear Scale)
ax2.set_xlabel('Number')
ax2.set_ylabel('Mean of Primes +1 and Primes -1')
ax2.set_title('Linear Regression on Mean Values of Primes Data by Different Segment Sizes')
ax2.legend()
ax2.grid(True)

# Save and show both plots
plt.tight_layout()
file_name='prime_pi_comparison_with_linear_and_log_scales.png'
plt.savefig(file_name)
plt.show()
