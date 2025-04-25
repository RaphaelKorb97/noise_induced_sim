# Noise-Induced Traffic Simulation

A Python implementation of microscopic traffic flow models to study the emergence of stop-and-go waves in traffic systems, with a particular focus on noise-induced phenomena. This simulation compares different traffic models including the Social Force Model (SFM) and the Speed-Induced Decision Making (SIDM) model.

## Project Description

This simulation explores how different levels of noise and various model parameters affect traffic flow patterns, particularly the emergence of stop-and-go waves. It implements both stable and unstable variants of several traffic models, allowing for comparative analysis of traffic behavior under different conditions.

The project is inspired by the experiment by Sugiyama et al. (2007), where 22 vehicles drive around a 231-meter long single-lane roundabout, starting from uniform initial conditions. After a transition period, stop-and-go waves emerge naturally.

## Features

- Multiple traffic flow models:
  - SOVM (Stable/Unstable Optimal Velocity Model)
  - SFVDM (Stable/Unstable Full Velocity Difference Model)
  - Tomer et al. model (Stable/Unstable)
  - SIDM (Stable/Unstable Speed-Induced Decision Making)
  - SATG (Stochastic Adaptive Time Gap)
- Real-time visualization with multiple views:
  - Live simulation view
  - Trajectory plots
  - Time series analysis
- Customizable parameters:
  - Number of vehicles
  - Noise intensity (sigma)
  - Model selection
  - Simulation speed
- PyQt5-based GUI interface
- Data export capabilities for analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RaphaelKorb97/noise_induced_sim.git
cd noise_induced_sim
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the simulation with:
```bash
python main.py
```

### Key Features in the Interface
- Model Selection: Choose between different traffic models
- Noise Control: Adjust the noise intensity (sigma) using the slider
- Speed Control: Modify the simulation speed
- Perturbation Button: Apply a braking perturbation to the blue vehicle
- Reset Button: Restart the simulation with current parameters

## Models

### SOVM (Optimal Velocity Model)
- **Stable Version**: Maintains smooth traffic flow
- **Unstable Version**: Can produce stop-and-go waves
- Key parameters: Sensitivity parameter τ (2.0 for stable, 1.0 for unstable)

### SFVDM (Full Velocity Difference Model)
- **Stable Version**: Combines optimal velocity and relative speed
- **Unstable Version**: Enhanced sensitivity to relative speed
- Key parameters: κ (2.0 for stable, 2.7 for unstable)

### Tomer et al. Model
- **Stable Version**: Inertial model with balanced parameters
- **Unstable Version**: Increased sensitivity to speed differences
- Key parameters: K (7.0 for stable, 3.0 for unstable)

### SIDM (Speed-Induced Decision Making)
- **Stable Version**: Balanced acceleration and deceleration
- **Unstable Version**: Enhanced sensitivity to speed differences
- Key parameters: A (4.0 for stable, 5.0 for unstable)

### SATG (Stochastic Adaptive Time Gap)
- Adaptive time gap model with bounded parameters
- Smooth transitions between acceleration and deceleration

## References

1. Sugiyama, Y., Fukui, M., Kikuchi, M., Hasebe, K., Nakayama, A., Nishinari, K., ... & Yukawa, S. (2007). Traffic jams without bottlenecks—experimental evidence for the physical mechanism of the formation of a jam. New Journal of Physics, 10(3), 033001.

2. Tian, J. F., Jia, B., & Li, X. G. (2016). A new car following model: comprehensive optimal velocity model. Communications in Nonlinear Science and Numerical Simulation, 36, 167-176.

3. Bando, M., Hasebe, K., Nakayama, A., Shibata, A., & Sugiyama, Y. (1995). Dynamical model of traffic congestion and numerical simulation. Physical review E, 51(2), 1035.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Raphael Korbmacher
