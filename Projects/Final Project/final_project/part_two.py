import pandas as pd
import numpy as np
from numpy.linalg import inv
from final_project.utils import attrib_series

def get_expected_return(train: pd.DataFrame, coef_df: pd.DataFrame) -> pd.Series:
    """Calculate expected return for each asset based on CAPM. Alpha is assumed to be 0.

    Args:
        train (pd.DataFrame): DataFrame containing training data.
        coef_df (pd.DataFrame): DataFrame containing CAPM coefficients.

    Returns:
        pd.Series: _description_
    """
    mu_mkt = train['mkt_excess'].mean()
    mu_exp = coef_df['beta'] * mu_mkt
    return mu_exp

def get_cov_matrix(train: pd.DataFrame, coef_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate covariance matrix for assets based on CAPM.

    Args:
        train (pd.DataFrame): DataFrame containing training data.
        coef_df (pd.DataFrame): DataFrame containing CAPM coefficients.

    Returns:
        pd.DataFrame: Covariance matrix for assets.
    """
    # estimate market variance
    sigma2_mkt = train['mkt_excess'].var()

    # estimate systematic covariance as beta_i * beta_j * sigma2_mkt
    # and idiosyncratic covariance as resid_var_i * resid_var_j
    # then combine them into a covariance matrix
    Sigma = np.outer(coef_df['beta'], coef_df['beta']) * sigma2_mkt + np.diag(coef_df['resid_var'])
    
    # reformat as a DataFrame and set the index and columns to the asset names
    Sigma = pd.DataFrame(Sigma, index=coef_df.index, columns=coef_df.index)
    return Sigma

def get_optimal_sharpe_ratio_weights(Sigma: pd.DataFrame, mu_exp: pd.Series, ports: pd.DataFrame) -> dict:
    """Calculate the optimal weights for each portfolio based on the Sharpe ratio.

    Args:
        Sigma (pd.DataFrame): Covariance matrix of asset returns.
        mu_exp (pd.Series): Expected returns of assets.
        ports (pd.DataFrame): Portfolio DataFrame.
    Returns:
        dict: Dictionary containing optimal weights for each portfolio.
    """
    def optimal_sharpe_ratio_weights(asset_list):
        # subset of the covariance matrix containing only the assets in the portfolio
        Sigma_sub = Sigma.loc[asset_list, asset_list].values
        # subset of the expected returns containing only the assets in the portfolio
        mu_sub    = mu_exp.loc[asset_list].values
        # calculate the weights using the formula w = inv(Sigma) @ mu
        w_raw = inv(Sigma_sub) @ mu_sub
        # normalize the weights to sum to 1 and return as a Series
        return pd.Series(w_raw / w_raw.sum(), index=asset_list)

    # calculate the optimal weights for each portfolio
    op_weights = {p: optimal_sharpe_ratio_weights(g['Symbol'].tolist()) for p,g in ports.groupby('Portfolio')}
    return op_weights

def get_attribution_part_two(holding: pd.DataFrame, op_weights: dict, sys_ret: pd.DataFrame, idio_ret: pd.DataFrame) -> pd.DataFrame:
    """Get the attribution for each portfolio based on the optimal weights.

    Args:
        holding (pd.DataFrame): DataFrame containing daily returns during holding period.
        op_weights (dict): Dictionary containing optimal weights for each portfolio.
        sys_ret (pd.DataFrame): DataFrame containing daily systematic returns during holding period.
        idio_ret (pd.DataFrame): DataFrame containing daily idiosyncratic returns during holding period.
    Returns:
        pd.DataFrame: DataFrame containing attribution for each portfolio.
    """
    attrib_p2 = pd.concat({p: attrib_series(w, holding, sys_ret, idio_ret) for p,w in op_weights.items()}, axis=1).T
    total_weights = pd.concat(op_weights).groupby(level=1).mean()
    attrib_p2.loc['TOTAL'] = attrib_series(total_weights, holding, sys_ret, idio_ret)
    return attrib_p2

def print_idio_risk(coef_df: pd.DataFrame, idio_ret: pd.Series) -> None:
    expected_sd = np.sqrt(coef_df['resid_var']) * np.sqrt(252)
    realised_sd = idio_ret.std() * np.sqrt(252)
    print(pd.DataFrame({'Expected Idio Risk':expected_sd, 'Realised Idio Risk':realised_sd}).describe().round(2))
