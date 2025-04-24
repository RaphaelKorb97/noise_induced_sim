import numpy as np

def tanh(y):
    return (1 - np.exp(-2 * y)) / (1 + np.exp(-2 * y))

def Z(y):
    return (y + np.abs(y)) / 2

def logsumexp(a, b, eps):
    # Avoid overflow
    a_eps = a / eps
    b_eps = b / eps
    if np.abs(b_eps) < 700 and np.abs(a_eps) < 700:
        return eps * np.log(np.exp(a_eps) + np.exp(b_eps))
    else:
        # Match NetLogo's behavior: if eps > 0 return max, else return min
        if eps > 0:
            return max(a, b)
        else:
            return min(a, b)
