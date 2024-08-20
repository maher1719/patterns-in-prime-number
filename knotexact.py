from tabulate import tabulate

class Knot:
    def __init__(self, crossings):
        self.crossings = crossings  # List of tuples representing crossings
        self.simplifications = []   # To keep track of simplifications

    def simplify(self):
        while True:
            simplified = False
            i = 0
            while i < len(self.crossings) - 1:
                j = i + 1
                while j < len(self.crossings):
                    # Type 1 Reidemeister move
                    if self.crossings[i] == self.crossings[j]:
                        self.simplifications.append((i, j, "Type 1"))
                        self.crossings.pop(j)
                        self.crossings.pop(i)
                        simplified = True
                        break
                    # Type 2 Reidemeister move
                    elif (self.crossings[i][0] == self.crossings[j][0] and
                          self.crossings[i][1] == self.crossings[j][1]):
                        self.simplifications.append((i, j, "Type 2"))
                        self.crossings.pop(j)
                        self.crossings.pop(i)
                        simplified = True
                        break
                    j += 1
                if simplified:
                    break
                i += 1
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

    def print_simplifications(self):
        table = [["Index 1", "Index 2", "Move Type"]]
        for simplification in self.simplifications:
            table.append([simplification[0], simplification[1], simplification[2]])
        print(tabulate(table, headers="firstrow", tablefmt="grid"))

# Test case: More complex unknot example
test_crossings = [(1, 'over'), (2, 'under'), (3, 'over'), (4, 'under'), (3, 'under'), (2, 'over'), (1, 'under'), (5, 'over'), (5, 'under')]

# Initialize the knot
knot = Knot(test_crossings)

# Print original knot diagram
print("Original Knot Diagram:")
knot.print_table()

# Check if the knot is an unknot
result = knot.is_unknot()
print(f"Is Unknot: {result}")

# Print simplified diagram and simplifications applied
print("\nSimplified Diagram:")
knot.print_table()

print("\nNumber of remaining crossings:", len(knot.crossings))

print("\nSimplifications applied:")
knot.print_simplifications()