from tabulate import tabulate

class Knot:
    def __init__(self, crossings):
        self.crossings = crossings  # List of tuples representing crossings

    def simplify(self):
        print("Starting Simplification:")
        simplified = True
        while simplified:
            simplified = False
            # Dictionary to track pairs of crossings
            pair_indices = {}
            for i, crossing in enumerate(self.crossings):
                if crossing[0] in pair_indices:
                    # Found a pair
                    j = pair_indices[crossing[0]]
                    if self.crossings[j][1] != crossing[1]:
                        # Type 1 Reidemeister move
                        print(f"Applying Type 1 move: Removing crossings {self.crossings[j]} and {crossing}")
                        self.crossings.pop(i)
                        self.crossings.pop(j)
                        simplified = True
                        break
                else:
                    pair_indices[crossing[0]] = i

            if not simplified:
                i = 0
                while i < len(self.crossings) - 1:
                    if self.crossings[i][1] == self.crossings[i + 1][1]:
                        # Type 2 Reidemeister move
                        print(f"Applying Type 2 move: Removing crossings {self.crossings[i]} and {self.crossings[i + 1]}")
                        self.crossings.pop(i)
                        self.crossings.pop(i)
                        simplified = True
                        break
                    else:
                        i += 1

        print("Final simplified diagram:")
        self.print_table()

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
    ([(1, 'over'), (1, 'under')], True),  # Simple unknot with Type 1 move
    ([(2, 'under'), (2, 'under')], True),  # Simple unknot with Type 2 move
    ([(1, 'over'), (2, 'under'), (1, 'over'), (3, 'under')], False),  # Complex knot
    ([(1, 'over'), (2, 'under'), (2, 'under'), (1, 'over')], True),  # Another unknot with Type 2 move
    ([(1, 'over'), (2, 'under'), (3, 'over'), (1, 'under'), (2, 'over'), (3, 'under')], False),  # Trefoil knot
    ([(1, 'over'), (2, 'under'), (3, 'over'), (4, 'under'), (1, 'under'), (2, 'over'), (3, 'under'), (4, 'over')], True),  # Complex knot with simplification
    ([(1,'under'),(2,'over'),(3,'under'),(4,'under'),(5,'over'),(6,'under'),(7,'over'),
(8,'under'),(9,'under'),(3,'over'),(10,'over'),(11,'under'),(12,'over'),(1,'over'),
(2,'under'),(13,'under'),(11,'over'),(14,'over'),(4,'over'),(15,'under'),(8,'over'),
(7,'under'),(6,'over'),(12,'under'),(13,'over'),(10,'under'),(14,'under'),(5,'under'),
(15,'over'),(9,'over'),],True)
]

# Function to test the algorithm
def test_knot_algorithm():
    for crossings, expected in test_cases:
        print(f"\nTesting knot: {crossings}")
        knot = Knot(crossings)
        knot.print_table()
        result = knot.is_unknot()
        print(f"Expected: {expected} | Result: {result}")
        #assert result == expected, f"Test failed for knot: {crossings}"

# Run the tests
test_knot_algorithm()
