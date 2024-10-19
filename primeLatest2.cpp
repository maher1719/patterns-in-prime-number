#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <thread>
#include <mutex>
#include <atomic>
#include <algorithm>
#include <future>
#include <chrono>

std::mutex mtx;  // For thread synchronization

// Prime checking function (simple trial division)
bool is_prime(int num) {
    if (num <= 1) return false;
    if (num == 2 || num == 3) return true;
    if (num % 2 == 0 || num % 3 == 0) return false;
    for (int i = 5; i * i <= num; i += 6) {
        if (num % i == 0 || num % (i + 2) == 0) return false;
    }
    return true;
}

// Generate primes based on the given number
std::tuple<int, std::vector<int>, int, int> addition(int number_to_generate_primes) {
    int quotient = number_to_generate_primes;
    int secondmult = 0, thirdmult = 0;
    std::vector<int> primes;
    int multiple_minus_one = 0;
    int twins_number = 0;
    int possible_twin1 = 0, possible_twin2 = 0;
    
    /*for (int index = 2; index <= number_to_generate_primes; ++index) {
        if (index % 2 == 0 || quotient % 2 == 0) {
            int prime_plus_one = index * quotient + 1;
            int prime_minus_one = index * quotient - 1;
            bool prime1 = false, prime2 = false;

            if ((prime_plus_one % 2 == 1 && is_prime(prime_plus_one)) || prime_plus_one == 2) {
                secondmult++;
                prime1 = true;
                possible_twin1 = prime_plus_one;
                primes.push_back(prime_plus_one);
            }

            if ((prime_minus_one % 2 == 1 && is_prime(prime_minus_one)) || prime_minus_one == 2) {
                multiple_minus_one++;
                prime2 = true;
                possible_twin2 = prime_minus_one;
                primes.push_back(prime_minus_one);
            }

            if (!prime1 || !prime2) continue;
            if ((prime_plus_one - 1) % 6 != 0) continue;
            if ((prime_plus_one - 1) % 6 == 0 && prime1 && prime2 && (possible_twin1 - possible_twin2 == 2)) {
                twins_number++;
            }
        }
    }*/
    for (int index = 2; index <= number_to_generate_primes; ++index) {
    // Use modulo instead of bitwise for even/odd check
    if (index % 2 == 0 || quotient % 2 == 0) {
        int prime_plus_one = index * quotient + 1;
        int prime_minus_one = index * quotient - 1;

        bool prime1 = false;
        bool prime2 = false;

        // Check primality using a suitable function
        if ((prime_plus_one % 2 == 1 && is_prime(prime_plus_one)) ) {
            secondmult++;
            prime1 = true;
            possible_twin1 = prime_plus_one;
            primes.push_back(prime_plus_one);
        }

        if ((prime_minus_one % 2 == 1 && is_prime(prime_minus_one))) {
            multiple_minus_one++;
            prime2 = true;
            possible_twin2 = prime_minus_one;
            primes.push_back(prime_minus_one);
        }

        if (!prime1 || !prime2) continue;
        if ((prime_plus_one - 1) % 6 != 0) continue;

        if ((prime_plus_one - 1) % 6 == 0 && prime1 && prime2 && (possible_twin1 - possible_twin2 == 2)) {
            twins_number++;
        }
    }
}

    return std::make_tuple(secondmult, primes, multiple_minus_one, twins_number);
}

void calculate_range(int start, int end, std::vector<int>& labels, std::vector<int>& prime_count, 
                     std::vector<int>& prime_count_minus_one_equation, std::vector<int>& prime_twins_count,
                     std::vector<int>& is_number_prime) {
    for (int number = start; number <= end; ++number) {
        auto result = addition(number);
        bool prime_check = is_prime(number);
        
        std::lock_guard<std::mutex> lock(mtx);
        labels.push_back(number);
        prime_count.push_back(std::get<0>(result));
        prime_count_minus_one_equation.push_back(std::get<2>(result));
        prime_twins_count.push_back(std::get<3>(result));
        is_number_prime.push_back(prime_check ? 1 : 0);
    }
}

void write_to_csv(const std::string& filename, const std::vector<int>& labels, const std::vector<int>& prime_count,
                  const std::vector<int>& prime_count_minus_one_equation, const std::vector<int>& prime_twins_count,
                  const std::vector<int>& is_number_prime) {
    std::ofstream file(filename);
    file << "Number,Primes +1,Primes -1,Twins,isPrime\n";
    for (size_t i = 0; i < labels.size(); ++i) {
        file << labels[i] << "," << prime_count[i] << "," << prime_count_minus_one_equation[i] << "," 
             << prime_twins_count[i] << "," << is_number_prime[i] << "\n";
    }
    file.close();
}

void calculate(int min_interval, int end_interval) {
    std::vector<int> labels, prime_count, prime_count_minus_one_equation, prime_twins_count, is_number_prime;

    int chunk_size = 700;  // Adjust chunk size
    std::vector<std::pair<int, int>> ranges;
    for (int i = min_interval; i <= end_interval; i += chunk_size) {
        ranges.push_back({i, std::min(i + chunk_size - 1, end_interval)});
    }

    std::vector<std::future<void>> futures;
    for (const auto& range : ranges) {
        futures.push_back(std::async(std::launch::async, calculate_range, range.first, range.second, 
                                     std::ref(labels), std::ref(prime_count), std::ref(prime_count_minus_one_equation), 
                                     std::ref(prime_twins_count), std::ref(is_number_prime)));
    }

    for (auto& future : futures) {
        future.get();
    }

    write_to_csv("primes_data_" + std::to_string(min_interval) + "_" + std::to_string(end_interval) + ".csv", 
                 labels, prime_count, prime_count_minus_one_equation, prime_twins_count, is_number_prime);
}

int main() {
    int min_interval, end_interval;
    std::cout << "Enter the minimum interval: ";
    std::cin >> min_interval;
    std::cout << "Enter the maximum interval: ";
    std::cin >> end_interval;

    auto start_time = std::chrono::high_resolution_clock::now();
    
    calculate(min_interval, end_interval);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;
    
    std::cout << "Elapsed time: " << elapsed.count() << " seconds\n";
    return 0;
}
