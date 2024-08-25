import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from sympy import isprime

# Function to generate prime numbers based on the expressions p = ax + 1 and p = ax - 1
def generate_primes_sum(a_range, x_range):
    prime_sums = []
    for x in x_range:
        sum_p = 0
        for a in a_range:
            p1 = a * x + 1
            p2 = a * x - 1
            if isprime(p1):
                sum_p += p1
            if isprime(p2):
                sum_p += p2
        if sum_p > 0:  # Only include points where at least one prime was found
            prime_sums.append((x, sum_p))
    return prime_sums

# Define the range for 'a' and 'x'
a_range = range(1, 100)
x_range = range(3, 31001)

# Generate data for the sum of primes
prime_sums_data = generate_primes_sum(a_range, x_range)

# Convert data to DataFrame
df = pd.DataFrame(prime_sums_data, columns=['x', 'prime_sum'])

# Define segments for logarithmic regression based on multiples of 6
start = 2310
end = 31000
segments = [(i, i + 2310 - 1) for i in range(start, end, 2310)]

# Function to apply logarithmic regression
def log_regression(df_segment):
    X = np.log(df_segment['x'])
    X = sm.add_constant(X)  # Add constant term for intercept
    model = sm.OLS(df_segment['prime_sum'], X).fit()
    return model.params[1], model.params[0], model.rsquared, model.pvalues[1]  # slope (a), intercept (b), R^2, p-value

# Initialize results list
results = []

# Segment the data and perform logarithmic regression
for (start, end) in segments:
    df_segment = df[(df['x'] >= start) & (df['x'] <= end)]
    if not df_segment.empty:
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

# Correct the original log regression using the secondary regression results
df['log_x'] = np.log(df['x'])
df['corrected_slope'] = np.exp(slope_log_regression.predict(sm.add_constant(df['log_x'])))
df['corrected_intercept'] = np.exp(intercept_log_regression.predict(sm.add_constant(df['log_x'])))

# Calculate the corrected sum of primes using the corrected slope and intercept
df['corrected_prime_sum'] = df['corrected_slope'] * np.log(df['x']) + df['corrected_intercept']

# Visualize the original log regression, corrected regression, and segmented log regression
plt.figure(figsize=(14, 8))

# Original data and regression line
X = np.log(df['x'])
Y = df['prime_sum']
X_with_const = sm.add_constant(X)
original_model = sm.OLS(Y, X_with_const).fit()
plt.scatter(df['x'], df['prime_sum'], color='blue', s=10, label='Original Data (Sum of Primes)')
plt.plot(df['x'], original_model.predict(X_with_const), color='red', label='Original Log Regression')

# Corrected regression line
plt.plot(df['x'], df['corrected_prime_sum'], color='green', label='Corrected Log Regression')

# Optional: Segmented regression lines

plt.xlabel('x')
plt.ylabel('Sum of Primes p')
plt.legend()
plt.title('Original, Corrected, and Segmented Logarithmic Regression (Sum of Primes)')

plt.show()
