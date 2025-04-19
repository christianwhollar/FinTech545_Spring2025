import pandas as pd
import numpy as np
from scipy.stats import norm
from numpy.linalg import cholesky
from scipy.optimize import minimize

from final_project.part_two import get_attribution_part_two
from final_project.part_four import get_best_distribution_for_assert, ppf_from_best

def es_risk_parity(corr_mat: pd.DataFrame, best_fit: dict, 
                   initial_weights=None, maxiter=10):
    """Calculate risk parity portfolio weights using Expected Shortfall (ES).

    Args:
        corr_mat (pd.DataFrame): Correlation matrix for asset returns.
        best_fit (dict): Dictionary of best-fit distribution parameters per asset.
        initial_weights (np.array, optional): Initial asset weights for optimization.
        maxiter (int, optional): Maximum number of iterations for optimization.

    Returns:
        pd.Series: Optimized risk parity weights for each asset.
    """
    assets = corr_mat.index.tolist()
    n = len(assets)
    
    # cholesky decomposition of correlation matrix
    L = cholesky(corr_mat.values)

    # equal weights if initial weights not provided
    if initial_weights is None:
        initial_weights = np.ones(n)/n

    # gen standard normal random variables and transform via correlation
    Z = np.random.randn(1, n)
    U = norm.cdf(Z @ L.T)

    def portfolio_es(weights):
        """zalculate the portfolio ES using fitted distributions."""
        X = np.column_stack([ppf_from_best(*best_fit[asset], U[:, i]) 
                             for i, asset in enumerate(assets)])
        losses = -X @ weights
        return np.mean(losses[losses >= np.percentile(losses, 95)])

    def objective(x):
        """Objective function to minimize differences in risk contributions."""
        x = x / x.sum()
        rc = []
        bump = 0.001
        base_es = portfolio_es(x)

        # calculate risk contribution of each asset
        for i in range(n):
            x_bumped = x.copy()
            x_bumped[i] += bump
            x_bumped /= x_bumped.sum()
            rc.append(x[i] * (portfolio_es(x_bumped) - base_es) / bump)

        rc = np.array(rc)
        return ((rc / rc.sum() - 1/n)**2).sum()

    # optimization to minimize risk contribution differences
    result = minimize(
        objective,
        initial_weights,
        method='SLSQP',
        bounds=[(0.01, 0.99)] * n,
        constraints={'type': 'eq', 'fun': lambda x: x.sum() - 1},
        options={'maxiter': maxiter}
    )

    weights = result.x / result.x.sum()
    return pd.Series(weights, index=assets)

def get_attribution_part_five(weights_tbl: pd.DataFrame, holding: pd.DataFrame,
                              sys_ret: pd.DataFrame, idio_ret: pd.DataFrame,
                              train: pd.DataFrame, coef_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate attribution using risk parity weights based on ES.

    Args:
        weights_tbl (pd.DataFrame): Original portfolio weights DataFrame.
        holding (pd.DataFrame): DataFrame containing returns during holding period.
        sys_ret (pd.DataFrame): DataFrame containing daily systematic returns.
        idio_ret (pd.DataFrame): DataFrame containing daily idiosyncratic returns.
        train (pd.DataFrame): DataFrame containing training period returns.
        coef_df (pd.DataFrame): DataFrame containing CAPM coefficients.

    Returns:
        pd.DataFrame: Portfolio attribution based on risk parity optimal weights.
    """
    # determine best-fit distributions for each asset from training data
    best_fit = get_best_distribution_for_assert(train, coef_df)

    # calculate risk parity weights for each individual portfolio
    risk_parity_weights = {}
    for port, group in weights_tbl.groupby('Portfolio'):
        assets = group['Symbol'].tolist()
        risk_parity_weights[port] = es_risk_parity(
            train[assets].corr(),
            {k: best_fit[k] for k in assets},
            initial_weights=group.set_index('Symbol')['weight'].values
        )

    # calculate risk parity weights for the combined portfolio
    all_assets = weights_tbl['Symbol'].unique()
    risk_parity_weights['TOTAL'] = es_risk_parity(
        train[all_assets].corr(),
        {k: best_fit[k] for k in all_assets}
    )

    # calculate portfolio attribution using the risk parity weights
    attrib_p3 = get_attribution_part_two(holding, risk_parity_weights, sys_ret, idio_ret)

    return attrib_p3
