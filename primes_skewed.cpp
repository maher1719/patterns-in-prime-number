#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <algorithm>
#include <cmath>
#include <iterator>
#include <gnuplot-iostream.h> // For plotting using Gnuplot
#include <Eigen/Dense>        // If you need matrix operations (optional)

// Function to read CSV without duplicates
std::vector<std::map<std::string, int>> read_csv(const std::string& filename) {
    std::ifstream file(filename);
    std::string line;
    std::vector<std::map<std::string, int>> data;
    std::map<std::string, int> entry;
    
    while (std::getline(file, line)) {
        // Implement CSV parsing and removal of duplicates
        // Assuming CSV is comma-separated with columns like "Primes +1", "Primes -1", etc.
        // Process the line to extract values and store them in the map
        
        data.push_back(entry); // Store the entry
    }

    return data;
}

// Count occurrences in column
std::map<int, int> count_occurrences(const std::vector<std::map<std::string, int>>& data, const std::string& column) {
    std::map<int, int> counts;
    for (const auto& row : data) {
        int val = row.at(column);
        counts[val]++;
    }
    return counts;
}

// Function to perform curve fitting
void curve_fit(const std::vector<double>& x_data, const std::vector<double>& y_data) {
    // Implement curve fitting for log model: y = a / log(x) + b
    // You can use GSL or other numeric libraries for optimization
}

// Plot using Gnuplot
void plot_data(const std::vector<double>& x, const std::vector<double>& y, const std::string& title, const std::string& xlabel, const std::string& ylabel) {
    Gnuplot gp;
    gp << "set title '" << title << "'\n";
    gp << "set xlabel '" << xlabel << "'\n";
    gp << "set ylabel '" << ylabel << "'\n";
    gp << "plot '-' with linespoints title 'Data'\n";
    gp.send1d(boost::make_tuple(x, y));
}

// Main function to process prime data
void process_prime_data(const std::string& column) {
    std::vector<std::map<std::string, int>> data = read_csv("primes.txt");
    std::map<int, int> number_counts = count_occurrences(data, column);

    std::vector<int> X;
    std::vector<int> Y;

    for (const auto& count : number_counts) {
        X.push_back(count.first);
        Y.push_back(count.second);
    }

    // Perform ratio calculations and store in vectors
    std::vector<double> ratio_X, ratio_Y;
    for (size_t i = 0; i < X.size(); ++i) {
        ratio_X.push_back(X[i]);
        ratio_Y.push_back(X[i] / static_cast<double>(*std::max_element(Y.begin(), Y.end())));
    }

    // Plot data
    plot_data(ratio_X, ratio_Y, "Ratio n/max(Y)", "n", "ratio");

    // Perform curve fitting
    curve_fit(ratio_X, ratio_Y);
}

int main() {
    // Process different prime columns
    process_prime_data("Primes +1");
    process_prime_data("Primes -1");
    process_prime_data("Twins");

    return 0;
}
