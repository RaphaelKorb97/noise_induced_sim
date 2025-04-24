import tkinter as tk
from tkinter import ttk
from tkinter import StringVar, DoubleVar, IntVar
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import threading
import time
from simulation import VehicleSimulation

class TrafficSimApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Noise-Induced Traffic Simulation (Tkinter)")
        self.root.minsize(900, 600)
        self.dt = 0.1
        self.steps_per_update = 20
        # Variables
        self.n_vehicles = IntVar(value=22)
        self.sigma = DoubleVar(value=0.6)
        self.seed = IntVar(value=22)
        self.model = StringVar(value="SATG")
        # --- Controls ---
        controls = ttk.Frame(root)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        ttk.Label(controls, text="Number of vehicles").grid(row=0, column=0)
        ttk.Scale(controls, from_=5, to=50, variable=self.n_vehicles, orient=tk.HORIZONTAL, length=100, command=lambda e: self.update_label(self.n_vehicles, self.n_label)).grid(row=0, column=1)
        self.n_label = ttk.Label(controls, text=f"{self.n_vehicles.get()}")
        self.n_label.grid(row=0, column=2)
        ttk.Label(controls, text="Sigma (noise)").grid(row=1, column=0)
        ttk.Scale(controls, from_=0.0, to=2.0, variable=self.sigma, orient=tk.HORIZONTAL, length=100, command=lambda e: self.update_label(self.sigma, self.sigma_label, fmt="{:.2f}")).grid(row=1, column=1)
        self.sigma_label = ttk.Label(controls, text=f"{self.sigma.get():.2f}")
        self.sigma_label.grid(row=1, column=2)
        ttk.Label(controls, text="Seed").grid(row=2, column=0)
        ttk.Entry(controls, textvariable=self.seed, width=8).grid(row=2, column=1)
        ttk.Label(controls, text="Model").grid(row=3, column=0)
        model_box = ttk.Combobox(controls, textvariable=self.model, values=[
            "SOVM", "SOVM unstable", "SFVDM", "SFVDM unstable",
            "Tomer et al.", "Tomer et al. unstable",
            "SIDM", "SIDM unstable", "SATG"
        ], state="readonly", width=16)
        model_box.grid(row=3, column=1, columnspan=2)
        # Buttons
        self.setup_btn = ttk.Button(controls, text="Setup", command=self.setup_simulation)
        self.setup_btn.grid(row=4, column=0, pady=5)
        self.move_btn = ttk.Button(controls, text="Move", command=self.toggle_run)
        self.move_btn.grid(row=4, column=1, pady=5)
        # --- Plots ---
        frame = ttk.Frame(root)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.fig, (self.ax_traj, self.ax_stats) = plt.subplots(1, 2, figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.draw()  # Force initial draw
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.fig.tight_layout()
        # --- Simulation ---
        self.sim = None
        self.running = False
        self.sim_thread = None
        self.setup_simulation()

    def update_label(self, var, label, fmt="{}"):
        label.config(text=fmt.format(var.get()))

    def setup_simulation(self):
        self.running = False
        self.move_btn.config(text="Move")
        self.sim = VehicleSimulation(
            n_vehicles=self.n_vehicles.get(),
            model=self.model.get(),
            sigma=self.sigma.get(),
            seed=self.seed.get(),
            dt=self.dt
        )
        self.update_plots()

    def toggle_run(self):
        if self.running:
            self.running = False
            self.move_btn.config(text="Move")
        else:
            self.running = True
            self.move_btn.config(text="Pause")
            self.sim_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.sim_thread.start()

    def run_simulation(self):
        while self.running:
            for _ in range(self.steps_per_update):
                self.sim.step()
            self.update_plots()
            time.sleep(0.05)

    def update_plots(self):
        self.ax_traj.clear()
        self.ax_stats.clear()
        xs = self.sim.history["x"]
        ts = self.sim.history["time"]
        # Trajectories plot
        if len(xs) > 2:
            xs = np.array(xs)
            ts = np.array(ts)
            n_vehicles = xs.shape[1]
            for i in range(n_vehicles):
                self.ax_traj.plot(xs[:, i], ts, lw=0.7)
        self.ax_traj.set_xlabel("Space [m]")
        self.ax_traj.set_ylabel("Time [s]")
        self.ax_traj.set_xlim(0, self.sim.L)
        self.ax_traj.set_title("Trajectories")
        # Time series plot
        if len(self.sim.history["mean_speed"]) > 2:
            line1, = self.ax_stats.plot(ts, self.sim.history["mean_speed"], label="Mean speed [m/s]")
            line2, = self.ax_stats.plot(ts, self.sim.history["gap_sd"], label="Gap SD [m]")
            handles, labels = self.ax_stats.get_legend_handles_labels()
            if labels:
                self.ax_stats.legend()
        self.ax_stats.set_xlabel("Time [s]")
        self.ax_stats.set_title("Time sequences")
        self.fig.tight_layout()
        self.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSimApp(root)
    print("Starting mainloop...")
    root.mainloop()
