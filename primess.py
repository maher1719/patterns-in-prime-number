import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import argparse

# Prime cache
prime_cache = {}

def is_prime(num):
    """Check if a number is prime using the Miller-Rabin primality test."""
    if num in prime_cache:
        return prime_cache[num]
    if num <= 1:
        return False
    if num <= 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    s = 0
    d = num - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    def miller_rabin_test(a, s, d, n):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        while s > 1:
            x = pow(x, 2, n)
            s -= 1
            if x == n - 1:
                return True
        return False
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        if num == a:
            return True
        if not miller_rabin_test(a, s, d, num):
            prime_cache[num] = False
            return False
    prime_cache[num] = True
    return True

def addition(number_to_generate_primes):
    """Generate primes based on the given number."""
    quotient = math.floor(number_to_generate_primes)
    secondmult = 0
    thirdmult = 0
    primes = []
    multiple_minus_one = 0
    twins_number = 0

    for index in range(2, number_to_generate_primes + 1):
        prime_plus_one = index * quotient + 1
        prime_minus_one = index * quotient - 1

        if is_prime(prime_plus_one):
            secondmult += 1
            primes.append(prime_plus_one)

        if is_prime(prime_minus_one):
            multiple_minus_one += 1
            primes.append(prime_minus_one)

        if prime_plus_one - prime_minus_one == 2:
            twins_number += 1

    return secondmult, thirdmult, primes, multiple_minus_one, twins_number

def get_background_color(label):
    """Get the background color for a given label."""
    background_color_chart = [
        "rgba(0, 0, 0, 1.0)",  # black
        "rgba(0, 255, 0, 1.0)",  # Green (Cool)
        "rgba(255, 0, 0, 1.0)",  # Red (Warm)
        "rgba(0, 0, 255, 1.0)",  # Blue (Cool)
        "rgba(255, 0, 255, 1.0)",  # Magenta (Cool)
        "rgba(255, 255, 0, 1.0)",  # Yellow (Warm)
    ]
    background_color_chart_special = [
        "rgba(255, 128, 0, 1.0)",
        "rgba(64, 224, 208, 1.0)",
    ]

    remainder_420 = label % 210
    if remainder_420 == 0:
        return background_color_chart_special[1]
    remainder_60 = label % 30
    if remainder_60 == 0:
        return background_color_chart_special[0]
    remainder = label % 6

    if remainder == 2:
        return background_color_chart[0]  # black for 12n+2
    elif remainder == 4:
        return background_color_chart[1]  # Green for 12n+4
    elif remainder == 6:
        return background_color_chart[2]  # Red for 12n+6
    elif remainder == 8:
        return background_color_chart[3]  # Blue for 12n+8
    elif remainder == 10:
        return background_color_chart[4]  # Magenta for 12n+10
    elif remainder == 0:
        return background_color_chart[5]  # Yellow for 12n

def calculate_range(start, end):
    """Calculate prime-related data for a range of numbers."""
    results = []
    for number in range(start, end + 1):
        result = addition(number)
        prime_check = is_prime(number)
        results.append((number, result, prime_check))
    return results

def calculate(min_interval, end_interval):
    """Perform the main calculations and generate the data for plotting."""
    unique_primes = []
    labels = []
    labels2 = []
    labels3 = []
    labels4 = []
    prime_count = []
    primes_count_plus = 0
    primes_count_minus = 0
    prime_count_minus_one_equation = []
    prime_twins_count = []
    prime_twins_exception = []
    prime_twins_exception3 = []
    prime_twins_exception4 = []
    prime_twins_ratio_plus_one = []
    prime_reverse_twins_ratio_plus_one = []
    ln_func = []
    ln_func2 = []
    ln_func3 = []
    ln_func4 = []
    ln = []
    reciproc_ln_for_multiple_of_3 = []
    reciproc_ln = []
    sqrt2 = math.sqrt(2)

    content_html = []

    # Parallel processing
    chunk_size = 1000  # Adjust the chunk size based on your system's capabilities
    ranges = [(i, min(i + chunk_size - 1, end_interval)) for i in range(min_interval, end_interval + 1, chunk_size)]

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(calculate_range, start, end) for start, end in ranges]
        for future in as_completed(futures):
            results = future.result()
            for number, result, prime_check in results:
                if number > 0:  # Ensure number is positive
                    labels.append(number)
                    prime_count.append(result[0])
                    primes_count_plus += result[0]
                    primes_count_minus += result[3]
                    prime_count_minus_one_equation.append(result[3])
                    prime_twins_count.append(result[4])

                    ln_func.append(round(number / math.log(number)))
                    ln_func2.append(round(number / math.log(number)) * sqrt2)
                    ln_func3.append(round(number / math.log(number)) / sqrt2)
                    ln_func4.append(round(number / math.log(number)) * 2 * sqrt2)
                    log_number = math.log(number) - sqrt2
                    result_log_twin_prime_ratio = log_number

                    ln.append(result_log_twin_prime_ratio)
                    reciproc_ln_for_multiple_of_3.append(result_log_twin_prime_ratio - 2)
                    reciproc_ln.append(1 / result_log_twin_prime_ratio)
                    prime_twins_ratio_plus_one.append(result[0] / result[4])
                    prime_reverse_twins_ratio_plus_one.append(result[4] / result[0])

                    if number % 6 == 0 and result[4] > 0:
                        labels2.append(number)
                        prime_twins_exception.append(result[4])
                    if number % 30 == 0 and result[4] > 0:
                        labels3.append(number)
                        prime_twins_exception3.append(result[4])
                    if number % 210 == 0 and result[4] > 0:
                        labels4.append(number)
                        prime_twins_exception4.append(result[4])

                    unique_primes.extend(result[2])

                    content_html.append(
                        f"<tr style='color:{'white' if prime_check else 'black'};background-color:{'black' if prime_check else 'white'};'>" +
                        f"<td>{number}</td>" +
                        f"<td>{result[0]}</td>" +
                        f"<td>{result[3]}</td>" +
                        f"<td>{result[4]}</td>" +
                        f"<td>{prime_check}</td>" +
                        "</tr>"
                    )

    unique_primes2 = sorted(set(unique_primes))
    content = ""
    twin_primes = []

    for index in range(len(unique_primes2)):
        if unique_primes2[index] - unique_primes2[index - 1] == 2:
            content += f"<span style='color:red'>{unique_primes2[index]}</span>, "
            twin_primes.append(unique_primes2[index - 1])
            twin_primes.append(unique_primes2[index])
        else:
            content += f"{unique_primes2[index]}, "

    primes_results = f"<div> primes plus 1= {primes_count_plus} prime minus 1= {primes_count_minus} </div>"
    ratio = f" ratio unique primes / twin primes {len(unique_primes2)} / {len(twin_primes)} = {len(unique_primes2) / len(twin_primes)}"
    ratio += primes_results
    ratio += f" ratio primes plus / primes minus ={primes_count_plus / primes_count_minus}"
    result_primes_found = f"<div>{content}</div>{len(unique_primes2) / len(twin_primes)}"
    twin_primes_found = ", ".join(map(str, twin_primes))
    result_primes_found += f"<div>{twin_primes_found}</div>"

    # Plotting
    fig = go.Figure()
    labels= range(min_interval,end_interval)
    # Add scatter plot for prime count
    fig.add_trace(go.Scatter(
        x=labels,
        y=prime_count,
        mode='markers',
        marker=dict(color=[get_background_color(label) for label in labels]),
        name='# of primes equation +1'
    ))

    # Add line plots for ln functions
    fig.add_trace(go.Scatter(
        x=labels,
        y=ln_func,
        mode='lines',
        line=dict(color='black'),
        name='# of primes equation +1'
    ))
    fig.add_trace(go.Scatter(
        x=labels,
        y=ln_func2,
        mode='lines',
        line=dict(color='green'),
        name='# of primes equation +1 *sqrt'
    ))
    fig.add_trace(go.Scatter(
        x=labels,
        y=ln_func3,
        mode='lines',
        line=dict(color='yellow'),
        name='# of primes equation +1 /sqrt'
    ))
    fig.add_trace(go.Scatter(
        x=labels,
        y=ln_func4,
        mode='lines',
        line=dict(color='blue'),
        name='# of primes equation +1 *2sqrt'
    ))

    fig.update_layout(title='Prime Count and Ln Functions', xaxis_title='Number', yaxis_title='Prime Count')
    fig.show()

    # Plot for prime count minus one equation
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=labels,
        y=prime_count_minus_one_equation,
        mode='markers',
        marker=dict(color=[get_background_color(label) for label in labels]),
        name='# of primes equation -1'
    ))
    fig2.add_trace(go.Scatter(
        x=labels,
        y=ln_func,
        mode='lines',
        line=dict(color='black'),
        name='# of primes equation +1'
    ))
    fig2.update_layout(title='Prime Count Minus One Equation', xaxis_title='Number', yaxis_title='Prime Count')
    fig2.show()

    # Bar plot for prime twins exception
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=labels2,
        y=prime_twins_exception,
        marker=dict(color=[get_background_color(label) for label in labels2]),
        name='# twins'
    ))
    fig3.update_layout(title='Prime Twins Exception', xaxis_title='Number', yaxis_title='Twin Primes Count')
    fig3.show()

    # Scatter plot for prime twins exception 3
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=labels3,
        y=prime_twins_exception3,
        mode='markers',
        marker=dict(color=[get_background_color(label) for label in labels3]),
        name='# twins'
    ))
    fig4.update_layout(title='Prime Twins Exception 3', xaxis_title='Number', yaxis_title='Twin Primes Count')
    fig4.show()

    # Bar plot for prime twins exception 4
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=labels4,
        y=prime_twins_exception4,
        marker=dict(color=[get_background_color(label) for label in labels4]),
        name='# twins'
    ))
    fig5.update_layout(title='Prime Twins Exception 4', xaxis_title='Number', yaxis_title='Twin Primes Count')
    fig5.show()

    # Scatter plot for prime twins ratio plus one
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=labels,
        y=prime_twins_ratio_plus_one,
        mode='markers',
        marker=dict(color=[get_background_color(label) for label in labels]),
        name='# ratio'
    ))
    fig6.add_trace(go.Scatter(
        x=labels,
        y=ln,
        mode='lines',
        line=dict(color='black'),
        name='# of primes equation +1'
    ))
    fig6.update_layout(title='Prime Twins Ratio Plus One', xaxis_title='Number', yaxis_title='Ratio')
    fig6.show()

    # Scatter plot for prime reverse twins ratio plus one
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=labels,
        y=prime_reverse_twins_ratio_plus_one,
        mode='markers',
        marker=dict(color=[get_background_color(label) for label in labels]),
        name='# ratio'
    ))
    fig7.add_trace(go.Scatter(
        x=labels,
        y=reciproc_ln,
        mode='lines',
        line=dict(color='red'),
        name='line average'
    ))
    fig7.update_layout(title='Prime Reverse Twins Ratio Plus One', xaxis_title='Number', yaxis_title='Ratio')
    fig7.show()

def main():
    """Main function to parse command-line arguments and run the calculations."""
    parser = argparse.ArgumentParser(description='Calculate and plot prime-related data.')
    parser.add_argument('min_interval', type=int, help='Minimum interval value')
    parser.add_argument('end_interval', type=int, help='End interval value')
    args = parser.parse_args()

    start_time = time.time()
    calculate(args.min_interval, args.end_interval)
    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()
