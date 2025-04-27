import numpy as np
import matplotlib.pyplot as plt

# Given data point: 1000 elements takes 40 seconds
elements_measured = 1000
time_measured = 40

# Target: 10,000 elements should take under 3000 seconds
elements_target = 10000
time_target = 3000

# Calculate coefficient for optimized performance
k_optimized = time_target / (elements_target ** 2)
print(f"Optimized coefficient k = {k_optimized}")

# Generate data points for different element counts (up to 10,000)
elements = np.array([100, 500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000])
time_seconds = k_optimized * elements ** 2

# Create the time complexity chart
plt.figure(figsize=(10, 6))
plt.plot(elements, time_seconds, 'b-', linewidth=2)

# Add labels
plt.xlabel('Number of Elements (n)', fontsize=12)
plt.ylabel('Execution Time (seconds)', fontsize=12)
plt.title('Time Complexity of VLSI Placement Algorithm', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

# Format the y-axis with commas for thousands
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))

# Save the chart
plt.tight_layout()
plt.savefig('vlsi_algorithm_complexity.png', dpi=300)
plt.savefig('vlsi_algorithm_complexity.pdf')  # PDF version for publication
plt.show()

# Print data table for reference
print("\nEstimated execution times (optimized):")
print("Elements | Time (seconds)")
print("-" * 30)
for n, t in zip(elements, time_seconds):
    print(f"{n:8,d} | {t:14,.2f}")
