import pandas as pd
import numpy as np
from scipy.stats import norm
import scipy.optimize as optimize
import matplotlib.pyplot as plt

def problem_three():
    print("PROBLEM 3")
    print("\tPART A")
    problem_three_part_a()
    print("\tPART B")
    problem_three_part_b()
    print("\tPART C")
    problem_three_part_c()
    print("\tPART D")
    print("\t\tMethod 1")
    problem_three_part_d_method_one()
    print("\t\tMethod 2")
    problem_three_part_d_method_two()
    print("\tPART E")
    problem_three_part_e()

def problem_three_part_a():
    # get inputs and calculate implied vol using helper function
    S0, K, r, T, call_price, _ = get_inputs()
    implied_vol = implied_volatility(call_price, S0, K, r, T)
    print(f"\t\tImplied Volatility: {implied_vol:.2f}")

def problem_three_part_b():
    # get inputs and calculate greeks using helper functions
    S0, K, r, T, call_price, _ = get_inputs()
    implied_vol = implied_volatility(call_price, S0, K, r, T)

    delta = bsm_delta_call(S0, K, r, T, implied_vol)
    print(f"\t\tDelta: {delta:.2f}")
    vega = bsm_vega(S0, K, r, T, implied_vol)
    print(f"\t\tVega: {vega:.2f}")
    theta = bsm_theta_call(S0, K, r, T, implied_vol)
    print(f"\t\tTheta: {theta:.2f}")

    # proving vega, calculate the new price of the call option with a 1% increase in volatility
    new_vol = implied_vol + 0.01
    new_price = bsm_call(S0, K, r, T, new_vol)
    actual_change = new_price - call_price

    print(f"\t\tCalculated Price Change: {actual_change:.2f}")

def problem_three_part_c():
    # get inputs and calculate put price using helper functions
    S0, K, r, T, call_price, _ = get_inputs()
    put_price = bsm_put(S0, K, r, T, implied_volatility(call_price, S0, K, r, T))

    # put-call parity
    parity_lhs = call_price - put_price
    parity_rhs = S0 - K * np.exp(-r * T)
    print(f"\t\tPut-Call Parity LHS: ${parity_lhs:.4f}")
    print(f"\t\tPut-Call Parity RHS: ${parity_rhs:.4f}")
    print(f"\t\tDifference: ${abs(parity_lhs-parity_rhs):.6f}")
    print(f"\t\tPut-Call Parity holds: {abs(parity_lhs-parity_rhs) < 1e-4}")

def problem_three_part_d_method_one():
    # get ipnuts and calculate implied vol
    S0, K, r, T, call_price, _ = get_inputs()
    implied_vol = implied_volatility(call_price, S0, K, r, T)

    # problem inputs
    annual_vol = 0.25
    days_in_year = 255
    holding_period = 20
    alpha = 0.05

    # scale parameters to holding period
    scaling_factor = np.sqrt(holding_period / days_in_year)
    vol_period = annual_vol * scaling_factor

    # construct porfolio
    portfolio = {
        "call": 1,
        "put": 1,
        "stock": 1
    }

    print("\t\tDelta Normal Approximation")

    # calculate portfolio delta
    delta_call = bsm_delta_call(S0, K, r, T, implied_vol)
    delta_put = bsm_delta_put(S0, K, r, T, implied_vol)
    delta_portfolio = portfolio["call"] * delta_call + portfolio["put"] * delta_put + portfolio["stock"]
    print(f"\t\t\tPortfolio delta: {delta_portfolio:.4f}")

    # portfolio theta calculation
    theta_call = bsm_theta_call(S0, K, r, T, implied_vol)
    theta_put = bsm_theta_put(S0, K, r, T, implied_vol)
    theta_portfolio = portfolio["call"] * theta_call + portfolio["put"] * theta_put

    # portfolio vol
    portfolio_vol = abs(delta_portfolio) * S0 * vol_period

    # var/es delta calculation, similar to problem 2
    z_alpha = norm.ppf(alpha) 
    VaR_delta = -portfolio_vol * z_alpha
    ES_delta = portfolio_vol * norm.pdf(z_alpha) / alpha

    # time decay which was called out in problem statement
    time_decay = theta_portfolio * holding_period

    # adjust VaR and ES for time decay
    VaR_delta_adjusted = VaR_delta - time_decay
    ES_delta_adjusted  = ES_delta  - time_decay

    print(f"\t\t\tDelta Normal VaR (5%, 20 days): ${VaR_delta_adjusted:.4f}")
    print(f"\t\t\tDelta Normal ES (5%, 20 days): ${ES_delta_adjusted:.4f}")


def problem_three_part_d_method_two():
    # get option inputs and calculate implied vol
    S0, K, r, T, call_price, _ = get_inputs()
    implied_vol = implied_volatility(call_price, S0, K, r, T)

    # calculate put price
    put_price = bsm_put(S0, K, r, T, implied_vol)

    # problem inputs
    annual_vol = 0.25
    annual_return = 0
    days_in_year = 255
    holding_period = 20
    alpha = 0.05

    # remaining time 
    T_remaining = T - (holding_period / days_in_year)

    # portfolio value today
    portfolio_value = call_price + put_price + S0

    # Scale parameters to holding period
    scaling_factor = np.sqrt(holding_period / days_in_year)

    print("\t\tMonte Carlo Simulation")

    # MC parameters
    n_simulations = 10000
    np.random.seed(42)

    # random stock price paths
    Z = np.random.standard_normal(n_simulations)
    S_T = S0 * np.exp((annual_return - 0.5 * annual_vol**2) * (holding_period/days_in_year) + annual_vol * scaling_factor * Z)

    # calculate option values at the end of holding period
    call_values = np.array([bsm_call(s, K, r, T_remaining, implied_vol) for s in S_T])
    put_values = np.array([bsm_put(s, K, r, T_remaining, implied_vol) for s in S_T])

    # calculate portfolio values at the end of holding period
    portfolio_values = call_values + put_values + S_T

    # calculate P&L
    pnl = portfolio_values - portfolio_value

    # VaR and ES as a percentile of the P&L distribution
    VaR_MC = -np.percentile(pnl, alpha * 100)
    ES_MC = -np.mean(pnl[pnl <= -VaR_MC])

    print(f"\t\t\tMonte Carlo VaR (5%, 20 days): ${VaR_MC:.4f}")
    print(f"\t\t\tMonte Carlo ES (5%, 20 days): ${ES_MC:.4f}")

def problem_three_part_e():
    # get inputs and calculate implied vol and put price
    S0, K, r, T, call_price, _ = get_inputs()
    implied_vol = implied_volatility(call_price, S0, K, r, T)
    put_price = bsm_put(S0, K, r, T, implied_vol)

    # problem inputs
    days_in_year = 255
    holding_period = 20

    # remaining time
    T_remaining = T - (holding_period / days_in_year) 

    # simulated prices +/- 30% of current price
    stock_prices = np.linspace(S0 * 0.7, S0 * 1.3, 100)

    # store payoffs
    portfolio_payoffs = []

    # portfolio value today
    portfolio_value = call_price + put_price + S0

    # calculate portfolio payoffs at the end of holding period for each price
    for s in stock_prices:
        call_value = bsm_call(s, K, r, T_remaining, implied_vol)
        put_value = bsm_put(s, K, r, T_remaining, implied_vol)
        portfolio_payoffs.append(call_value + put_value + s)

    # create fig
    plt.figure(figsize=(10, 6))
    plt.plot(stock_prices, portfolio_payoffs)
    plt.axhline(y=portfolio_value, color='r', linestyle='--', label='Current portfolio value')
    plt.xlabel('Stock Price')
    plt.ylabel('Portfolio Value')
    plt.title('Portfolio Value vs. Stock Price at End of Holding Period')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('img/portfolio_payoff.png')

def get_inputs():
    S0 = 31        # Stock price
    K = 30         # Strike price
    r = 0.10       # Risk-free rate
    T = 0.25       # Time to maturity in years
    call_price = 3.00  # Market price of the call option
    dividend_yield = 0  # No dividends

    return S0, K, r, T, call_price, dividend_yield

# bsm for call
def bsm_call(S, K, r, T, sigma, q=0):
    d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call

# bsm for put
def bsm_put(S, K, r, T, sigma, q=0):
    d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    put = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
    return put

# bsm deltas
def bsm_delta_call(S, K, r, T, sigma, q=0):
    d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return np.exp(-q * T) * norm.cdf(d1)

def bsm_delta_put(S, K, r, T, sigma, q=0):
    d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return -np.exp(-q * T) * norm.cdf(-d1)

# bsm vega
def bsm_vega(S, K, r, T, sigma, q=0):
    d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T) / 100  # Divided by 100 for 1% change

# bsm thetas
def bsm_theta_call(S, K, r, T, sigma, q=0):
    d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    theta = -S * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2) + q * S * np.exp(-q * T) * norm.cdf(d1)
    return theta / 365  # Daily theta

def bsm_theta_put(S, K, r, T, sigma, q=0):
    d1 = (np.log(S/K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    theta = -S * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2) - q * S * np.exp(-q * T) * norm.cdf(-d1)
    return theta / 365  # Daily theta

def implied_volatility(price, S, K, r, T, option_type='call'):
    # define fxn based on call/put status
    def objective(sigma):
        if option_type == 'call':
            return bsm_call(S, K, r, T, sigma) - price
        else:
            return bsm_put(S, K, r, T, sigma) - price
    
    # guess
    sigma_initial = 0.2
    
    # solving methodology - I pulled this from AI
    implied_vol = optimize.newton(objective, sigma_initial)
    return implied_vol

if __name__ == "__main__":
    problem_three()