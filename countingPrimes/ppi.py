import numpy as np
from scipy.optimize import fsolve
from sympy import primepi

# Define the function to solve
def equation(x, a, pi_a):
    # Calculate the argument for the logarithm
    argument = a - a / (x * np.pi / 2)
    
    # Ensure argument is positive and non-zero for the logarithm
    if argument <= 0:
        return np.nan  # Logarithm is not defined for non-positive values
    
    # Compute the value of the equation
    result = pi_a - a / np.log(argument)
    
    # Return as float
    return float(result)

# Example value for a
a = 10000000000  # Adjust as needed

# Calculate pi(a) using SymPy
pi_a = primepi(a)

# Numerical solution for x
x_initial_guess = 1
x_solution = fsolve(equation, x_initial_guess, args=(a, pi_a))

print(f"Value of x: {x_solution[0]}")
