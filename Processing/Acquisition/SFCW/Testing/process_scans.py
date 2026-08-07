import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

data = np.load("scans/all_scans.npz")
rp_db = data["rp_db"]
range_axis = data["range_axis"]
range_max = data["range_max"]

fig, ax = plt.subplots(figsize=(11, 5))
line, = ax.plot(range_axis, rp_db[0])
title = ax.set_title("Range Profile Scan 0")

ax.set_xlabel("Range m")
ax.set_ylabel("Magnitude dB")
ax.set_ylim(-60, 0)
ax.set_xlim(0, range_max)
ax.grid(True)

def update(i):
    line.set_ydata(rp_db[i])
    title.set_text(f"Range Profile Scan {i}")
    return line, title

ani = FuncAnimation(fig, update, frames=len(rp_db), interval=300, blit=False)
ani.save("scans/range_profiles.mp4", fps=5, dpi=150)

plt.show()