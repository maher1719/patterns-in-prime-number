import numpy as np
from scipy.optimize import fsolve
from sympy import primepi
import matplotlib.pyplot as plt

# Define the function to solve
def equation(x, a, pi_a):
    # Calculate the argument for the logarithm
    argument = a - a / (x * np.pi / 2)
    # Ensure argument is positive and non-zero for the logarithm
    if argument <= 0:
        return np.nan  # Logarithm is not defined for non-positive values
    # Compute the value of the equation
    result = pi_a - a / np.log(argument)
    return float(result)

# Define the range and step size for a
#a_start = 1000000000
#a_end = 20000000000
#a_step = 5000000000


a_start = 10000000000
a_end = 100000000000
a_step = 10000000000


# Generate values for a
a_values = np.arange(a_start, a_end + a_step, a_step)

# Arrays to hold the results
x_solutions = []

# Compute x for each value of a
for a in a_values:
    pi_a = primepi(a)
    # Initial guess for x
    x_initial_guess = 1
    # Numerical solution for x
    x_solution, = fsolve(equation, x_initial_guess, args=(a, pi_a))
    x_solutions.append(x_solution)

# Plotting the results
plt.figure(figsize=(12, 6))
plt.plot(a_values, x_solutions, marker='o', linestyle='-', color='b')
plt.xlabel('a')
plt.ylabel('x')
plt.title('Plot of x vs. a')
plt.grid(True)
plt.show()
