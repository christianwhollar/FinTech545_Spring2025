import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def problem_five():
    df = pd.read_csv("DailyReturn.csv")

    # Part B
    lambdas = np.linspace(0.1, 0.9, 9)  # lambda values from 0.1 to 0.9
    explained_variances = []

    for lambd in lambdas:
        cov_matrix = ew_cov_matrix(df.drop(columns="Date").values, lambd=lambd)
        
        #  PCA
        pca = PCA()
        pca.fit(cov_matrix)
        
        # compute cumulative explained variance
        cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
        explained_variances.append(cumulative_variance)
    
    # plot the cumulative explained variance
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, lambd in enumerate(lambdas):
        plt.plot(range(1, len(explained_variances[i]) + 1), explained_variances[i], label=f"λ = {lambd:.1f}")

    plt.xlabel("Number of Principal Components")
    plt.ylabel("Cumulative Variance Explained")
    plt.title("PCA Cumulative Variance Explained for Different λ")
    plt.legend()

    fig.savefig("img/lambda_cumulative_variance.png")


def ew_cov_matrix(returns, lambd):
    T, N = returns.shape
    # calculate weights
    weights = np.array([(1 - lambd) * (lambd ** i) for i in range(T - 1, -1, -1)])

    # normalize weights
    weights /= weights.sum() 
    
    # calculate the mean adjusted returns
    mean_adj_returns = returns - returns.mean()

    # calculate the weighted covariance matrix
    weighted_cov = (mean_adj_returns.T @ np.diag(weights) @ mean_adj_returns)
    return weighted_cov