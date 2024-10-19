#include <iostream>
#include <vector>
#include <cmath>
#include <future>
#include <chrono>
#include <fstream>
#include <sstream>
#include <mutex>
#include <algorithm>

// Mutex for handling concurrent access to shared resources
std::mutex mtx;

// Function to check if a number is prime (optimized)
bool is_prime(int num) {
    if (num < 2) return false;
    if (num == 2 || num == 3) return true;
    if (num % 2 == 0 || num % 3 == 0) return false;
    for (int i = 5; i * i <= num; i += 6) {
        if (num % i == 0 || num % (i + 2) == 0) return false;
    }
    return true;
}

// Function to generate prime information for a range of numbers
std::vector<std::tuple<int, int, int, int>> calculate_range(int start, int end) {
    std::vector<std::tuple<int, int, int, int>> results;
    for (int number = start; number <= end; ++number) {
        int primes_plus_one = 0, primes_minus_one = 0, twins = 0;
        int quotient = number;
        for (int i = 2; i <= number; ++i) {
            int prime_plus_one = i * quotient + 1;
            int prime_minus_one = i * quotient - 1;

            bool prime1 = false, prime2 = false;
            if ((prime_plus_one % 2 == 1 && is_prime(prime_plus_one)) || prime_plus_one == 2) {
                primes_plus_one++;
                prime1 = true;
            }

            if ((prime_minus_one % 2 == 1 && is_prime(prime_minus_one)) || prime_minus_one == 2) {
                primes_minus_one++;
                prime2 = true;
            }

            if (prime1 && prime2 && (prime_plus_one - prime_minus_one == 2) && ((prime_plus_one - 1) % 6 == 0)) {
                twins++;
            }
        }
        results.push_back({ number, primes_plus_one, primes_minus_one, twins });
    }
    return results;
}

// Function to calculate prime-related data for a given range using parallel processing
void calculate(int min_interval, int max_interval, const std::string& output_file) {
    const int chunk_size = 700; // Adjust chunk size for parallel processing

    std::vector<std::future<std::vector<std::tuple<int, int, int, int>>>> futures;
    for (int i = min_interval; i <= max_interval; i += chunk_size) {
        int end = std::min(i + chunk_size - 1, max_interval);
        futures.push_back(std::async(std::launch::async, calculate_range, i, end));
    }

    // Collect and write results to a CSV file
    std::ofstream file(output_file);
    file << "Number,Primes +1,Primes -1,Twins\n";

    for (auto& future : futures) {
        auto results = future.get();
        for (const auto& result : results) {
            file << std::get<0>(result) << "," << std::get<1>(result) << "," 
                 << std::get<2>(result) << "," << std::get<3>(result) << "\n";
        }
    }

    file.close();
}

// Main function to execute the calculation and measure time
int main() {
    int min_interval, max_interval;
    std::cout << "Enter the minimum interval: ";
    std::cin >> min_interval;
    std::cout << "Enter the maximum interval: ";
    std::cin >> max_interval;

    auto start_time = std::chrono::high_resolution_clock::now();

    // Perform calculation and save results to CSV
    calculate(min_interval, max_interval, "primes_data.csv");

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;

    std::cout << "Elapsed time: " << elapsed.count() << " seconds\n";

    return 0;
}
