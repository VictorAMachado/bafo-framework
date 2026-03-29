import numpy as np

def exposure(deg, threshold):
    return np.sum(deg > threshold)

def exposure_norm(deg, threshold):
    return np.mean(deg > threshold)

def exposure_weighted(deg, threshold):
    return np.sum((deg - threshold) * (deg > threshold))

def exposure_weighted_norm(deg, threshold):
    excess = (deg - threshold) * (deg > threshold)
    return np.sum(excess) / len(deg)