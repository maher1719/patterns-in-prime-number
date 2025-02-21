import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def smooth_data(x_data, y_data, group_size):
    """
    Group data into intervals and calculate the mean of each group.
    """
    num_groups = max(1, len(x_data) // group_size)  # Ensure at least one group
    smoothed_x, smoothed_y = [], []
    
    for i in range(num_groups):
        group_x = x_data[i * group_size: (i + 1) * group_size]
        group_y = y_data[i * group_size: (i + 1) * group_size]
        if len(group_x) > 0:  # Avoid empty groups
            smoothed_x.append(np.mean(group_x))
            smoothed_y.append(np.mean(group_y))
    
    return np.array(smoothed_x), np.array(smoothed_y)

def find_threshold(x_data, y_data):
    """
    Find the threshold where the first derivative becomes negative (decreasing).
    """
    first_derivative = np.diff(y_data)
    decreasing_indices = np.where(first_derivative < 0)[0]
    if len(decreasing_indices) == 0:
        return x_data[-1]  # Return max if no threshold is found
    return x_data[decreasing_indices[0]]

def plot_data_with_threshold(x_data, y_data, threshold, title):
    """
    Plot the data and mark the threshold point.
    """
    plt.figure(figsize=(8, 5))
    plt.plot(x_data, y_data, label="Data")
    plt.axvline(x=threshold, color='red', linestyle='--', label=f"Threshold at x={threshold}")
    plt.legend()
    plt.xlabel("X Data")
    plt.ylabel("Y Data")
    plt.title(title)
    plt.show()

def find_best_divid(x_data, y_data, min_divid=10, max_divid=100):
    """
    Find the best divide value by maximizing the detected threshold.
    """
    best_divid, best_threshold = None, 0
    for divid in range(min_divid, max_divid + 1):
        group_size = max(1, x_data[-1] // divid)
        smoothed_x, smoothed_y = smooth_data(x_data, y_data, group_size)
        threshold = find_threshold(smoothed_x, smoothed_y)
        if threshold > best_threshold:
            best_threshold = threshold
            best_divid = divid
    return best_divid, best_threshold

# Load data
datatxt_all = pd.read_csv('primes_data_150000.txt', low_memory=False)

for column in ['Primes +1', 'Primes -1', 'Twins']:
    data_counts = datatxt_all[column].value_counts().sort_index()
    x_data = data_counts.index.to_numpy()
    y_data = data_counts.values
    
    best_divid, threshold = find_best_divid(x_data, y_data)
    print(f"Best divid for {column}: {best_divid}, Calculated Threshold: {threshold}")
    
    group_size = max(1, x_data[-1] // best_divid)
    smoothed_x, smoothed_y = smooth_data(x_data, y_data, group_size)
    plot_data_with_threshold(smoothed_x, smoothed_y, threshold, f"{column} Data with Threshold smoothed")
    plot_data_with_threshold(x_data, y_data, threshold, f"{column} Data with Threshold")
