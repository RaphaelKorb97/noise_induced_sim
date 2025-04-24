import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QComboBox, QSlider, QLineEdit,
                           QPushButton, QFrame, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from simulation import VehicleSimulation
from matplotlib.patches import Circle

class SimulationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traffic Simulation (Sugiyama et al. 2007)")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set Apple-like style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #d2d2d7;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: #1d1d1f;
            }
            QLabel {
                color: #1d1d1f;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
            QPushButton:pressed {
                background-color: #0062b9;
            }
            QComboBox {
                border: 1px solid #d2d2d7;
                border-radius: 6px;
                padding: 6px;
                background-color: white;
                min-width: 200px;
                color: #1d1d1f;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #d2d2d7;
                height: 4px;
                background: white;
                margin: 0px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #0071e3;
                border: none;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #0077ed;
            }
            QLineEdit {
                border: 1px solid #d2d2d7;
                border-radius: 6px;
                padding: 6px;
                background-color: white;
                color: #1d1d1f;
                font-size: 12px;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create control panel
        control_panel = QGroupBox("Controls")
        control_panel.setMaximumWidth(300)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(12)

        # Model selection
        model_group = QGroupBox("Model Settings")
        model_layout = QVBoxLayout(model_group)
        model_layout.setSpacing(8)
        
        model_label = QLabel("Model:")
        model_layout.addWidget(model_label)
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "SOVM", "SOVM unstable", "SFVDM", "SFVDM unstable",
            "Tomer et al.", "Tomer et al. unstable",
            "SIDM", "SIDM unstable", "SATG"
        ])
        self.model_combo.setCurrentText("SATG")
        self.model_combo.currentTextChanged.connect(self.change_model)
        model_layout.addWidget(self.model_combo)

        # Sigma control
        sigma_label = QLabel("Sigma:")
        model_layout.addWidget(sigma_label)
        self.sigma_slider = QSlider(Qt.Horizontal)
        self.sigma_slider.setMinimum(0)
        self.sigma_slider.setMaximum(200)
        self.sigma_slider.setValue(60)
        self.sigma_slider.valueChanged.connect(self.change_sigma)
        model_layout.addWidget(self.sigma_slider)
        self.sigma_label = QLabel("0.60")
        model_layout.addWidget(self.sigma_label)

        # Speed control
        speed_label = QLabel("Speed (ticks/sec):")
        model_layout.addWidget(speed_label)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(300)
        self.speed_slider.setValue(20)
        self.speed_slider.valueChanged.connect(self.change_speed)
        model_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel("20")
        model_layout.addWidget(self.speed_label)

        # Seed control
        seed_label = QLabel("Seed:")
        model_layout.addWidget(seed_label)
        self.seed_input = QLineEdit("22")
        model_layout.addWidget(self.seed_input)

        control_layout.addWidget(model_group)

        # Control buttons
        button_group = QGroupBox("Simulation Control")
        button_layout = QVBoxLayout(button_group)
        button_layout.setSpacing(8)
        
        # Tick counter
        self.tick_counter = 0
        tick_label = QLabel("Ticks:")
        button_layout.addWidget(tick_label)
        self.tick_display = QLabel("0")
        button_layout.addWidget(self.tick_display)
        
        # Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_simulation)
        button_layout.addWidget(self.reset_button)
        
        # Start/Stop button
        self.start_stop_button = QPushButton("Stop")
        self.start_stop_button.clicked.connect(self.toggle_simulation)
        button_layout.addWidget(self.start_stop_button)
        
        # Perturbation button
        self.perturb_button = QPushButton("Perturbation")
        self.perturb_button.clicked.connect(self.apply_perturbation)
        button_layout.addWidget(self.perturb_button)
        
        control_layout.addWidget(button_group)
        control_layout.addStretch()
        layout.addWidget(control_panel)

        # Create plot area
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.setSpacing(20)
        
        # Create the figure with white background
        self.fig = Figure(figsize=(12, 8), facecolor='white')
        self.canvas = FigureCanvas(self.fig)
        plot_layout.addWidget(self.canvas)
        layout.addWidget(plot_widget)

        # Setup plots
        self.setup_plots()

        # Create simulation
        self.sim = VehicleSimulation(
            n_vehicles=22,
            circuit_length=231.0,
            dt=0.05,
            model="SATG",
            sigma=0.6,
            seed=22
        )

        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(50)  # Update every 50ms (20 FPS)
        self.simulation_running = True
        self.speed_multiplier = 1.0  # Initialize speed multiplier

    def setup_plots(self):
        # Create a 2x1 grid with the left column split into two rows
        gs = self.fig.add_gridspec(2, 2, width_ratios=[1, 1.5], height_ratios=[1, 1])
        
        # Live simulation (top left)
        self.ax_live = self.fig.add_subplot(gs[0, 0])
        radius = 231.0/(2*np.pi)
        self.circle = Circle((0, 0), radius, fill=False, color='#d2d2d7', linestyle='--')
        self.ax_live.add_patch(self.circle)
        self.ax_live.set_aspect('equal')
        self.ax_live.set_xlim(-radius*1.2, radius*1.2)
        self.ax_live.set_ylim(-radius*1.2, radius*1.2)
        self.ax_live.grid(True, color='#f0f0f0')
        self.ax_live.set_title("Live Simulation", pad=20)
        self.ax_live.set_facecolor('white')

        # Initialize vehicle plots
        self.vehicle_plots = []
        angles = np.zeros(22)
        x_pos = radius * np.cos(angles)
        y_pos = radius * np.sin(angles)
        for i in range(22):
            if i == 21:
                plot, = self.ax_live.plot(x_pos[i], y_pos[i], 'bo', markersize=10)
            else:
                plot, = self.ax_live.plot(x_pos[i], y_pos[i], 'ko', markersize=8)
            self.vehicle_plots.append(plot)

        # Time series (bottom left)
        self.ax_time = self.fig.add_subplot(gs[1, 0])
        self.mean_speed_line, = self.ax_time.plot([], [], 'b-', label='Mean speed [m/s]')
        self.gap_sd_line, = self.ax_time.plot([], [], 'r-', label='Gap SD [m]')
        self.ax_time.set_xlabel("Time [s]", labelpad=10)
        self.ax_time.set_ylabel("Value", labelpad=10)
        self.ax_time.set_title("Time Series", pad=20)
        self.ax_time.legend()
        self.ax_time.grid(True, color='#f0f0f0')
        self.ax_time.set_facecolor('white')

        # Trajectories (right side, full height)
        self.ax_traj = self.fig.add_subplot(gs[:, 1])
        self.ax_traj.set_xlabel("Space [m]", labelpad=10)
        self.ax_traj.set_ylabel("Time [s]", labelpad=10)
        self.ax_traj.set_title("Trajectories", pad=20)
        self.ax_traj.grid(True, color='#f0f0f0')
        self.ax_traj.set_xlim(-115, 115)
        self.ax_traj.set_ylim(0, 200)
        self.ax_traj.set_facecolor('white')
        
        # Initialize trajectory lines
        self.traj_lines = []
        self.traj_data = {i: {'x': [], 'y': []} for i in range(22)}
        for i in range(22):
            if i == 21:  # Special blue vehicle
                line, = self.ax_traj.plot([], [], 'b-', linewidth=2.0, alpha=1.0)
            else:
                line, = self.ax_traj.plot([], [], 'k-', linewidth=1.0, alpha=0.6)
            self.traj_lines.append(line)

        # Adjust layout
        self.fig.tight_layout(pad=3.0)

    def update_plots(self):
        if self.simulation_running:
            # Run multiple simulation steps based on speed setting
            steps = int(self.speed_multiplier)
            for _ in range(steps):
                self.sim.step()
                self.tick_counter += 1
            # Update tick display
            self.tick_display.setText(str(self.tick_counter))
            
            # Update live view
            radius = 231.0/(2*np.pi)
            angles = 2 * np.pi * self.sim.x / 231.0
            for i, (angle, plot) in enumerate(zip(angles, self.vehicle_plots)):
                x_pos = radius * np.cos(angle)
                y_pos = radius * np.sin(angle)
                plot.set_data([x_pos], [y_pos])
            
            # Update trajectories and time series
            if len(self.sim.history["x"]) > 2:
                x = np.array(self.sim.history["x"])
                time = np.array(self.sim.history["time"])
                current_time = time[-1]
                
                # Check if we need to reset trajectories (reached top of diagram)
                if current_time >= 200:
                    # Reset simulation time but keep history for time series
                    self.sim.time = 0
                    # Clear only trajectory data
                    for i in range(22):
                        self.traj_data[i]['x'] = []
                        self.traj_data[i]['y'] = []
                    # Keep time series data but reset trajectory history
                    self.sim.history["x"] = [self.sim.x.copy()]
                    self.sim.history["time"] = [0]
                    self.sim.history["mean_speed"] = [np.mean(self.sim.speed)]
                    self.sim.history["gap_sd"] = [np.std(self.sim.gap)]
                    return
                
                # Process each vehicle's trajectory
                circuit_length = 231.0
                
                for i in range(22):
                    # Get the latest point
                    x_pos = x[-1, i]
                    
                    # Center and unwrap x position
                    x_centered = x_pos - circuit_length/2
                    rounds = np.floor(x_pos / circuit_length)
                    x_unwrapped = x_centered - (rounds * circuit_length)
                    
                    # Add new point if it doesn't create a wrap-around line
                    if (len(self.traj_data[i]['x']) == 0 or 
                        abs(x_unwrapped - self.traj_data[i]['x'][-1]) < circuit_length/2):
                        self.traj_data[i]['x'].append(x_unwrapped)
                        self.traj_data[i]['y'].append(current_time)
                    else:
                        # Start a new segment
                        self.traj_data[i]['x'].append(None)  # Break the line
                        self.traj_data[i]['y'].append(None)
                        self.traj_data[i]['x'].append(x_unwrapped)
                        self.traj_data[i]['y'].append(current_time)
                    
                    # Update the line
                    self.traj_lines[i].set_data(self.traj_data[i]['x'], self.traj_data[i]['y'])
                
                # Update time series - show only the most recent 200 seconds
                window_start = max(0, current_time - 200)
                window_end = current_time
                
                # Convert history lists to numpy arrays for comparison
                time_array = np.array(self.sim.history["time"])
                mean_speed_array = np.array(self.sim.history["mean_speed"])
                gap_sd_array = np.array(self.sim.history["gap_sd"])
                
                # Filter data to show only the current window
                mask = (time_array >= window_start) & (time_array <= window_end)
                window_time = time_array[mask]
                window_mean_speed = mean_speed_array[mask]
                window_gap_sd = gap_sd_array[mask]
                
                # Update the lines with windowed data
                self.mean_speed_line.set_data(window_time, window_mean_speed)
                self.gap_sd_line.set_data(window_time, window_gap_sd)
                
                # Set the x-axis limits to show the current window
                self.ax_time.set_xlim(window_start, window_end)
                self.ax_time.relim()
                self.ax_time.autoscale_view()
            
            self.canvas.draw()

    def change_model(self, model):
        self.sim.model = model

    def change_sigma(self):
        value = self.sigma_slider.value() / 100.0
        self.sigma_label.setText(f"{value:.2f}")
        self.sim.sigma = value

    def change_speed(self):
        speed = self.speed_slider.value()
        self.speed_label.setText(str(speed))
        self.timer.setInterval(50)  # Keep constant 20 FPS refresh rate
        # Store the speed multiplier for use in update_plots
        self.speed_multiplier = speed / 20

    def toggle_simulation(self):
        self.simulation_running = not self.simulation_running
        if self.simulation_running:
            self.start_stop_button.setText("Stop")
        else:
            self.start_stop_button.setText("Start")

    def reset_simulation(self):
        try:
            seed = int(self.seed_input.text())
        except ValueError:
            seed = 22

        self.sim = VehicleSimulation(
            n_vehicles=22,
            circuit_length=231.0,
            dt=0.05,
            model=self.model_combo.currentText(),
            sigma=self.sigma_slider.value() / 100.0,
            seed=seed
        )
        
        # Reset tick counter
        self.tick_counter = 0
        self.tick_display.setText("0")
        
        # Clear trajectory data
        for i in range(22):
            self.traj_data[i] = {'x': [], 'y': []}
            self.traj_lines[i].set_data([], [])
        
        # Clear time series data
        self.mean_speed_line.set_data([], [])
        self.gap_sd_line.set_data([], [])
        
        # Reset axes limits
        self.ax_traj.set_ylim(0, 200)
        self.ax_time.set_xlim(0, 200)
        
        # Redraw canvas
        self.canvas.draw()

    def apply_perturbation(self):
        """Apply a braking perturbation to the blue vehicle"""
        if self.sim:
            self.sim.apply_perturbation()

def main():
    app = QApplication(sys.argv)
    window = SimulationGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
