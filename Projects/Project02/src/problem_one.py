import pandas as pd
import numpy as np

def problem_one(df: pd.DataFrame):
    print("PROBLEM 1")
    prices = df.drop(columns=['Date'])

    print("\tPART A")
    problem_one_part_a(prices)

    print("\tPART B")
    problem_one_part_b(prices)

def problem_one_part_a(prices: pd.DataFrame):
    '''
    Calculate the Arithmetic Returns. Remove the mean, such that each series has 0 mean. Present the last 5 rows and the total standard deviation.
    Args:
        prices (pd.DataFrame): stock prices
    '''
    # calculate log returns and drop na values
    arithmetic_returns = prices.pct_change().dropna()

    # calculate mean for each stock
    arithmetic_returns_mean = arithmetic_returns.mean(axis=0)

    # subtract mean from each column for each stock
    arithmetic_returns_zero_mean = arithmetic_returns.sub(arithmetic_returns_mean, axis=1)

    print(f"\t\t{arithmetic_returns_zero_mean.tail(5)}")

    # calculate standard deviation of all cells
    total_standard_deviation_arith = arithmetic_returns_zero_mean.stack().std()

    print(f"\t\tArithmetic Total Standard Deviation: {total_standard_deviation_arith}")

def problem_one_part_b(prices: pd.DataFrame):
    '''
    Calculate the Log Returns. Remove the mean, such that each series has 0 mean. Present the last 5 rows and the total standard deviation.
    Args:
        prices (pd.DataFrame): stock prices
    '''
    # calculate log returns and drop na values
    log_returns = np.log(prices).diff()
    log_returns.dropna(inplace=True)

    # calculate mean for each stock
    log_returns_mean = log_returns.mean(axis=0)

    # subtract mean from each column for each stock
    log_returns_zero_mean = log_returns.sub(log_returns_mean, axis=1)

    print(f"\t\t{log_returns_zero_mean.tail(5)}")

    # calculate standard deviation of all cells
    total_standard_deviation_log = log_returns_zero_mean.stack().std()

    print(f"\t\tLogarithmic Total Standard Deviation: {total_standard_deviation_log}")

if __name__ == "__main__":
    df = pd.read_csv("./DailyPrices.csv")
    problem_one(df)