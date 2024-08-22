import numpy as np
import matplotlib.pyplot as plt

# Example data (segmentation index, a values, b values)
indices = np.array([6, 30, 210, 2310, 5000, 10000, 15000])
a_values = np.array([-0.43349545837141884030430105667620, -0.43397609454495539305085571868403, 
                     -0.44235852124135222052103699752479, -0.48640607348380066055071324626624, 
                     -0.51469164787125676330248325029970, -0.54758299636982910030269522394519, 
                     -0.57164741499225912857440334846615])
b_values = np.array([0.87148366126460774516715446225135, 0.87164958304487505369451127990033, 
                     0.87368264240130177888943308062153, 0.88422004736418968739997126249364, 
                     0.89083892530509323215426320530241, 0.89833026899889756311523569820565, 
                     0.90370227763754140681839999160729])

# Fit polynomial trendlines
coeff_a = np.polyfit(indices, a_values, 2)  # 2nd degree polynomial
coeff_b = np.polyfit(indices, b_values, 2)  # 2nd degree polynomial

# Create trendline functions
poly_a = np.poly1d(coeff_a)
poly_b = np.poly1d(coeff_b)

# Generate predictions for large indices
large_indices = np.linspace(1, 100, 100)
pred_a = poly_a(large_indices)
pred_b = poly_b(large_indices)

# Plot the results
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.scatter(indices, a_values, color='blue', label='Actual a values')
plt.plot(large_indices, pred_a, color='red', label='Trendline for a')
plt.xlabel('Segmentation Index')
plt.ylabel('a values')
plt.title('Trend of a Values')
plt.legend()

plt.subplot(1, 2, 2)
plt.scatter(indices, b_values, color='green', label='Actual b values')
plt.plot(large_indices, pred_b, color='orange', label='Trendline for b')
plt.xlabel('Segmentation Index')
plt.ylabel('b values')
plt.title('Trend of b Values')
plt.legend()

plt.tight_layout()
plt.show()
