import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd
import numpy as np

# Load the CSV file
file_path = 'prime_data2.csv'
data = pd.read_csv(file_path)

# Filter data to start from the value 6 and beyond
start_value = 6
filtered_data = data[data['Number'] >= start_value]

# Define different segment sizes
segment_sizes = [2, 6, 30, 210, 2310]

# Create figures for the different plots
fig_log, ax_log = plt.subplots(figsize=(12, 6))
fig_linear, ax_linear = plt.subplots(figsize=(12, 6))
fig_base6, ax_base6 = plt.subplots(figsize=(12, 6))

# Plot the original data points on all plots
x_original = filtered_data['Number']
y_original = (filtered_data['Primes +1'] + filtered_data['Primes -1']) / 2

ax_log.scatter(x_original, y_original, color='blue', label='Original Data', alpha=0.6)
ax_linear.scatter(x_original, y_original, color='blue', label='Original Data', alpha=0.6)
ax_base6.scatter(x_original, y_original, color='blue', label='Original Data', alpha=0.6)

# Calculate means and perform regression for each segment size
for segment_size in segment_sizes:
    # Group data by the segment size
    grouped = filtered_data.groupby(filtered_data.index // segment_size)
    
    # Calculate the mean of each group for Primes +1 and Primes -1
    mean_values = grouped[['Primes +1', 'Primes -1']].mean().mean(axis=1)
    
    # Calculate the midpoint for x values in each segment
    x_values = grouped['Number'].mean()

    # Perform logarithmic regression
    log_x = np.log10(x_values).values.reshape(-1, 1)
    log_y = np.log10(mean_values).values.reshape(-1, 1)

    # Fit a polynomial regression model
    poly = PolynomialFeatures(degree=1)
    X_poly = poly.fit_transform(log_x)
    poly_reg = LinearRegression()
    poly_reg.fit(X_poly, log_y)

    # Predict using the model
    log_y_pred = poly_reg.predict(X_poly)

    # Transform back to original scale
    y_pred = 10 ** log_y_pred

    # Plot regression line for this segment size on each plot
    ax_log.plot(x_values, y_pred, label=f'Logarithmic Regression ({segment_size} steps)', linewidth=2)
    ax_linear.plot(x_values, y_pred, label=f'Logarithmic Regression ({segment_size} steps)', linewidth=2)

    # Base-6 logarithmic regression
    log_x_base6 = np.log(x_values) / np.log(6)
    log_y_base6 = np.log(mean_values) / np.log(6)
    log_x_base6 = log_x_base6.values.reshape(-1, 1)
    log_y_base6 = log_y_base6.values.reshape(-1, 1)

    # Fit a polynomial regression model with base-6 logarithms
    X_poly_base6 = poly.fit_transform(log_x_base6)
    poly_reg_base6 = LinearRegression()
    poly_reg_base6.fit(X_poly_base6, log_y_base6)

    # Predict using the base-6 model
    log_y_pred_base6 = poly_reg_base6.predict(X_poly_base6)

    # Transform back to original scale
    y_pred_base6 = 6 ** log_y_pred_base6

    # Plot regression line for this segment size on the base-6 plot
    ax_base6.plot(x_values, y_pred_base6, label=f'Base-6 Logarithmic Regression ({segment_size} steps)', linewidth=2)

# Configure the logarithmic scale plot
ax_log.set_xscale('log')
ax_log.set_yscale('log')
ax_log.set_xlabel('Number (log scale)')
ax_log.set_ylabel('Mean of Primes +1 and Primes -1 (log scale)')
ax_log.set_title('Logarithmic Regression on Mean Values of Primes Data by Different Segment Sizes')
ax_log.legend()
ax_log.grid(True)
fig_log.savefig('prime_pi_comparison_log_scale.png')

# Configure the linear scale plot
ax_linear.set_xlabel('Number')
ax_linear.set_ylabel('Mean of Primes +1 and Primes -1')
ax_linear.set_title('Linear Regression on Mean Values of Primes Data by Different Segment Sizes')
ax_linear.legend()
ax_linear.grid(True)
fig_linear.savefig('prime_pi_comparison_linear_scale.png')

# Configure the base-6 logarithmic scale plot
ax_base6.set_xscale('log', base=6)
ax_base6.set_yscale('log', base=6)
ax_base6.set_xlabel('Number (base-6 log scale)')
ax_base6.set_ylabel('Mean of Primes +1 and Primes -1 (base-6 log scale)')
ax_base6.set_title('Base-6 Logarithmic Regression on Mean Values of Primes Data by Different Segment Sizes')
ax_base6.legend()
ax_base6.grid(True)
fig_base6.savefig('prime_pi_comparison_base6_scale.png')

plt.show()
