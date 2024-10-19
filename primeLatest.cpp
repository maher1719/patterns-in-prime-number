#include <iostream>
#include <vector>
#include <cmath>
#include <unordered_map>
#include <algorithm>
#include <fstream>
#include <string>
#include <thread>
#include <future>
#include <chrono>
#include <numeric>

// Note: We'll need to implement or find alternatives for some Python libraries

bool is_prime(int num) {
    if (num <= 1) return false;
    if (num == 2) return true;
    if (num % 2 == 0) return false;
    for (int i = 3; i <= std::sqrt(num); i += 2) {
        if (num % i == 0) return false;
    }
    return true;
}

struct AdditionResult {
    int secondmult;
    std::vector<int> primes;
    int multiple_minus_one;
    int twins_number;
};

AdditionResult addition(int number_to_generate_primes) {
    int quotient = number_to_generate_primes;
    int secondmult = 0;
    int multiple_minus_one = 0;
    int twins_number = 0;
    std::vector<int> primes;

    for (int index = 2; index <= number_to_generate_primes; ++index) {
        if ((index & 1) == 0 || (quotient & 1) == 0) {
            int prime_plus_one = index * quotient + 1;
            int prime_minus_one = index * quotient - 1;
            bool prime1 = false;
            bool prime2 = false;

            if ((prime_plus_one & 1) == 1 && is_prime(prime_plus_one) || prime_plus_one == 2) {
                secondmult++;
                prime1 = true;
                primes.push_back(prime_plus_one);
            }

            if ((prime_minus_one & 1) == 1 && is_prime(prime_minus_one) || prime_minus_one == 2) {
                multiple_minus_one++;
                prime2 = true;
                primes.push_back(prime_minus_one);
            }

            if (!prime1 || !prime2) continue;
            if ((prime_plus_one - 1) % 6 != 0) continue;
            if ((prime_plus_one - 1) % 6 == 0 && prime1 && prime2 && (prime_plus_one - prime_minus_one == 2)) {
                twins_number++;
            }
        }
    }

    return {secondmult, primes, multiple_minus_one, twins_number};
}

std::string get_background_color(int label) {
    std::vector<std::string> background_color_chart = {
        "rgba(0, 0, 0, 1.0)",
        "rgba(0, 255, 0, 1.0)",
        "rgba(255, 0, 0, 1.0)",
        "rgba(0, 0, 255, 1.0)",
        "rgba(255, 0, 255, 1.0)",
        "rgba(255, 255, 0, 1.0)"
    };
    std::vector<std::string> background_color_chart_special = {
        "rgba(255, 128, 0, 1.0)",
        "rgba(64, 224, 208, 1.0)"
    };

    int remainder_420 = label % 210;
    if (remainder_420 == 0) return background_color_chart_special[1];
    int remainder_60 = label % 30;
    if (remainder_60 == 0) return background_color_chart_special[0];
    int remainder = label % 6;

    if (remainder >= 0 && remainder <= 5) {
        return background_color_chart[remainder];
    }

    return "rgba(128, 128, 128, 1.0)";
}

std::vector<std::tuple<int, AdditionResult, bool>> calculate_range(int start, int end) {
    std::vector<std::tuple<int, AdditionResult, bool>> results;
    for (int number = start; number <= end; ++number) {
        AdditionResult result = addition(number);
        bool prime_check = is_prime(number);
        results.push_back(std::make_tuple(number, result, prime_check));
    }
    return results;
}

void calculate(int min_interval, int end_interval) {
    std::vector<int> labels, prime_count, prime_count_minus_one_equation, prime_twins_count;
    std::vector<bool> is_number_prime;
    std::vector<double> ln_func, ln_func2, ln_func3, ln_func4, ln, reciproc_ln, reciproc_ln_2, reciproc_ln_4;
    std::vector<double> prime_twins_ratio_plus_one, prime_reverse_twins_ratio_plus_one;

    int chunk_size = 700;
    std::vector<std::pair<int, int>> ranges;
    for (int i = min_interval; i <= end_interval; i += chunk_size) {
        ranges.push_back({i, std::min(i + chunk_size - 1, end_interval)});
    }

    std::vector<std::future<std::vector<std::tuple<int, AdditionResult, bool>>>> futures;
    for (const auto& range : ranges) {
        futures.push_back(std::async(std::launch::async, calculate_range, range.first, range.second));
    }

    for (auto& future : futures) {
        auto results = future.get();
        for (const auto& result : results) {
            int number = std::get<0>(result);
            const AdditionResult& add_result = std::get<1>(result);
            bool prime_check = std::get<2>(result);

            if (number > 0) {
                labels.push_back(number);
                prime_count.push_back(add_result.secondmult);
                prime_count_minus_one_equation.push_back(add_result.multiple_minus_one);
                prime_twins_count.push_back(add_result.twins_number);
                is_number_prime.push_back(prime_check);

                double math_log = std::log(number);
                double divide_log = std::round(number / math_log);
                ln_func.push_back(divide_log);
                ln_func2.push_back(divide_log * std::sqrt(2));
                ln_func3.push_back(divide_log / std::sqrt(2));
                ln_func4.push_back(divide_log * 2 * std::sqrt(2));

                double log_number = math_log - M_PI;
                double log_number_pi_2 = math_log - 2 * std::sqrt(2);
                double log_number_pi_4 = math_log + 2 * std::sqrt(2);

                ln.push_back(log_number);
                reciproc_ln.push_back(1 / log_number);
                reciproc_ln_2.push_back(1 / log_number_pi_2);
                reciproc_ln_4.push_back(1 / log_number_pi_4);

                if (add_result.twins_number > 0) {
                    prime_twins_ratio_plus_one.push_back(static_cast<double>(add_result.secondmult) / add_result.twins_number);
                } else {
                    prime_twins_ratio_plus_one.push_back(0);
                }
                prime_reverse_twins_ratio_plus_one.push_back(static_cast<double>(add_result.twins_number) / add_result.secondmult);
            }
        }
    }

    // Write results to CSV
    std::ofstream outfile("primes_data" + std::to_string(min_interval) + "-" + std::to_string(end_interval) + ".csv");
    outfile << "Number,Primes +1,Primes -1,Twins,isPrime\n";
    for (size_t i = 0; i < labels.size(); ++i) {
        outfile << labels[i] << "," << prime_count[i] << "," << prime_count_minus_one_equation[i] << ","
                << prime_twins_count[i] << "," << (is_number_prime[i] ? "true" : "false") << "\n";
    }
    outfile.close();
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

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    std::cout << "Elapsed time: " << duration.count() / 1000.0 << " seconds" << std::endl;

    return 0;
}