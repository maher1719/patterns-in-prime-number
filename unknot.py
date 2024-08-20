from tabulate import tabulate

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

# Test cases: List of tuples, each tuple representing a crossing (index, over/under)
test_cases = [
    ([(1, 'over'), (1, 'over')], True),
    ([(1, 'over'), (2, 'over'),(3, 'over'),(3, 'under'), (2, 'under'),(1, 'under')], True),   # Simple unknot
    ([(2, 'under'), (2, 'under')], True),  # Type 2 move example
    ([(1, 'over'), (2, 'under'), (1, 'over'), (3, 'under')], False),  # Complex knot
    ([(1, 'over'), (2, 'under'), (2, 'under'), (1, 'over')], True),  # Another unknot
]

# Function to test the algorithm and print the table
def test_knot_algorithm():
    for crossings, expected in test_cases:
        knot = Knot(crossings)
        print("Knot Diagram:")
        knot.print_table()
        result = knot.is_unknot()
        print(f"Expected: {expected} | Result: {result}\n")
        assert result == expected, f"Test failed for knot: {crossings}"

# Run the tests
test_knot_algorithm()
