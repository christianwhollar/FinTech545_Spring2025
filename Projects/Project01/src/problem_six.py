import pandas as pd
import numpy as np
import time
from scipy.linalg import cholesky
from sklearn.decomposition import PCA

def problem_six():
    df = pd.read_csv("problem6.csv")
    cov_matrix = df.cov().values
    raw_data = df.values
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    eigenvalues = np.clip(eigenvalues, 1e-6, None)
    cov_matrix = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

    # Part A
    time_cholesky, cov_chol = cholesky_simulation(cov_matrix, 10000)

    # Part B
    time_pca, cov_pca = pca_simulation(raw_data, 10000)

    # Part C
    frobenius_chol = np.linalg.norm(cov_chol - cov_matrix, 'fro')
    frobenius_pca = np.linalg.norm(cov_pca - cov_matrix, 'fro')

    # Part D
    eigenvalues_original = np.linalg.eigvalsh(cov_matrix)[::-1]  
    eigenvalues_chol = np.linalg.eigvalsh(cov_chol)[::-1]
    eigenvalues_pca = np.linalg.eigvalsh(cov_pca)[::-1]

    cumulative_original = np.cumsum(eigenvalues_original) / np.sum(eigenvalues_original)
    cumulative_chol = np.cumsum(eigenvalues_chol) / np.sum(eigenvalues_chol)
    cumulative_pca = np.cumsum(eigenvalues_pca) / np.sum(eigenvalues_pca)

    print("PROBLEM SIX:")

    print("\tPart A:")
    print(f"\t\tTime taken for Cholesky: {time_cholesky:.4f} seconds")
    print("\tPart B:")
    print(f"\t\tTime taken for PCA: {time_pca:.4f} seconds")

    print("\tPart C:")
    print(f"\t\tFrobenius norm for Cholesky: {frobenius_chol:.4f}")
    print(f"\t\tFrobenius norm for PCA: {frobenius_pca:.4f}")

    print("\tPart D:")
    print("\t\t:HIDDEN")
    # print("\t\tCumulative Explained Variance:")
    # print("\t\tOriginal:", cumulative_original)
    # print("\t\tCholesky:", cumulative_chol)
    # print("\t\tPCA:", cumulative_pca)


def cholesky_simulation(cov_matrix, num_draws):
    # start time
    start_cholesky = time.time()
    # Cholesky decomposition
    chol_decomp = cholesky(cov_matrix, lower=True) 
    # generate random samples
    random_samples = np.random.randn(cov_matrix.shape[0], num_draws)
    # simulate the data
    simulated_chol = chol_decomp @ random_samples
    # stop time
    end_cholesky = time.time()
    # calculate the covariance matrix
    cov_chol = np.cov(simulated_chol)
    return end_cholesky - start_cholesky, cov_chol

def pca_simulation(raw_data, num_draws):
    # start time
    start_pca = time.time()
    # PCA fit
    pca = PCA(n_components=0.75)
    pca.fit(raw_data)
    n_components = pca.n_components_
    # generate random samples
    Z = np.random.randn(num_draws, n_components)
    Z_scaled = Z * np.sqrt(pca.explained_variance_)
    # reconstruct the data
    pca_reconstructed = pca.inverse_transform(Z_scaled)
    # stop time
    end_pca = time.time()
    # calculate the covariance matrix
    cov_pca = np.cov(pca_reconstructed, rowvar=False)
    return end_pca - start_pca, cov_pca