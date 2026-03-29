import numpy as np
import pandas as pd
from scipy.stats import norm


def bafo(
    signal,
    normal_signal,
    prior_fault=0.01,
    lambda_slope=1.6,
    tau=50,
    forgetting=0.995,
    threshold=0.75
):
    signal = np.asarray(signal)
    normal_signal = np.asarray(normal_signal)

    # smoothing
    signal_smooth = pd.Series(signal).rolling(5, min_periods=1).mean().values

    # baseline
    mu_norm = np.mean(normal_signal)
    sigma_norm = np.std(normal_signal) + 1e-8

    # slope
    slope = np.gradient(signal_smooth)
    slope = pd.Series(slope).rolling(5, min_periods=1).mean().values
    slope = np.clip(slope, -3, 3)

    # combined signal
    x_signal = (signal_smooth - mu_norm) / sigma_norm + lambda_slope * slope

    alpha = np.exp(-1 / tau)
    posterior = prior_fault

    posterior_series = []
    deg_series = []
    deg_est = 0

    for x in x_signal:

        posterior_memory = forgetting * posterior
        posterior_pred = alpha * posterior_memory + (1 - alpha) * prior_fault

        # adaptive baseline
        if posterior < 0.1:
            mu_norm = forgetting * mu_norm + (1 - forgetting) * x
            sigma_norm = np.sqrt(
                forgetting * sigma_norm**2 +
                (1 - forgetting) * (x - mu_norm)**2
            )

        z = (x - mu_norm) / (sigma_norm + 1e-8)
        z = np.tanh(z / 3) * 3

        p_norm = norm.pdf(z, 0, 1)
        p_fault = norm.pdf(abs(z), loc=3.0, scale=1.5)

        posterior_bayes = (p_fault * posterior_pred) / (
            (p_fault * posterior_pred) + (p_norm * (1 - posterior_pred)) + 1e-12
        )

        if posterior > 0.95 and posterior_bayes > posterior_pred:
            posterior_bayes = posterior_pred

        gamma = 0.05 + 0.15 * abs(z) / (2 + abs(z))

        posterior_update = posterior_pred + gamma * (posterior_bayes - posterior_pred)
        posterior = 0.9 * posterior_update + 0.1 * posterior_bayes
        posterior = np.clip(posterior, 1e-6, 1 - 1e-6)

        # degradation
        deg_est = 0.995 * deg_est + (1 - 0.995) * posterior

        posterior_series.append(posterior)
        deg_series.append(deg_est)

    posterior_series = np.array(posterior_series)
    deg_series = np.array(deg_series)

    detection_index = next(
        (i for i, p in enumerate(posterior_series) if p >= threshold),
        None
    )

    return {
        "posterior": posterior_series,
        "deg_est": deg_series,
        "detected_index": detection_index
    }