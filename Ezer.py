import numpy as np
import matplotlib.pyplot as plt

# Parameters for the cosine wave
min_value = 20
max_value = 170
cycle_time = 75  # Time for one full cycle
num_cycles = 30  # Total number of cycles

# Calculated parameters
amplitude = (max_value - min_value) / 2  # Amplitude of the wave
offset = (max_value + min_value) / 2  # Center line (mean value)
frequency = 1 / cycle_time  # Frequency of the wave

# Generate time steps and the cosine wave
time_steps = np.linspace(0, cycle_time * num_cycles, num_cycles * 10)  # Fine resolution for smoothness
cosine_wave = amplitude * np.cos(2 * np.pi * frequency * time_steps) + offset

# Plot the cosine wave
plt.figure(figsize=(10, 6))
plt.plot(time_steps, cosine_wave, label="Cosine Wave", color="blue")
plt.axhline(min_value, color="red", linestyle="--", label=f"Min Bound ({min_value})")
plt.axhline(max_value, color="green", linestyle="--", label=f"Max Bound ({max_value})")

# Add labels, legend, and title
plt.title("Cosine Wave with Min/Max Bounds")
plt.xlabel("Time (units)")
plt.ylabel("Values")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
