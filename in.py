import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress
import scipy.integrate as integrate

# Function to compute all primes up to a maximum value using the Sieve of Eratosthenes
def sieve_of_eratosthenes(max_num):
    is_prime = [True] * (max_num + 1)
    is_prime[0] = is_prime[1] = False  # 0 and 1 are not primes
    p = 2
    while (p * p <= max_num):
        if (is_prime[p] == True):
            for i in range(p * p, max_num + 1, p):
                is_prime[i] = False
        p += 1
    primes = [p for p in range(max_num + 1) if is_prime[p]]
    return primes

# Precompute primes up to a reasonable upper bound
max_x = 1000000
primes = sieve_of_eratosthenes(int(max_x * 1.5))  # Upper bound adjusted to ensure coverage

# Function to calculate the prime counting function π(x)
def prime_counting_function(x):
    return np.sum(np.array(primes) <= x)

# Function to calculate the logarithmic integral Li(x)
def logarithmic_integral(x):
    if x < 2:
        return 0
    t = np.linspace(2, x, 1000)

    return np.round(np.trapezoid(1 / np.log(t), t))

# Define the range [a, b]
a = 5  # Start of the range
b = 30  # End of the range

# Generate sample data
x_values = np.linspace(a, max_x, 100000)
li_values = np.array([logarithmic_integral(x) for x in x_values])
pi_values = np.array([prime_counting_function(x) for x in x_values])
diff_values = li_values / pi_values

# Perform linear regression on differences
slope, intercept, r_value, p_value, std_err = linregress(x_values, diff_values)
print(f"Regression Line Equation: y = {slope:.32f}x + {intercept:.22f}")
print(f"R-squared Value: R² = {r_value**2:.32f}")
print(f"std_err: R² = {std_err:.32f}")
print(f"p_val: R² = {p_value:.32f}")
# Define the regression line function
def regression_line(x):
    return slope * x + intercept

# Create traces for Plotly
trace_li = go.Scatter(x=x_values, y=li_values, mode='lines+markers', name='Logarithmic Integral Li(x)')
trace_pi = go.Scatter(x=x_values, y=pi_values, mode='lines+markers', name='Prime Counting Function π(x)')
trace_diff = go.Scatter(x=x_values, y=diff_values, mode='markers', name='li(x) - π(x)')
trace_regression = go.Scatter(x=x_values, y=regression_line(x_values), mode='lines', name='Regression Line')

# Create the figure
fig = go.Figure()
fig.add_trace(trace_li)
fig.add_trace(trace_pi)
fig.add_trace(trace_diff)
fig.add_trace(trace_regression)

# Update layout
fig.update_layout(
    title="Interactive Plot of Li(x), π(x), and Their Differences",
    xaxis_title="x",
    yaxis_title="Value",
    showlegend=True
)

# Display the equation of the regression line
equation_text = f"Regression Line: y = {slope:.2f}x + {intercept:.2f}"
fig.add_annotation(
    x=0.5, y=-0.2, xref="paper", yref="paper",
    text=equation_text, showarrow=False,
    font=dict(size=14, color="black"),
    align="center"
)

# Add a note on the plot showing R-squared value for reference
r_squared_text = f"R² = {r_value**2:.2f}"
fig.add_annotation(
    x=0.5, y=-0.3, xref="paper", yref="paper",
    text=r_squared_text, showarrow=False,
    font=dict(size=14, color="black"),
    align="center"
)

# Show the plot
fig.show()
