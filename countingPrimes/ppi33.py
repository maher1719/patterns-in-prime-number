import numpy as np
from scipy.optimize import fsolve
from sympy import primepi
import matplotlib.pyplot as plt
import mpmath
import csv

# Define the function to solve
def equation(x, a, pi_a):
    argument = a - a / (x * np.pi / 2)
    if argument <= 0:
        return np.nan
    result = pi_a - a / np.log(argument)
    return float(result)

# Define the range and step size for a
a_start = 1600000
a_end = 60000000
a_step = 50000

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
    x_solution, = fsolve(equation, x_initial_guess, args=(a, pi_a))
    print(a, x_solution)
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

# Perform linear regression on x_solutions based on a_values
slope, intercept = np.polyfit(a_values, x_solutions, 1)
print(f"Linear regression equation: x = {slope:.15f} * a + {intercept:.15f}")

# Define the transformed function
def transformed_function(a, slope, intercept):
    x = slope * a + intercept
    if a - (0.6366197724 * a) / x <= 0:
        return np.nan
    pi=np.pi
    
    return primepi(a) - (a / np.log(a - (0.6366197724 * a) / x))

# Compute values for the transformed function
transformed_values = [transformed_function(a, slope, intercept) for a in a_values]

# Save the results to a CSV file
"""
csv_filename = "results2.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['a', 'x_solution', 'f(x)', '|Li(x) - pi(x)|', '|f(x) - pi(x)|'])
    for a, x_solution, f_x, li_minus_pi, f_minus_pi in zip(a_values, x_solutions, f_values, abs_li_minus_pi_values, abs_f_minus_pi_values):
        writer.writerow([a, x_solution, f_x, li_minus_pi, f_minus_pi])

print(f"Results saved to {csv_filename}")
"""

# Plotting the results for x vs. a
plt.figure(figsize=(12, 6))
plt.plot(a_values, x_solutions, marker='o', linestyle='-', color='b', label='x solutions')
plt.xlabel('a')
plt.ylabel('x')
plt.title('Plot of x vs. a')
plt.grid(True)

# Plot the linear regression line
plt.figure(figsize=(12, 6))
plt.plot(a_values, slope * a_values + intercept,marker='o', linestyle='--', color='b', label='Linear fit')
plt.plot(a_values, x_solutions, linestyle='-',marker='.', color='r', label='Linear fit')
plt.legend()


# Plotting |Li(x) - pi(x)| and |f(x) - pi(x)| on the same graph
plt.figure(figsize=(12, 6))
plt.plot(a_values, abs_li_minus_pi_values, marker='o', linestyle='-', color='r', label='|Li(x) - pi(x)|')
plt.plot(a_values, abs_f_minus_pi_values, marker='o', linestyle='-', color='g', label='|f(x) - pi(x)|')
plt.xlabel('a (steps)')
plt.ylabel('Absolute Differences')
plt.title('Comparison of |Li(x) - pi(x)| and |f(x) - pi(x)|')
plt.legend()
plt.grid(True)


# Plot the transformed function
plt.figure(figsize=(12, 6))
plt.plot(a_values, transformed_values, marker='o', linestyle='-', color='m', label='Transformed function')
plt.xlabel('a')
plt.ylabel('Transformed Value')
plt.title('Plot of Transformed Function')
plt.grid(True)
plt.legend()
plt.figure(figsize=(12, 6))
plt.plot(a_values, transformed_values, marker='o', linestyle='-', color='m', label='Transformed function')
plt.xlabel('a')
plt.ylabel('Transformed Value')
plt.title('Plot of Transformed Function')
plt.grid(True)
plt.legend()
plt.show()

