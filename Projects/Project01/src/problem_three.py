import pandas as pd
import numpy as np
import statsmodels.api as sm

def problem_three():
    df = pd.read_csv("problem3.csv")

    # Part A
    X = df[["x1", "x2"]].values
    n = X.shape[0]

    mu_hat = np.mean(X, axis=0)
    Sigma_hat = np.cov(X, rowvar=False)

    # Part B
    # Method 1 - Conditional Distriubtion
    # this is taken from Multivariate Statistics lecture notes
    x_one_val = 0.6
    mu1, mu2 = mu_hat[0], mu_hat[1]
    sigma_11 = Sigma_hat[0, 0]
    sigma_12 = Sigma_hat[0, 1]
    sigma_21 = Sigma_hat[1, 0]
    sigma_22 = Sigma_hat[1, 1]

    cond_mean_A = mu2 + (sigma_12 / sigma_11) * (x_one_val - mu1)
    cond_var_A = sigma_22 - sigma_21 * sigma_11 ** -1 * sigma_12

    # Method 2 - Linear Regression
    # this is taken from Multivariate Statistics lecture notes
    X = df[['x1']]
    y = df['x2'] 

    # add constant
    X = sm.add_constant(X)

    # create and fit the model
    model = sm.OLS(y, X).fit()

    # get the parameters
    beta0 = model.params['const']
    beta1 = model.params['x1']
    x_one_val = 0.6

    # calculate the mean and variance
    cond_mean_B = beta0 + beta1*x_one_val
    cond_var_B = model.mse_resid

    # Part C
    #  
    # cholesky decomposition of Sigma_hat
    L = np.linalg.cholesky(Sigma_hat)

    # generate random normal values
    N = 100000000
    Z = np.random.normal(size=(N, 2))

    # simulate the data
    X_sim = mu_hat + Z @ L.T
    tolerance = 0.05

    # get the values within the tolerance
    mask = np.abs(X_sim[:,0] - x_one_val) < tolerance

    # get the values of X2 conditioned on X1
    X2_conditioned = X_sim[mask, 1]

    # calculate the mean and variance
    cond_mean_sim = np.mean(X2_conditioned)
    cond_var_sim  = np.var(X2_conditioned, ddof=1)
    
    print("PROBLEM THREE:")
    print("\tPart A:")
    print("\t\tSample Mean:")
    print("\t\t", str(mu_hat).replace('\n', '\n\t\t'))
    print("\t\tSample Covariance Matrix:")
    print("\t\t", str(Sigma_hat).replace('\n', '\n\t\t'))

    print("\tPart B:")
    print("\t\tMethod 1:")
    print(f"\t\t\tConditional Mean: {cond_mean_A:.6f}")
    print(f"\t\t\tConditional Variance: {cond_var_A:.6f}")
    print("\t\tMethod 2:")
    print(f"\t\t\tConditional Mean: {cond_mean_B:.6f}")
    print(f"\t\t\tConditional Variance: {cond_var_B:.6f}")

    print("\tPart C:")
    print("\t\tConditional Mean (Simulated):")
    print(f"\t\t\t{cond_mean_sim:.6f}")
    print("\t\tConditional Variance (Simulated):")
    print(f"\t\t\t{cond_var_sim:.6f}")
    