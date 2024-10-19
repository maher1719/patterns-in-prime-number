#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <sstream>
#include <omp.h>
#include <unordered_map>
#include <algorithm>
#include <chrono>

// Check if a number is prime
bool is_prime(int num) {
    if (num <= 1) return false;
    if (num == 2) return true;
    if (num % 2 == 0) return false;
    for (int i = 3; i <= std::sqrt(num); i += 2) {
        if (num % i == 0) return false;
    }
    return true;
}

// Generate primes based on the given number
std::tuple<int, std::vector<int>, int, int> addition(int number_to_generate_primes) {
    int quotient = number_to_generate_primes;
    int secondmult = 0;
    int multiple_minus_one = 0;
    int twins_number = 0;
    std::vector<int> primes;

    for (int index = 2; index <= number_to_generate_primes; ++index) {
        if ((index & 1) == 0 || (quotient & 1) == 0) {
            int prime_plus_one = index * quotient + 1;
            int prime_minus_one = index * quotient - 1;
            bool prime1 = false, prime2 = false;

            if ((prime_plus_one & 1 && is_prime(prime_plus_one)) || prime_plus_one == 2) {
                secondmult++;
                prime1 = true;
                primes.push_back(prime_plus_one);
            }
            if ((prime_minus_one & 1 && is_prime(prime_minus_one)) || prime_minus_one == 2) {
                multiple_minus_one++;
                prime2 = true;
                primes.push_back(prime_minus_one);
            }
            if (prime1 && prime2 && (prime_plus_one - prime_minus_one == 2)) {
                if ((prime_plus_one - 1) % 6 == 0) {
                    twins_number++;
                }
            }
        }
    }
    return {secondmult, primes, multiple_minus_one, twins_number};
}

// Calculate primes-related data for a range
std::vector<std::tuple<int, std::tuple<int, std::vector<int>, int, int>, bool>> calculate_range(int start, int end) {
    std::vector<std::tuple<int, std::tuple<int, std::vector<int>, int, int>, bool>> results;
    for (int number = start; number <= end; ++number) {
        auto result = addition(number);
        bool prime_check = is_prime(number);
        results.emplace_back(number, result, prime_check);
    }
    return results;
}

// Main calculation with parallelism using OpenMP
void calculate(int min_interval, int end_interval) {
    std::vector<int> labels, prime_count, prime_count_minus_one_equation, prime_twins_count, is_number_prime;
    std::vector<int> ln_func, ln_func2, ln_func3, ln_func4, reciproc_ln, reciproc_ln_2, reciproc_ln_4;
    int primes_count_plus = 0, primes_count_minus = 0;

    const int chunk_size = 700;
    int num_chunks = (end_interval - min_interval) / chunk_size + 1;

    // Parallel region
    #pragma omp parallel for reduction(+:primes_count_plus,primes_count_minus) schedule(dynamic)
    for (int chunk = 0; chunk < num_chunks; ++chunk) {
        int start = min_interval + chunk * chunk_size;
        int end = std::min(start + chunk_size - 1, end_interval);

        auto results = calculate_range(start, end);
        for (const auto& [number, result, prime_check] : results) {
            int result0, result2, result3;
            std::vector<int> result1;
            std::tie(result0, result1, result2, result3) = result;

            #pragma omp critical
            {
                labels.push_back(number);
                prime_count.push_back(result0);
                primes_count_plus += result0;
                primes_count_minus += result2;
                prime_count_minus_one_equation.push_back(result2);
                prime_twins_count.push_back(result3);
                is_number_prime.push_back(prime_check);

                // Logarithmic functions for twin prime ratios
                if (number > 1) {
                    double log_number = std::log(number);
                    ln_func.push_back(number / log_number);
                    ln_func2.push_back(number / log_number * std::sqrt(2));
                    ln_func3.push_back(number / log_number / std::sqrt(2));
                    ln_func4.push_back(number / log_number * 2 * std::sqrt(2));

                    double log_pi = log_number - M_PI;
                    reciproc_ln.push_back(1 / log_pi);
                    reciproc_ln_2.push_back(1 / (log_number - 2 * std::sqrt(2)));
                    reciproc_ln_4.push_back(1 / (log_number + 2 * std::sqrt(2)));
                }
            }
        }
    }

    // Save results to CSV
    std::ofstream file("primes_C.csv");
    file << "Number,Primes +1,Primes -1,Twins,isPrime\n";
    for (size_t i = 0; i < labels.size(); ++i) {
        file << labels[i] << "," << prime_count[i] << "," << prime_count_minus_one_equation[i] << ","
             << prime_twins_count[i] << "," << is_number_prime[i] << "\n";
    }
    file.close();
}

int main() {
    

    auto start_time = std::chrono::high_resolution_clock::now();

    calculate(52001, 55000);

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;
    std::cout << "Elapsed time: " << elapsed.count() << " seconds\n";

    return 0;
}
