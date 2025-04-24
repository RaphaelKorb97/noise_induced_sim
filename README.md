# Noise-Induced Traffic Simulation

This project implements a microscopic traffic flow model to study the emergence of stop-and-go waves in traffic systems, with a particular focus on the effects of noise-induced phenomena. The simulation compares different traffic models including the Social Force Model (SFM) and the Speed-Induced Decision Making (SIDM) model.

## Project Description

The simulation explores how different levels of noise and various model parameters affect traffic flow patterns, particularly the emergence of stop-and-go waves. It implements both stable and unstable variants of the SIDM model, allowing for comparative analysis of traffic behavior under different conditions.

## Models

### SIDM (Speed-Induced Decision Making)
- **SIDM Stable**: A variant of the model that tends to maintain smooth traffic flow
- **SIDM Unstable**: A variant that can produce stop-and-go waves under certain conditions

The models incorporate:
- Optimal velocity functions
- Gap-dependent acceleration
- Noise-induced fluctuations
- Periodic boundary conditions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/noise-induced-sim.git
cd noise-induced-sim
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Features

- Multiple traffic flow models (SIDM stable/unstable)
- Customizable simulation parameters
- Real-time visualization of traffic patterns
- Data export for analysis
- Comparative analysis tools

## Usage

1. Run the main simulation:
```bash
python main.py
```

2. Adjust parameters in the configuration file to explore different scenarios:
- Number of vehicles
- Noise intensity
- Model parameters
- Simulation duration

## References

1. Tian, J. F., Jia, B., & Li, X. G. (2016). A new car following model: comprehensive optimal velocity model. Communications in Nonlinear Science and Numerical Simulation, 36, 167-176.

2. Bando, M., Hasebe, K., Nakayama, A., Shibata, A., & Sugiyama, Y. (1995). Dynamical model of traffic congestion and numerical simulation. Physical review E, 51(2), 1035.

## Credits

Developed by Raphael Korbmacher

## License

This project is licensed under the MIT License - see the LICENSE file for details.
