import matplotlib.pyplot as plt
import numpy as np

from break_axes import broken_and_clip_axes, scale_axes
from break_axes.break_axes import remove_yaxis_minor_ticks

plt.rcParams["ytick.minor.visible"] = True
plt.rcParams["xtick.minor.visible"] = True
plt.rcParams["xtick.top"] = True
plt.rcParams["ytick.right"] = True


x = np.linspace(0, np.pi, 15)
y1 = 0.15 * np.sin(x) + 0.97
y2 = -0.06 * np.sin(x)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 2.4), sharey=True)
for ax in (ax1, ax2):
    ax.set_xlim(-0.1, np.pi + 0.1)
    ax.plot(x, y1, marker="o", mew=1, mec="dimgray", label="Y1")
    ax.plot(x, y2, marker="s", mew=1, mec="dimgray", label="Y2")

    ax.set_yticks([-0.05, 0, 0.95, 1, 1.05, 1.1])
    scale_axes(ax, y_interval=[(0.02, 0.95, 0.05)])

    ax.set_yticks([-0.05, 0, 0.95, 1, 1.05, 1.1])

    broken_and_clip_axes(ax, y=[0.5])

    ax.legend(loc="center")

# must be put below set_yticks or set_xticks
remove_yaxis_minor_ticks(ax2, intervals=[(0.02, 0.95)])

plt.savefig("remove_ticks_in_scaled_interval.png", dpi=144)
plt.show()
