import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from sympy import isprime

# Function to generate primes from the expressions p = ax + 1 and p = ax - 1
def generate_primes(a_range, x_range):
    primes_data = []
    for a in a_range:
        for x in x_range:
            p1 = a * x + 1
            p2 = a * x - 1
            if isprime(p1):
                primes_data.append((a, x, p1))
            if isprime(p2):
                primes_data.append((a, x, p2))
    return primes_data

# Generate data for a specified range of a and x
a_range = range(1, 100)
x_range = range(3, 31001)
primes_data = generate_primes(a_range, x_range)

# Convert data to DataFrame for easier manipulation
df = pd.DataFrame(primes_data, columns=['a', 'x', 'p'])

# Function to apply logarithmic regression
def log_regression(df_segment):
    X = np.log(df_segment['x'])
    X = sm.add_constant(X)  # Add constant term for intercept
    model = sm.OLS(df_segment['p'], X).fit()
    return model.params[1], model.params[0], model.rsquared, model.pvalues[1]  # slope (a), intercept (b), R^2, p-value

# Segment the data and perform logarithmic regression
segments = [(1000, 5000), (5001, 10000), (10001, 20000), (20001, 31000)]
results = []

for (start, end) in segments:
    df_segment = df[(df['x'] >= start) & (df['x'] <= end)]
    slope, intercept, r_squared, p_value = log_regression(df_segment)
    results.append((start, end, slope, intercept, r_squared, p_value))

# Convert results to DataFrame
results_df = pd.DataFrame(results, columns=['start_x', 'end_x', 'slope', 'intercept', 'R^2', 'p-value'])

# Perform secondary regression on slope and intercept from different segments
slope_log_regression = sm.OLS(np.log(results_df['slope']), sm.add_constant(np.log(results_df['start_x']))).fit()
intercept_log_regression = sm.OLS(np.log(results_df['intercept']), sm.add_constant(np.log(results_df['start_x']))).fit()

# Print out the regression results
print("Segmented Logarithmic Regression Results:")
print(results_df)
print("\nSecondary Regression on Slope:")
print(slope_log_regression.summary())
print("\nSecondary Regression on Intercept:")
print(intercept_log_regression.summary())

# Visualize the original log regression and segmented log regression
plt.figure(figsize=(14, 8))

# Original data and regression line
X = np.log(df['x'])
Y = df['p']
X_with_const = sm.add_constant(X)
original_model = sm.OLS(Y, X_with_const).fit()
plt.scatter(df['x'], df['p'], color='blue', s=10, label='Original Data')
plt.plot(df['x'], original_model.predict(X_with_const), color='red', label='Original Log Regression')

# Segmented regression lines
colors = ['orange', 'green', 'purple', 'brown']
for i, (start, end) in enumerate(segments):
    df_segment = df[(df['x'] >= start) & (df['x'] <= end)]
    X_segment = np.log(df_segment['x'])
    Y_segment = df_segment['p']
    X_segment_with_const = sm.add_constant(X_segment)
    model_segment = sm.OLS(Y_segment, X_segment_with_const).fit()
    plt.plot(df_segment['x'], model_segment.predict(X_segment_with_const), color=colors[i], label=f'Segment {start}-{end}')

plt.xlabel('x')
plt.ylabel('Prime p')
plt.legend()
plt.title('Original and Segmented Logarithmic Regression')

# Further analysis and plotting of secondary regressions
plt.figure(figsize=(14, 8))

# Plot secondary regression on slope
plt.subplot(2, 1, 1)
plt.scatter(np.log(results_df['start_x']), np.log(results_df['slope']), color='blue', s=50, label='Log(Slope)')
plt.plot(np.log(results_df['start_x']), slope_log_regression.predict(sm.add_constant(np.log(results_df['start_x']))), color='red', label='Secondary Log Regression (Slope)')
plt.xlabel('Log(Start x)')
plt.ylabel('Log(Slope)')
plt.legend()
plt.title('Secondary Logarithmic Regression on Slope')

# Plot secondary regression on intercept
plt.subplot(2, 1, 2)
plt.scatter(np.log(results_df['start_x']), np.log(results_df['intercept']), color='blue', s=50, label='Log(Intercept)')
plt.plot(np.log(results_df['start_x']), intercept_log_regression.predict(sm.add_constant(np.log(results_df['start_x']))), color='red', label='Secondary Log Regression (Intercept)')
plt.xlabel('Log(Start x)')
plt.ylabel('Log(Intercept)')
plt.legend()
plt.title('Secondary Logarithmic Regression on Intercept')

plt.tight_layout()
plt.show()
