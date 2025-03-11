import pandas as pd
import numpy as np
from scipy import stats

def problem_two(df: pd.DataFrame):
    alpha = 0.05

    print("PROBLEM 2")

    print("\tPART A")
    problem_two_part_a(df)

    print("\tPart B")
    print("\t\tNormally distributed with exponentially weighted covariance with lambda=0.97")
    problem_two_part_b_method_one(df, alpha)
    
    print("\t\tT distribution using a Gaussian Copula")
    problem_two_part_b_method_two(df, alpha)

    print("\t\tHistorical simulation using the full history")
    problem_two_part_b_method_three(df, alpha)

def problem_two_part_a(df: pd.DataFrame):
    '''
    Calculate the current value of the portfolio given today is 1/3/2025'
    '''
    # get prices and shares
    SPY_price, AAPL_price, EQIX_price, SPY_shares, AAPL_shares, EQIX_shares = get_prices_and_shares(df)

    # calculate portfolio value
    portfolio_value = SPY_shares * SPY_price + AAPL_shares * AAPL_price + EQIX_shares * EQIX_price

    print(f"\t\tPortfolio Value: ${portfolio_value:.2f}")

def problem_two_part_b_method_one(df: pd.DataFrame, alpha: float):
    '''
    Normally distributed with exponentially weighted covariance with lambda=0.97
    '''
    # helper functions
    SPY_price, AAPL_price, EQIX_price, SPY_shares, AAPL_shares, EQIX_shares = get_prices_and_shares(df)
    weights_portfolio = get_weight_portfolio(df)
    portfolio_value = get_portfolio_value(df)

    returns = get_returns(df)
    lambda_ = 0.97

    # initialize weights
    weights = np.zeros(len(returns))

    # calculate weights
    for i in range(len(returns)):
        weights[i] = (1 - lambda_) * lambda_ ** i

    # normalize the weights
    weights = weights / np.sum(weights)

    # calculate the exponentially weighted moving average
    ewma_cov = np.zeros((3, 3))
    for i in range(len(returns)):
        r = returns.iloc[len(returns) - 1 - i].values.reshape(-1, 1)
        ewma_cov += weights[i] * np.dot(r, r.T)

    # calculate portfolio volatility
    port_vol = np.sqrt(np.dot(weights_portfolio.T, np.dot(ewma_cov, weights_portfolio)))

    # calculate stock volatilites and values
    stock_vols = np.sqrt(np.diag(ewma_cov))
    stock_values = np.array([SPY_shares * SPY_price, AAPL_shares * AAPL_price, EQIX_shares * EQIX_price])

    # VaR calculation (normal distribution)
    z_score = stats.norm.ppf(alpha)
    stock_var = -z_score * stock_vols * stock_values
    port_var = -z_score * port_vol * portfolio_value

    # ES calculation (normal distribution)
    es_factor = stats.norm.pdf(z_score) / alpha
    stock_es = stock_var * es_factor
    port_es = port_var * es_factor

    # normal distribution results
    print(f"\t\t\tSPY VaR: ${stock_var[0]:.2f}, ES: ${stock_es[0]:.2f}")
    print(f"\t\t\tAAPL VaR: ${stock_var[1]:.2f}, ES: ${stock_es[1]:.2f}")
    print(f"\t\t\tEQIX VaR: ${stock_var[2]:.2f}, ES: ${stock_es[2]:.2f}")
    print(f"\t\t\tPortfolio VaR: ${port_var:.2f}, ES: ${port_es:.2f}")

def problem_two_part_b_method_two(df: pd.DataFrame, alpha: float):
    '''
    T distribution using a Gaussian Copula
    '''
    returns = get_returns(df)

    weights_port = get_weight_portfolio(df)

    portfolio_value = get_portfolio_value(df)

    stock_values = get_stock_values(df)

    # fitting the copula...

    # get t distribution parameters
    t_params = []
    for col in returns.columns:
        params = stats.t.fit(returns[col])
        t_params.append(params)

    normal_returns = returns.copy()
    for i, col in enumerate(returns.columns):
        # get t distribution parameters
        df, loc, scale = t_params[i]

        # transform observation to uniform
        u = stats.t.cdf(returns[col], df, loc, scale)

        # normal quantile function
        normal_returns[col] = stats.norm.ppf(u)

    # calculate correlation matrix
    corr_matrix = normal_returns.corr().values

    n_sim = 10000
    np.random.seed(42)

    # simulation n_sims from the multivariate normal
    sim_normal = np.random.multivariate_normal(np.zeros(3), corr_matrix, n_sim)

    # for each var Z_i
    sim_returns = np.zeros((n_sim, 3))
    for i in range(3):
        # get t distribution parameters
        df, loc, scale = t_params[i]

        # transform observation to uniform
        u = stats.norm.cdf(sim_normal[:, i])

        # normal quantile function
        sim_returns[:, i] = stats.t.ppf(u, df, loc, scale)

    sim_port_returns = np.dot(sim_returns, weights_port)

    # calculate the VaR and ES (percentile of simulated returns)
    stock_var_t = -np.percentile(sim_returns, alpha * 100, axis=0) * stock_values
    port_var_t = -np.percentile(sim_port_returns, alpha * 100) * portfolio_value

    # create np array to store expected shortfall values
    stock_es_t = np.zeros(3)
    for i in range(3):
        threshold = -stock_var_t[i] / stock_values[i]
        stock_es_t[i] = -np.mean(sim_returns[:, i][sim_returns[:, i] <= threshold]) * stock_values[i]

    port_threshold = -port_var_t / portfolio_value
    port_es_t = -np.mean(sim_port_returns[sim_port_returns <= port_threshold]) * portfolio_value

    # print results for method two
    print(f"\t\t\tSPY VaR: ${stock_var_t[0]:.2f}, ES: ${stock_es_t[0]:.2f}")
    print(f"\t\t\tAAPL VaR: ${stock_var_t[1]:.2f}, ES: ${stock_es_t[1]:.2f}")
    print(f"\t\t\tEQIX VaR: ${stock_var_t[2]:.2f}, ES: ${stock_es_t[2]:.2f}")
    print(f"\t\t\tPortfolio VaR: ${port_var_t:.2f}, ES: ${port_es_t:.2f}")

def problem_two_part_b_method_three(df: pd.DataFrame, alpha: float):
    '''
    Historic simulation using the full history
    '''

    # helper functions
    returns = get_returns(df)
    weight_portfolio = get_weight_portfolio(df)
    portfolio_value = get_portfolio_value(df)
    stock_values = get_stock_values(df)

    # calculate portfolio returns
    hist_port_returns = np.dot(returns.values, weight_portfolio)

    # VaR calculation - percentile on the profit and loss distribution
    stock_var_hist = -np.percentile(returns.values, alpha * 100, axis=0) * stock_values
    port_var_hist = -np.percentile(hist_port_returns, alpha * 100) * portfolio_value

    # ES calculation - mean of all values less than or equal to the VaR
    stock_es_hist = np.zeros(3)
    for i in range(3):
        # calculate threshold as the ratio of the VaR to the stock value
        threshold = -stock_var_hist[i] / stock_values[i]
        stock_es_hist[i] = -np.mean(returns.values[:, i][returns.values[:, i] <= threshold]) * stock_values[i]

    # calculate portfolio ES
    port_threshold = -port_var_hist / portfolio_value
    port_es_hist = -np.mean(hist_port_returns[hist_port_returns <= port_threshold]) * portfolio_value

    # print results from method 3
    print(f"\t\t\tSPY VaR: ${stock_var_hist[0]:.2f}, ES: ${stock_es_hist[0]:.2f}")
    print(f"\t\t\tAAPL VaR: ${stock_var_hist[1]:.2f}, ES: ${stock_es_hist[1]:.2f}")
    print(f"\t\t\tEQIX VaR: ${stock_var_hist[2]:.2f}, ES: ${stock_es_hist[2]:.2f}")
    print(f"\t\t\tPortfolio VaR: ${port_var_hist:.2f}, ES: ${port_es_hist:.2f}")

def get_prices_and_shares(df: pd.DataFrame):
    # calculate prices
    SPY_price = df[df.Date == "2025-01-03"]["SPY"].values[0]
    AAPL_price = df[df.Date == "2025-01-03"]["AAPL"].values[0]
    EQIX_price = df[df.Date == "2025-01-03"]["EQIX"].values[0]

    # store share info
    SPY_shares = 100
    AAPL_shares = 200
    EQIX_shares = 150

    return SPY_price, AAPL_price, EQIX_price, SPY_shares, AAPL_shares, EQIX_shares

def get_returns(df: pd.DataFrame):
    # calculate returns
    returns = df[["SPY", "AAPL", "EQIX"]].pct_change().dropna()

    # zero the mean
    returns = returns - returns.mean()

    return returns

def get_weight_portfolio(df: pd.DataFrame):
    # get prices and shares
    SPY_price, AAPL_price, EQIX_price, SPY_shares, AAPL_shares, EQIX_shares = get_prices_and_shares(df)

    # calculate portfolio value
    portfolio_value = SPY_shares * SPY_price + AAPL_shares * AAPL_price + EQIX_shares * EQIX_price

    # calculate weights
    weights_port = np.array([
        SPY_shares * SPY_price / portfolio_value,
        AAPL_shares * AAPL_price / portfolio_value,
        EQIX_shares * EQIX_price / portfolio_value
    ])

    return weights_port

def get_portfolio_value(df: pd.DataFrame):
    # get prices and shares
    SPY_price, AAPL_price, EQIX_price, SPY_shares, AAPL_shares, EQIX_shares = get_prices_and_shares(df)

    # calculate portfolio value
    portfolio_value = SPY_shares * SPY_price + AAPL_shares * AAPL_price + EQIX_shares * EQIX_price

    return portfolio_value

def get_stock_values(df: pd.DataFrame):
    # get prices and shares
    SPY_price, AAPL_price, EQIX_price, SPY_shares, AAPL_shares, EQIX_shares = get_prices_and_shares(df)

    # calculate stock values
    stock_values = np.array([SPY_shares * SPY_price, AAPL_shares * AAPL_price, EQIX_shares * EQIX_price])

    return stock_values

if __name__ == "__main__":
    df = pd.read_csv("./DailyPrices.csv")
    problem_two(df)