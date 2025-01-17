import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import argparse
from mpmath import li
import sympy
from functools import lru_cache


@lru_cache(maxsize=None)
def is_prime(num):
    """Check if a number is prime using sympy."""
    return sympy.isprime(num)


def generate_primes(number_to_generate_primes):
    """
    Generate prime-related data for a given number.
    
    Returns:
        secondmult: Count of valid primes for 'number * quotient + 1'.
        primes: List of generated primes.
        multiple_minus_one: Count of valid primes for 'number * quotient - 1'.
        twins_number: Count of twin primes.
    """
    quotient = number_to_generate_primes
    secondmult = 0
    multiple_minus_one = 0
    twins_number = 0
    primes = []

    print(f"Calculating for: {number_to_generate_primes}")
    for index in range(2, number_to_generate_primes + 1):
        if (index & 1 == 0 or quotient & 1 == 0):
            prime_plus_one = index * quotient + 1
            prime_minus_one = index * quotient - 1

            prime1 = prime_plus_one & 1 == 1 and is_prime(prime_plus_one) or prime_plus_one == 2
            prime2 = prime_minus_one & 1 == 1 and is_prime(prime_minus_one) or prime_minus_one == 2

            if prime1:
                secondmult += 1
                primes.append(prime_plus_one)

            if prime2:
                multiple_minus_one += 1
                primes.append(prime_minus_one)

            if prime1 and prime2 and (prime_plus_one - prime_minus_one == 2):
                if (prime_plus_one - 1) % 6 == 0:  # Faster exit for non-twin cases
                    twins_number += 1

    return secondmult, primes, multiple_minus_one, twins_number


def calculate_range(start, end):
    """
    Compute prime-related data for a range of numbers.
    
    Returns:
        A list of tuples (number, result, is_prime_flag).
    """
    results = []
    for number in range(start, end + 1):
        result = generate_primes(number)
        prime_flag = is_prime(number)
        results.append((number, result, prime_flag))
    return results


def calculate(min_interval, max_interval):
    """
    Perform calculations across a range and save results to a DataFrame.
    
    Returns:
        A pandas DataFrame containing results for the range.
    """
    labels = []
    prime_count = []
    prime_count_minus_one_equation = []
    prime_twins_count = []
    is_number_prime = []

    # Define chunks for parallel processing
    chunk_size = 700
    ranges = [(i, min(i + chunk_size - 1, max_interval)) for i in range(min_interval, max_interval + 1, chunk_size)]
    print(f"Processing ranges: {ranges}")

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(calculate_range, start, end) for start, end in ranges]
        for future in as_completed(futures):
            results = future.result()
            for number, result, prime_check in results:
                if number > 0:
                    labels.append(number)
                    prime_count.append(result[0])
                    prime_count_minus_one_equation.append(result[2])
                    prime_twins_count.append(result[3])
                    is_number_prime.append(prime_check)

    # Save results to a DataFrame
    data_to_csv = {
        'Number': labels,
        'Primes +1': prime_count,
        'Primes -1': prime_count_minus_one_equation,
        'Twins': prime_twins_count,
        'isPrime': is_number_prime,
    }
    df_new = pd.DataFrame(data_to_csv).sort_values(by="Number")
    output_file = f'primes_data_{min_interval}_{max_interval}.csv'
    df_new.to_csv(output_file, index=False)
    print(f"Saved results to: {output_file}")
    return df_new


def main():
    """
    Main function to orchestrate the calculations and handle data updates.
    """
    for number in range(122001, 150001, 1000):
        a, b = number, number + 999
        to_read = a - 1

        try:
            # Read the existing data
            datatxt_original = pd.read_csv(f'primes_data_{to_read}.txt')
        except FileNotFoundError:
            datatxt_original = pd.DataFrame(columns=['Number', 'Primes +1', 'Primes -1', 'Twins', 'isPrime'])

        # Perform calculations for two ranges
        start_time = time.time()
        data1 = calculate(a, b)
        elapsed_time = time.time() - start_time
        print(f"Elapsed time for ranges {a}-{b} : {elapsed_time:.2f} seconds")

        # Merge new data with the original
        data_series = [datatxt_original, data1]
        combined_data = pd.concat(data_series).sort_values(by="Number").drop_duplicates()
        combined_data.to_csv(f'primes_data_{b}.txt', index=False)


if __name__ == "__main__":
    main()
