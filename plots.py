import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.figure import Figure

class SimulationPlotter:
    def __init__(self, circuit_length=231.0, n_vehicles=22):
        self.circuit_length = circuit_length
        self.n_vehicles = n_vehicles
        self.setup_figures()
        
    def setup_figures(self):
        # Live simulation figure
        self.live_fig = Figure(figsize=(8, 8))
        self.live_ax = self.live_fig.add_subplot(111)
        radius = self.circuit_length/(2*np.pi)
        self.circle = Circle((0, 0), radius, fill=False, color='gray', linestyle='--')
        self.live_ax.add_patch(self.circle)
        self.live_ax.set_aspect('equal')
        self.live_ax.set_xlim(-radius*1.2, radius*1.2)
        self.live_ax.set_ylim(-radius*1.2, radius*1.2)
        self.live_ax.grid(True)
        self.live_ax.set_title("Live Simulation")
        
        # Vehicle scatter plots
        radius = self.circuit_length/(2*np.pi)
        angles = np.zeros(self.n_vehicles)
        x_pos = radius * np.cos(angles)
        y_pos = radius * np.sin(angles)
        self.vehicle_plots = []
        for i in range(self.n_vehicles):
            if i == 21:  # Special blue vehicle
                plot, = self.live_ax.plot(x_pos[i], y_pos[i], 'bo', markersize=10)
            else:
                plot, = self.live_ax.plot(x_pos[i], y_pos[i], 'ko', markersize=8)
            self.vehicle_plots.append(plot)
        
        # Trajectories figure
        self.traj_fig = Figure(figsize=(10, 6))
        self.traj_ax = self.traj_fig.add_subplot(111)
        self.traj_ax.set_xlabel("Space [m]")
        self.traj_ax.set_ylabel("Time [s]")
        self.traj_ax.set_title("Trajectories")
        self.traj_ax.grid(True)
        self.traj_lines = []
        for i in range(self.n_vehicles):
            if i == 21:
                line, = self.traj_ax.plot([], [], 'b-', linewidth=2)
            else:
                line, = self.traj_ax.plot([], [], 'k-', alpha=0.5)
            self.traj_lines.append(line)
        self.traj_ax.set_xlim(-115, 115)
        
        # Time series figure
        self.time_fig = Figure(figsize=(8, 8))
        self.time_ax1 = self.time_fig.add_subplot(211)
        self.time_ax2 = self.time_fig.add_subplot(212)
        
        self.mean_speed_line, = self.time_ax1.plot([], [], 'b-')
        self.gap_sd_line, = self.time_ax2.plot([], [], 'r-')
        
        self.time_ax1.set_ylabel("Mean speed [m/s]")
        self.time_ax2.set_xlabel("Time [s]")
        self.time_ax2.set_ylabel("Gap SD [m]")
        self.time_ax1.grid(True)
        self.time_ax2.grid(True)
        self.time_fig.suptitle("Time sequences")
        
        # Adjust layouts
        self.live_fig.tight_layout()
        self.traj_fig.tight_layout()
        self.time_fig.tight_layout()
    
    def update_live_view(self, x):
        radius = self.circuit_length/(2*np.pi)
        angles = 2 * np.pi * x / self.circuit_length
        for i, (angle, plot) in enumerate(zip(angles, self.vehicle_plots)):
            x_pos = radius * np.cos(angle)
            y_pos = radius * np.sin(angle)
            plot.set_data([x_pos], [y_pos])
        return self.live_fig
    
    def update_trajectories(self, history):
        x = np.array(history["x"])
        time = np.array(history["time"])
        
        # Update y-axis limits based on current time
        current_time = time[-1]
        window_start = max(0, current_time - 250)
        self.traj_ax.set_ylim(window_start, window_start + 250)
        
        # Update trajectory lines
        for i, line in enumerate(self.traj_lines):
            line.set_data(x[:, i], time)
        
        return self.traj_fig
    
    def update_time_series(self, history):
        time = history["time"]
        mean_speed = history["mean_speed"]
        gap_sd = history["gap_sd"]
        
        # Update time series data
        self.mean_speed_line.set_data(time, mean_speed)
        self.gap_sd_line.set_data(time, gap_sd)
        
        # Update axis limits
        for ax in [self.time_ax1, self.time_ax2]:
            ax.relim()
            ax.autoscale_view()
        
        return self.time_fig

def plot_live_simulation(x, circuit_length):
    """Plot the current state of vehicles on a circular track"""
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Plot circular track
    radius = circuit_length/(2*np.pi)
    circle = Circle((0, 0), radius, fill=False, color='gray', linestyle='--')
    ax.add_patch(circle)
    
    # Convert positions to angles and plot vehicles
    angles = 2 * np.pi * x / circuit_length
    for i, angle in enumerate(angles):
        # Calculate vehicle position
        x_pos = radius * np.cos(angle)
        y_pos = radius * np.sin(angle)
        
        # Plot vehicle
        if i == 21:  # Special blue vehicle
            ax.plot(x_pos, y_pos, 'bo', markersize=10)
        else:
            ax.plot(x_pos, y_pos, 'ko', markersize=8)
    
    # Set equal aspect ratio and limits
    ax.set_aspect('equal')
    ax.set_xlim(-radius*1.2, radius*1.2)
    ax.set_ylim(-radius*1.2, radius*1.2)
    ax.grid(True)
    ax.set_title("Live Simulation")
    return fig

# Trajectory plot (space vs. time, each line = one vehicle)
def plot_trajectories(history, circuit_length):
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot circular track
    radius = circuit_length/(2*np.pi)
    circle = Circle((0, 0), radius, fill=False, color='gray', linestyle='--')
    ax.add_patch(circle)
    
    # Plot vehicle trajectories
    x = np.array(history["x"])
    time = np.array(history["time"])
    
    # Convert positions to angles and plot
    angles = 2 * np.pi * x / circuit_length
    for i in range(x.shape[1]):
        if i == 21:  # Special blue vehicle
            ax.plot(time, angles[:, i], 'b-', linewidth=2)
        else:
            ax.plot(time, angles[:, i], 'k-', alpha=0.5)
    
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Position [rad]")
    ax.set_title("Vehicle Trajectories")
    ax.grid(True)
    return fig

# Time series plot (mean speed, gap SD)
def plot_time_series(history):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
    
    # Plot mean speed
    ax1.plot(history["time"], history["mean_speed"], 'b-')
    ax1.set_ylabel("Mean speed [m/s]")
    ax1.grid(True)
    
    # Plot gap standard deviation
    ax2.plot(history["time"], history["gap_sd"], 'r-')
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Gap SD [m]")
    ax2.grid(True)
    
    fig.suptitle("Time Series")
    return fig
