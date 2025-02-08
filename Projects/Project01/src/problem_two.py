import pandas as pd
import numpy as np

def problem_two():
    df = pd.read_csv("problem2.csv")

    # Part A
    mat = calculate_pairwise_covariance_matrix(df)

    # Part B
    is_psd = is_positive_semi_definite(mat)

    # Part C
    # Rebenato-Jackal method
    rj_mat = near_psd_rebenato_jackal(mat)
    # Higham method
    higham_mat = higham_method(mat)

    # Part D
    overlap_mat = calculate_covariance_matrix_with_overlapping_data(df)

    print("PROBLEM TWO:")
    
    print("\tPart A:")
    print("\t\tPairwise Covariance Matrix:")
    print("\t\t", str(mat).replace('\n', '\n\t\t'))

    print("\tPart B:")
    print(f"\t\t{is_psd}")

    print("\tPart C:")
    print("\t\tRebenato-Jackal Method:")
    print("\t\t", str(rj_mat).replace('\n', '\n\t\t'))
    print("\t\tHigham Method:")
    print("\t\t", str(higham_mat).replace('\n', '\n\t\t'))

    print("\tPart D:")
    print("\t\tCovariance Matrix with Overlapping Data:")
    print("\t\t", str(overlap_mat).replace('\n', '\n\t\t'))

def calculate_pairwise_covariance_matrix(df: pd.DataFrame) -> np.ndarray:
    cols = df.columns
    m = len(cols)

    # generate a matrix to store the covariance values
    mat = np.zeros((m, m))

    # iterate over all pairs of columns
    for i in range(m):
        for j in range(m):

            # get the values of the columns
            xi = df[cols[i]].values
            xj = df[cols[j]].values

            # mask out the NaN values
            mask = ~np.isnan(xi) & ~np.isnan(xj)

            # apply the mask
            xi = xi[mask]
            xj = xj[mask]

            # calculate the covariance, update the matrix
            mat[i, j] = np.cov(xi, xj)[0, 1]
            mat[j, i] = mat[i, j]
    
    return mat

def is_positive_semi_definite(mat: np.ndarray) -> bool:

    # 1. generate eigen values for input matrix
    # 2. check if all eigen values are greater than or equal to 0

    return np.all(np.linalg.eigvals(mat) >= 0)

def near_psd_rebenato_jackal(mat, epsilon=0) -> np.ndarray:
    # get the eigen values and vectors
    vals, vecs = np.linalg.eigh(mat)

    # set the negative eigen values to 0
    vals = np.maximum(vals, epsilon)

    # reconstruct the matrix
    return vecs @ np.diag(vals) @ vecs.T

def higham_method(A, maximum_iterations=100, tol=1e-7):

    # this is taken from lecture notes

    # initialize the variables
    Y_k_1 = A.copy()
    n = A.shape[0]
    delta_S_k_1 = 0

    for k in range(maximum_iterations):
        # set r_k to the current matrix minus the delta
        R_k = Y_k_1 - delta_S_k_1

        # get the eigen values and vectors
        vals, vecs = np.linalg.eigh(R_k)

        # set the negative eigen values to 0, reconstruct matrix
        X_k = (vecs @ np.diag(np.maximum(vals, 0)) @ vecs.T)

        # calculate the difference and delta S
        delta_S = X_k - R_k

        # set Y_k to the new matrix
        Y_k = X_k

        # calculate the frobenius norm
        diffFrob = np.linalg.norm(Y_k - Y_k_1, 'fro')

        # update the variables
        Y_k_1 = Y_k
        delta_S_k_1 = delta_S

        # check if the difference is less than the tolerance
        if diffFrob < tol:
            break
    
    return Y_k

def calculate_covariance_matrix_with_overlapping_data(df: pd.DataFrame) -> np.ndarray:
    # drop the rows with NaN values
    df_overlap = df.dropna(axis=0, how="any")
    # call part A function
    return calculate_pairwise_covariance_matrix(df_overlap)