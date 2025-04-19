import pandas as pd
import numpy as np
from scipy.stats import norm, t, skewnorm, norminvgauss
from numpy.linalg import cholesky

ALPHA_CI = 0.95
SIM_N    = 5000 

def get_best_distribution_for_assert(train: pd.DataFrame, coef_df: pd.DataFrame) -> dict:
    """Get the best distribution for each asset.

    Args:
        train (pd.DataFrame): DataFrame containing daily returns during training period.
        coef_df (pd.DataFrame): DataFrame containing CAPM coefficients.

    Returns:
        dict: Dictionary containing the best distribution and its parameters for each asset.
    """

    def fit_best(x):
        # force mean 0
        x = x - x.mean()

        # create a dictionary to store the log-likelihood values and parameters for each distribution
        ll = {}
        params = {}

        # normal distribution
        loc,scale = norm.fit(x)
        ll['Normal'] = norm.logpdf(x, loc, scale).sum()
        params['Normal'] = (loc,scale)

        # student t
        df,loc,scale = t.fit(x, floc=0)  # enforce loc 0
        ll['T'] = t.logpdf(x, df, loc, scale).sum()
        params['T'] = (df,loc,scale)

        # skew normal
        a,loc,scale = skewnorm.fit(x, floc=0)
        ll['SkewNorm'] = skewnorm.logpdf(x, a, loc, scale).sum()
        params['SkewNorm'] = (a,loc,scale)

        # normal inverse gaussian
        try:
            a,b,loc,scale = norminvgauss.fit(x, floc=0)
            ll['NIG'] = norminvgauss.logpdf(x, a,b, loc, scale).sum()
            params['NIG'] = (a,b,loc,scale)
        except Exception:
            ll['NIG'] = -np.inf
            params['NIG'] = ()

        # calculate AIC for each distribution
        # AIC = -2*log-likelihood + 2*number of parameters
        aic = {k: -2*llv + 2*len(params[k]) for k,llv in ll.items()}

        # extract the distribution with the lowest AIC
        # and return the name and parameters
        best = min(aic, key=aic.get)
        return best, params[best]

    best_fit = {sym: fit_best(train[sym] - train['rf']) for sym in coef_df.index}

    return best_fit

def sample_rvs(name,param,size) -> np.ndarray:
    """Sample random variables from the specified distribution.

    Args:
        name (_type_): Name of the distribution to sample from.
        param (_type_): Parameters for the distribution.
        size (_type_): Number of samples to generate.

    Returns:
        _type_: Array of sampled random variables.
    """
    if name=='Normal':
        return norm.rvs(*param,size=size)
    if name=='T':
        return t.rvs(*param,size=size)
    if name=='SkewNorm':
        return skewnorm.rvs(*param,size=size)
    if name=='NIG':
        return norminvgauss.rvs(*param,size=size)

def ppf_from_best(name, param, u):
    """Calculate the percent point function (PPF) for the specified distribution.

    Args:
        name (_type_): Name of the distribution.
        param (_type_): Parameters for the distribution.
        u (_type_): Quantile level.

    Returns:
        _type_: PPF value for the specified distribution.
    """
    if name == 'Normal':
        loc, scale = param
        return norm.ppf(u, loc, scale)
    if name == 'T':
        df, loc, scale = param
        return t.ppf(u, df, loc, scale)
    if name == 'SkewNorm':
        a, loc, scale = param
        return skewnorm.ppf(u, a, loc, scale)
    if name == 'NIG':
        a, b, loc, scale = param
        return norminvgauss.ppf(u, a, b, loc, scale)

def var_es(weights, train: pd.DataFrame, corr_mat: pd.DataFrame, best_fit: dict, copula=True, sims=SIM_N, confidence=ALPHA_CI):
    """Calculate Value at Risk (VaR) and Expected Shortfall (ES) for a portfolio.

    Args:
        weights (_type_): Portfolio weights.
        corr_mat (pd.DataFrame): Correlation matrix.
        best_fit (dict): Best fit distribution parameters for each asset.
        copula (bool, optional): _description_. Defaults to True. Copula method.
        sims (_type_, optional): _description_. Defaults to SIM_N. Number of simulations.
        confidence (_type_, optional): _description_. Defaults to ALPHA_CI. Confidence level.

    Returns:
        _type_: _description_
    """
    w = weights.values
    idx = weights.index

    # if type is gaussian cop
    if copula:
        L = cholesky(corr_mat.loc[idx,idx].values)
        Z = np.random.randn(sims,len(idx)) @ L.T
        U = norm.cdf(Z)
        if copula:
            L = cholesky(corr_mat.loc[idx, idx].values)
            Z = np.random.randn(sims, len(idx)) @ L.T
            U = norm.cdf(Z)
            X = np.column_stack([
                ppf_from_best(*best_fit[sym], U[:, i])
                for i, sym in enumerate(idx)
            ])

    # else run multivariate normal
    else:
        X = np.random.multivariate_normal(np.zeros(len(idx)),
                                          train[idx].cov().values,
                                          size=sims)
    port = X @ w
    var = -np.percentile(port, (1-confidence)*100)
    es  = -port[port <= -var].mean()
    return var, es

def get_var_es_normal_copula(train: pd.DataFrame, coef_df: pd.DataFrame, weights_tbl: pd.DataFrame) -> tuple:
    """Calculate Value at Risk (VaR) and Expected Shortfall (ES) for normal and copula methods for each portfolio.

    Args:
        train (pd.DataFrame): DataFrame containing daily returns during training period.
        coef_df (pd.DataFrame): DataFrame containing CAPM coefficients.
        weights_tbl (pd.DataFrame): DataFrame containing portfolio weights.

    Returns:
        tuple: Tuple containing two dictionaries:
            - var_es_normal: Dictionary containing VaR and ES for normal method.
            - var_es_copula: Dictionary containing VaR and ES for copula method.
    """
    best_fit = get_best_distribution_for_assert(train, coef_df)
    corr_mat = train[coef_df.index].corr()
    var_es_normal = {}
    var_es_copula = {}
    for p,g in weights_tbl.groupby('Portfolio'):
        w0 = g.set_index('Symbol')['weight']
        var_es_normal[p] = var_es(w0, train, corr_mat, best_fit, copula=False)
        var_es_copula[p] = var_es(w0, train, corr_mat, best_fit, copula=True)
    w_total = weights_tbl.set_index('Symbol')['weight']
    var_es_normal['TOTAL'] = var_es(w_total, train, corr_mat, best_fit, copula=False)
    var_es_copula['TOTAL'] = var_es(w_total, train, corr_mat, best_fit, copula=True)

    return var_es_normal, var_es_copula

def print_best_fit(train: pd.DataFrame, coef_df: pd.DataFrame):
    best_fit = get_best_distribution_for_assert(train, coef_df)
    best_fit_df = pd.DataFrame(best_fit, index=['model','params']).T

    print("Best Fit Per Stock:")
    for sym, row in best_fit_df.iterrows():
        print(f"{sym}: {row['model']}, {row['params']}")