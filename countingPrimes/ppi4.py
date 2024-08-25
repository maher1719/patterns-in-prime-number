import numpy as np
from scipy.optimize import fsolve, curve_fit
from sympy import primepi
import matplotlib.pyplot as plt
import mpmath
import csv

# Define the function to solve
def equation(x, a, pi_a,rg):
    argument = a - a / (x * np.pi / 2)
    if argument <= 0:
        return np.nan
    result = pi_a - a / np.log(argument)
    
    return float(result)

# Define the logarithmic model for regression
def log_model(a, alpha, beta):
    return alpha * np.log(a) + beta

# Define the range and step size for a
a_start = 1000000000
a_end = 20000000000
a_step = 1000000000

# Generate values for a
a_values = np.arange(a_start, a_end + a_step, a_step)

# Arrays to hold the results
x_solutions = []
f_values = []
abs_li_minus_pi_values = []
abs_f_minus_pi_values = []

# Compute x for each value of a
for a in a_values:
    pi_a = primepi(a)
    x_initial_guess = 1
    
    # Solve for x using the initial guess and a placeholder rg value
    x_solution, = fsolve(equation, x_initial_guess, args=(a, pi_a, 1))
    print(a,x_solution)
    x_solutions.append(x_solution)
    
    # Calculate the modified f(x) using the solution x
    if x_solution > 0:  # Ensure x_solution is positive
        f_x = a / np.log(a - a / (x_solution * np.pi / 2))
    else:
        f_x = np.nan
    
    f_values.append(f_x)
    
    # Calculate Li(x) using mpmath
    li_x = mpmath.li(a)
    
    abs_li_minus_pi = np.abs(li_x - pi_a)
    abs_f_minus_pi = np.abs(f_x - pi_a)
    
    abs_li_minus_pi_values.append(abs_li_minus_pi)
    abs_f_minus_pi_values.append(abs_f_minus_pi)

# Perform logarithmic regression on x_solutions
a_values_non_nan = np.array(a_values)
x_solutions_non_nan = np.array(x_solutions)
params, _ = curve_fit(log_model, a_values_non_nan, x_solutions_non_nan)

# Extract the regression parameters
alpha, beta = params
print(f"Logarithmic Regression Equation for x_solutions: x = {alpha:.5f} * log(a) + {beta:.5f}")

# Calculate the corrected x values using the regression model
x_corrected_values = log_model(a_values_non_nan, *params)

# Save the results to a CSV file
csv_filename = "results.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['a', 'x_solution', 'f(x)', 'f_corrected(x)', '|Li(x) - pi(x)|', '|f(x) - pi(x)|'])
    for a, x_solution, f_x, li_minus_pi, f_minus_pi in zip(a_values, x_solutions, f_values, abs_li_minus_pi_values, abs_f_minus_pi_values):
        writer.writerow([a, x_solution, f_x, np.nan, li_minus_pi, f_minus_pi])

print(f"Results saved to {csv_filename}")

# Plotting the results for x vs. a and corrected x values
plt.figure(figsize=(12, 6))
plt.plot(a_values, x_solutions, marker='o', linestyle='-', color='b', label='x vs. a')
#plt.plot(a_values, x_corrected_values, marker='o', linestyle='--', color='g', label='Corrected x using log regression')
plt.xlabel('a')
plt.ylabel('x / Corrected x')
plt.title('Plot of x and Corrected x vs. a')
plt.legend()
plt.grid(True)

# Plotting |Li(x) - pi(x)| and |f(x) - pi(x)| on the same graph
plt.figure(figsize=(12, 6))
plt.plot(a_values, abs_li_minus_pi_values, marker='o', linestyle='-', color='r', label='|Li(x) - pi(x)|')
plt.plot(a_values, abs_f_minus_pi_values, marker='o', linestyle='-', color='g', label='|f(x) - pi(x)|')
plt.xlabel('a (steps)')
plt.ylabel('Absolute Differences')
plt.title('Comparison of |Li(x) - pi(x)| and |f(x) - pi(x)|')
plt.legend()
plt.grid(True)
plt.show()
