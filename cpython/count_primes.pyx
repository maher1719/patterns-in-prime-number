# Import necessary libraries
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Declare Cython types
cimport numpy as cnp
from libc.math cimport log

# Logarithmic model with type annotations
def log_model(cnp.ndarray[double] x, double a, double b) -> cnp.ndarray:
    cdef cnp.ndarray[double] result = np.empty_like(x)  # Allocate array for result
    cdef int i
    for i in range(x.shape[0]):
        result[i] = a / log(x[i]) + b
    return result

# Linear model with type annotations
def linear_model(cnp.ndarray[double] x, double a, double b) -> cnp.ndarray:
    cdef cnp.ndarray[double] result = np.empty_like(x)  # Allocate array for result
    cdef int i
    for i in range(x.shape[0]):
        result[i] = a * x[i] + b
    return result

# Function to plot primes and perform curve fitting
def plot_primes(str column):
    datatxt_original = pd.read_csv('../primes.txt').drop_duplicates()
    # Your original logic
    cdef list range_prime = []
    cdef int i, range_max
    for i in range(10, 60000, 100):
        range_prime.append(i)

    print(range_prime)
    ranging = []
    for range_max in range_prime:
        number_counts_primes_plus_one = datatxt_original[column].value_counts().sort_index()
        X = number_counts_primes_plus_one.index
        Y = number_counts_primes_plus_one.values
        ranging.append([X, Y])

    cdef int j
    ratio_primes_max_X = []
    ratio_primes_max_Y = []
    for j in range(len(ranging)):
        ratio_primes_max_X.append(range_prime[j])
        ratio_primes_max_Y.append(range_prime[j] / max(ranging[j][1]))

    # Plot using Plotly
    fig2 = go.Figure()

    # Add the original data counts
    fig2.add_trace(go.Scatter(
        x=ratio_primes_max_X,
        y=ratio_primes_max_Y,
        mode='lines+markers',
        name='Original Counts',
        marker=dict(color='red', size=8, opacity=0.5),
    ))

    fig2.update_layout(
        title=f'Ratio n/max(Y) without adjust to range 52000 and without Y squared for {column}',
        xaxis_title='n',
        yaxis_title='ratio',
        legend=dict(x=1, y=0.9),
        template='plotly_white'
    )
    fig2.show()

    # Perform curve fitting
    cdef cnp.ndarray[double] n = np.array(ratio_primes_max_X, dtype=np.float64)
    cdef cnp.ndarray[double] y = np.array(ratio_primes_max_Y, dtype=np.float64)

    popt_log, _ = curve_fit(log_model, n, y)
    popt_linear, _ = curve_fit(linear_model, n, y)

    # Generate points for the fitted curve
    cdef cnp.ndarray[double] n_fit = np.linspace(min(n), max(n), 100)
    cdef cnp.ndarray[double] y_fit_log = log_model(n_fit, *popt_log)
    cdef cnp.ndarray[double] y_fit_linear = linear_model(n_fit, *popt_linear)

    # Plot the original data and the fitted curve for log model
    plt.scatter(n, y, color='red', label='Data')
    plt.plot(n_fit, y_fit_log, label=f'Fit: a / log(n) + b', color='blue')
    plt.xlabel('n')
    plt.ylabel('max(Y)/n')
    plt.title(f'Curve Fitting: max(Y)/n vs n (Log Model) for {column}')
    plt.legend()
    plt.show()

    # Plot the original data and the fitted curve for linear model
    plt.scatter(n, y, color='red', label='Data')
    plt.plot(n_fit, y_fit_linear, label=f'Fit: a*n + b', color='blue')
    plt.xlabel('n')
    plt.ylabel('max(Y)/n')
    plt.title(f'Curve Fitting: n/max(Y) vs n (Linear Model) for {column}')
    plt.legend()
    plt.show()

    # Calculate and display R-squared values
    cdef cnp.ndarray[double] y_pred_log = log_model(n, *popt_log)
    cdef double ss_res_log = np.sum((y - y_pred_log) ** 2)
    cdef double ss_tot_log = np.sum((y - np.mean(y)) ** 2)
    cdef double r_squared_log = 1 - (ss_res_log / ss_tot_log)
    print(f"R-squared (Log Model): {r_squared_log}")

    cdef cnp.ndarray[double] y_pred_linear = linear_model(n, *popt_linear)
    cdef double ss_res_linear = np.sum((y - y_pred_linear) ** 2)
    cdef double ss_tot_linear = np.sum((y - np.mean(y)) ** 2)
    cdef double r_squared_linear = 1 - (ss_res_linear / ss_tot_linear)
    print(f"R-squared (Linear Model): {r_squared_linear}")

# Call the function with your columns
plot_primes("Primes +1")
plot_primes("Primes -1")
plot_primes("Twins")
