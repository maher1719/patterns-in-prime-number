import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

# ========================
# Simulation Parameters
# ========================

# Time step for the animation (seconds)
dt = 0.05

# Default intrinsic spin rate (in degrees per second).
# (A spin rate of 45°/unit time means the object rotates 45 degrees every second.)
default_spin_rate_deg = 45.0  

# Default constant offset in rotation (in degrees). This offset will be added to the intrinsic spin.
# (This can be interpreted as a fixed tilt in the spinor’s orientation.)
default_rotation_offset_deg = 45.0

# Figure‐8 (Lissajous) path amplitudes in x and y directions:
default_A = 1.0   # amplitude for the x-direction (sinusoidal)
default_B = 0.5   # amplitude for the y-direction (sinusoidal with double frequency)

# ========================
# Define the “Spinor” Shape
# ========================
# We represent the spinor as an arrow-like polygon defined in local coordinates.
# The arrow points to the right in its local frame.
L = 0.2  # arrow length
W = 0.1  # arrow width

# Define vertices of a simple arrow polygon (in local coordinates)
# The arrow is defined so that its tip is at (L/2, 0) and its base is to the left.
arrow_shape = np.array([
    [-L/2, -W/2],
    [ L/2,  0.0],
    [-L/2,  W/2]
])

# ========================
# Set Up the Figure and Axes
# ========================
fig, ax = plt.subplots(figsize=(8, 6))
plt.subplots_adjust(left=0.1, bottom=0.3)  # leave space at the bottom for sliders

# Set equal aspect ratio for proper geometry display
ax.set_aspect('equal', 'box')

# Set axis limits to display both the figure-8 path and the spinning arrow
ax.set_xlim(-default_A - 0.5, default_A + 0.5)
ax.set_ylim(-default_B - 0.5, default_B + 0.5)
ax.set_title("Spinor: Intrinsic Spin + Figure-8 Path")

# Create an initial arrow patch (as a Polygon) at the origin.
# (We will update its vertices in the animation.)
arrow_patch = plt.Polygon(arrow_shape, closed=True, color='tab:blue')
ax.add_patch(arrow_patch)

# ========================
# Create Interactive Sliders
# ========================
# We create three sliders:
#   1. Spin Rate (in degrees per second)
#   2. Rotation Offset (in degrees)
#   3. Amplitudes A (x-axis amplitude) and B (y-axis amplitude) for the figure-8

# Slider for intrinsic spin rate
ax_spin = plt.axes([0.15, 0.20, 0.65, 0.03])
slider_spin = Slider(
    ax=ax_spin,
    label="Spin Rate (°/s)",
    valmin=0,
    valmax=180,
    valinit=default_spin_rate_deg,
    valstep=1,
    color='tab:orange'
)

# Slider for rotation offset (adds a constant angular shift)
ax_offset = plt.axes([0.15, 0.15, 0.65, 0.03])
slider_offset = Slider(
    ax=ax_offset,
    label="Rotation Offset (°)",
    valmin=0,
    valmax=180,
    valinit=default_rotation_offset_deg,
    valstep=1,
    color='tab:green'
)

# Slider for path amplitude in x-direction (A)
ax_A = plt.axes([0.15, 0.10, 0.65, 0.03])
slider_A = Slider(
    ax=ax_A,
    label="Path Amplitude A",
    valmin=0.1,
    valmax=2.0,
    valinit=default_A,
    valstep=0.05,
    color='tab:purple'
)

# Slider for path amplitude in y-direction (B)
ax_B = plt.axes([0.15, 0.05, 0.65, 0.03])
slider_B = Slider(
    ax=ax_B,
    label="Path Amplitude B",
    valmin=0.1,
    valmax=2.0,
    valinit=default_B,
    valstep=0.05,
    color='tab:red'
)

# ========================
# Animation Update Function
# ========================
def update(frame):
    """
    Update the position and orientation of the arrow (spinor) for each animation frame.
    
    There are two simultaneous motions:
    - The arrow’s center follows a figure-8 (Lissajous) path:
          x(t) = A * sin(t)
          y(t) = B * sin(2t)
      where A and B are the amplitudes (controlled by sliders).
    
    - The arrow itself rotates about its center:
          θ(t) = (spin_rate [in rad/s]) * t + rotation_offset
      where the spin_rate and rotation_offset (both in radians) are controlled by sliders.
    
    The rotated arrow is obtained by applying a 2D rotation matrix R(θ) to the local arrow_shape.
    """
    # Current time (in seconds)
    t = frame * dt

    # Read current slider values and convert degrees to radians where needed
    current_spin_rate = np.deg2rad(slider_spin.val)       # intrinsic spin rate in rad/s
    current_offset = np.deg2rad(slider_offset.val)          # constant rotation offset in rad
    current_A = slider_A.val  # amplitude for x-motion
    current_B = slider_B.val  # amplitude for y-motion

    # Compute the center position of the arrow along the figure-8 (Lissajous) path.
    # Here, we choose a Lissajous pattern: x = A*sin(t), y = B*sin(2t)
    x_center = current_A * np.sin(t)
    y_center = current_B * np.sin(2*t)
    center = np.array([x_center, y_center])
    
    # Compute the instantaneous rotation angle of the arrow:
    # The arrow spins intrinsically at current_spin_rate and gets an additional constant offset.
    theta = current_spin_rate * t + current_offset
    
    # Construct the 2D rotation matrix:
    #    R(θ) = [[cosθ, -sinθ],
    #            [sinθ,  cosθ]]
    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])
    
    # Apply the rotation matrix to each vertex of the arrow (defined in local coordinates)
    # and then translate by the center position.
    rotated_arrow = arrow_shape.dot(R.T) + center

    # Update the arrow polygon's vertices for the animation.
    arrow_patch.set_xy(rotated_arrow)
    
    return arrow_patch,

# ========================
# Create and Run the Animation
# ========================
# The FuncAnimation will call update(frame) repeatedly.
anim = FuncAnimation(
    fig,       # the figure object to animate
    update,    # the function that updates the animation
    frames=np.arange(0, 600),  # number of frames (here: 600 frames ≅ 30 seconds)
    interval=50,               # delay between frames in milliseconds
    blit=True
)

# Display the plot window with the animation and sliders.
plt.show()
