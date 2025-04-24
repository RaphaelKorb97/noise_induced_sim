import numpy as np
from utils import tanh, Z, logsumexp

class VehicleSimulation:
    def __init__(self, n_vehicles=22, circuit_length=231.0, dt=0.05, model="SATG", sigma=0.6, seed=0):
        self.n = n_vehicles
        self.L = circuit_length
        self.dt = dt
        self.model = model
        self.sigma = sigma
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.reset()

    def reset(self):
        # Evenly spaced initial positions, all same speed
        self.x = np.linspace(0, self.L, self.n, endpoint=False)
        self.speed = np.full(self.n, 5.0)  # initial speed (m/s) matching NetLogo
        self.acc = np.zeros(self.n)
        self.gap = np.zeros(self.n)
        self.time = 0.0
        # Clear all history
        self.history = {"x": [], "speed": [], "gap": [], "mean_speed": [], "gap_sd": [], "time": []}
        # Add initial state to history
        self.history["x"].append(self.x.copy())
        self.history["speed"].append(self.speed.copy())
        self.history["gap"].append(self.gap.copy())
        self.history["mean_speed"].append(np.mean(self.speed))
        self.history["gap_sd"].append(np.std(self.gap))
        self.history["time"].append(self.time)

    def apply_perturbation(self):
        """Apply a braking perturbation to the blue vehicle (index 21)"""
        # Reduce speed of blue vehicle by 50%
        self.speed[21] *= 0.2

    def step(self):
        n = self.n
        L = self.L
        dt = self.dt
        sigma = self.sigma
        model = self.model
        x = self.x
        speed = self.speed
        
        # Initialize arrays
        gap = np.zeros(n)
        acc = np.zeros(n)
        noise_volatility = np.zeros(n)
        
        # Compute gaps and relative speeds with proper periodic boundary handling
        for i in range(n):
            next_i = (i + 1) % n
            # Calculate gap with proper periodic boundary handling
            raw_gap = x[next_i] - x[i]
            if raw_gap < 0:
                raw_gap += L
            # Calculate gap exactly as in NetLogo: gap = next_x - x - 5 + floor(who/21) * world-width
                   # Subtract vehicle length and ensure minimum gap
            gap[i] = max(raw_gap - 5, 0.1)  # 5m vehicle length, 0.1m minimum gap

        
        rel_speed = np.roll(speed, -1) - speed
        
        # Model selection
        for i in range(n):
            g = gap[i]
            v = speed[i]
            dv = rel_speed[i]
            
            if model == "SOVM":
                acc[i] = (self.V(g) - v) / 0.5
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1))))
            elif model == "SOVM unstable":
                acc[i] = (self.V(g) - v) / 1.0
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1))))
            elif model == "SFVDM":
                acc[i] = (self.V(g) - v) / 2.5 + dv / 2.0
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1))))
            elif model == "SFVDM unstable":
                acc[i] = (self.V(g) - v) / 2.5 + dv / 2.7
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1))))
            elif model == "Tomer et al.":
                acc[i] = 7 * (1 - (v * 2 + 5) / (g + 5)) - (Z(-dv)) ** 2 / 2 / g - 2 * Z(v - 20)
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1)))) 
            elif model == "Tomer et al. unstable":
                acc[i] = 3 * (1 - (v * 2 + 5) / (g + 5)) - (Z(-dv)) ** 2 / 2 / g - 2 * Z(v - 20)
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1))))
            elif model == "SIDM":
                # f(v_n,Dv_n) = 2 + v_n - v_n * Dv_n / A, with A = 4
                # v = GEschwidigkeit, 20= v0= Wunschgeschwindigkeit, g=gap=Nettoabstand
                f = 2 + v - v * dv / 4
                acc[i] = 2 * (1 - (f / g) ** 2 - (v / 20) ** 4)
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1))))
            elif model == "SIDM unstable":
                # f(v_n,Dv_n) = 2 + v_n - v_n * Dv_n / A, with A = 5
                f = 2 + 1 * v - v * dv / 5
                acc[i] = 2 * (1 - (f / g) ** 2 - (v / 20) ** 4)
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1))))
            elif model == "SATG":
                # Calculate time gap exactly as in NetLogo
                bounded_time_gap = logsumexp(logsumexp(g / logsumexp(v, 1e-10, 0.01), 4, -0.01), 0.1, 0.01)
                
                # Calculate acceleration exactly as in NetLogo
                acc[i] = (0.2 * (g - v) + dv) / bounded_time_gap
                
                # Calculate noise volatility for this vehicle
                noise_volatility[i] = sigma / (1 + np.exp(min(700, -1000 * (v - 0.1))))
        
        # Update speeds with noise using Euler-Maruyama scheme
        # Generate Wiener process increments dW_n
        dW = self.rng.normal(0, 1, n)
        valid = np.abs(acc) < 1e5
        
        # Calculate new speeds using Euler-Maruyama discretization:
        # v_n(t + dt) = v_n(t) + dt * acc + s(v_n) * sqrt(dt) * dW_n
        new_speed = np.copy(speed)
        new_speed[valid] = speed[valid] + dt * acc[valid] + np.sqrt(dt) * noise_volatility[valid] * dW[valid]
        
        # Ensure minimum speed to prevent complete stops
        new_speed = np.maximum(new_speed, 0.1)
        
        # Calculate new positions
        new_x = x + new_speed * dt
        
        # Enforce minimum spacing between vehicles
        for i in range(n):
            next_i = (i + 1) % n
            # Calculate actual distance between vehicles
            dist = new_x[next_i] - new_x[i]
            if dist < 0:
                dist += L
            # If vehicles are too close, adjust their positions
            if dist < 5:  # Minimum safe distance (vehicle length)
                # Move the following vehicle back
                new_x[next_i] = new_x[i] + 5
                # Ensure periodic boundary
                if new_x[next_i] >= L:
                    new_x[next_i] -= L
        
        # Apply periodic boundary conditions
        new_x = new_x % L
        
        # Update state
        self.x = new_x
        self.speed = new_speed
        self.acc = acc
        self.gap = gap
        self.time += dt
        self.history["x"].append(new_x.copy())
        self.history["speed"].append(new_speed.copy())
        self.history["gap"].append(gap.copy())
        self.history["mean_speed"].append(np.mean(new_speed))
        self.history["gap_sd"].append(np.std(gap))
        self.history["time"].append(self.time)

    @staticmethod
    def V(s):
        return 13.7 * tanh(s / 20 - 0.5) + 6.3
