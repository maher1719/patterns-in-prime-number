from tabulate import tabulate
import random
class Knot:
    def __init__(self, crossings):
        self.crossings = crossings  # List of tuples representing crossings

    def simplify(self):
        while True:
            simplified = False
            i = 0
            
            while i < len(self.crossings) - 1:
                if self.crossings[i] == self.crossings[i + 1]:
                    # Apply Type 1 Reidemeister move
                    self.crossings.pop(i)
                    self.crossings.pop(i)
                    simplified = True
                elif (self.crossings[i][0] == self.crossings[i + 1][0] and
                      self.crossings[i][1] == self.crossings[i + 1][1]):
                    # Apply Type 2 Reidemeister move
                    self.crossings.pop(i)
                    self.crossings.pop(i)
                    simplified = True
                else:
                    i += 1

                if simplified:
                    break

            if not simplified:
                break

    def is_unknot(self):
        self.simplify()
        return len(self.crossings) == 0

    def print_table(self):
        table = [["Crossing Index", "Type"]]
        for crossing in self.crossings:
            table.append([crossing[0], crossing[1]])
        print(tabulate(table, headers="firstrow", tablefmt="grid"))

# Function to generate random test cases
def generate_random_test_cases(num_cases, max_crossings):
    test_cases = []
    for _ in range(num_cases):
        num_crossings = random.randint(2, max_crossings)  # Generate random number of crossings
        crossings = generate_random_knot(num_crossings)
        is_unknot = random.choice([True, False])  # Randomly determine if it's an unknot
        test_cases.append((crossings, is_unknot))
    return test_cases

# Function to test the algorithm and print the table
def test_knot_algorithm():
    test_cases = [
        ([(1, 'over'), (1, 'over')], True),  # Simple unknot
        ([(2, 'over'), (2, 'under')], True),  # Type 2 move example
        ([(1, 'over'), (2, 'under'), (1, 'over'), (3, 'under')], False),  # Complex knot
        ([(1, 'over'), (2, 'under'), (2, 'under'), (1, 'over')], True),  # Another unknot
    ]
    
    
    for crossings, expected in test_cases:
        knot = Knot(crossings)
        print("Knot Diagram:")
        knot.print_table()
        result = knot.is_unknot()
        print(f"Expected: {expected} | Result: {result}\n")
        assert result == expected, f"Test failed for knot: {crossings}"

    # Generate and test random test cases
    random_test_cases = generate_random_test_cases(5, 10)
    for crossings, is_unknot in random_test_cases:
        knot = Knot(crossings)
        print("Random Knot Diagram:")
        knot.print_table()
        expected = is_unknot
        result = knot.is_unknot()
        print(f"Expected: {expected} | Result: {result}\n")
        assert result == expected, f"Test failed for knot: {crossings}"

# Run the tests
test_knot_algorithm()
