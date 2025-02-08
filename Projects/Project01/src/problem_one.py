import pandas as pd
import numpy as np
from scipy.stats import norm, t, skew, kurtosis

def problem_one():
    # Problem 1
    df = pd.read_csv("problem1.csv")
    X = df["X"].values

    # Part A
    mean = np.mean(X)
    variance = np.var(X)
    skewness = skew(X, bias=False)
    kurt = kurtosis(X, fisher=True, bias=False)

    # Part C
    # perform normal distribution, t-distribution fit
    mu_hat_norm, sigma_hat_norm = norm.fit(X)
    nu_hat_t, loc_hat_t, scale_hat_t = t.fit(X)

    # k_normal: normal distribution has 2 parameters (mu, sigma)
    k_normal = 2

    # k_t: t distribution has 3 parameters (nu, loc, scale)
    k_t = 3

    # sum of log-likelihoods
    ll_normal = np.sum(norm.logpdf(X, mu_hat_norm, sigma_hat_norm))
    ll_t = np.sum(t.logpdf(X, df=nu_hat_t, loc=loc_hat_t, scale=scale_hat_t))

    # AIC
    aic_normal = 2*k_normal - 2*ll_normal
    aic_t = 2*k_t - 2*ll_t

    # BIC
    n = len(X)
    bic_normal = k_normal * np.log(n) - 2*ll_normal
    bic_t = k_t * np.log(n) - 2*ll_t

    print("PROBLEM ONE:")

    print("\tPart A:")

    print(f"\t\tMean: {mean:.6f}")
    print(f"\t\tVariance: {variance:.6f}")
    print(f"\t\tSkewness: {skewness:.6f}")
    print(f"\t\tKurtosis: {kurt:.6f}")

    print("\tPart C:")

    print(f"\t\tNormal AIC: {aic_normal:.6f}")
    print(f"\t\tNormal BIC: {bic_normal:.6f}")
    print(f"\t\tt AIC: {aic_t:.6f}")
    print(f"\t\tt BIC: {bic_t:.6f}")