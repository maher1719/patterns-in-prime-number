import pandas as pd

# Load the CSV file to check its content
file_path = '/home/maher/Downloads/output2To100.csv'
data = pd.read_csv(file_path)

# Display the first few rows of the dataframe to understand its structure
data.head()
grouped_data = data.groupby(['result', 'operation'])
count_grouped = grouped_data.size().reset_index(name='counts')

# Calculate the mean of the 'number' and 'quotient' for each group
mean_grouped = grouped_data.mean().reset_index()

# Display the results
count_grouped, mean_grouped
# Group the data by 'result' and 'operation'
grouped_data = data.groupby(['result', 'operation'])

# Count the number of occurrences for each group
count_grouped = grouped_data.size().reset_index(name='counts')

# Calculate the mean of the 'number' and 'quotient' for each group
mean_grouped = grouped_data.mean().reset_index()

# Display the results
count_grouped.head(), mean_grouped.head()
count_csv_path = 'grouped_count2.csv'
mean_csv_path = 'grouped_mean2.csv'

# Save the count of occurrences to a CSV file
count_grouped.to_csv(count_csv_path, index=False)

# Save the mean of 'number' and 'quotient' to another CSV file
mean_grouped.to_csv(mean_csv_path, index=False)

print(f'Count grouped data saved to {count_csv_path}')
print(f'Mean grouped data saved to {mean_csv_path}')