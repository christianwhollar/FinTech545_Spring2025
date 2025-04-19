import pandas as pd
import statsmodels.api as sm

def load_data(
        prices_path: str = "DailyPrices.csv",
        rf_path: str = "rf.csv",
        port_path: str = "initial_portfolio.csv"
    ) -> tuple:
    """Loads the data from the specified CSV files.

    Args:
        prices_path (str, optional): Path to DailyPrices. Defaults to "DailyPrices.csv".
        rf_path (str, optional): Path to rf. Defaults to "rf.csv".
        port_path (str, optional): Path to initial_portfolio. Defaults to "initial_portfolio.csv".

    Returns:
        prices(pd.DataFrame): DataFrame containing daily prices.
        rf(pd.DataFrame): DataFrame containing risk-free rates.
        ports(pd.DataFrame): DataFrame containing portfolio weights.
    """
    prices = pd.read_csv(prices_path, parse_dates=['Date']).sort_values('Date')
    rf = pd.read_csv(rf_path, parse_dates=['Date']).sort_values('Date')
    ports = pd.read_csv(port_path)

    return prices, rf, ports

def calculate_daily_returns(prices: pd.DataFrame, rf: pd.DataFrame) -> pd.DataFrame:
    """Calculates daily returns, risk-free rates, and market excess returns.

    Args:
        prices (pd.DataFrame): DataFrame containing daily prices.
        rf (pd.DataFrame): DataFrame containing risk-free rates.

    Returns:
        pd.DataFrame: DataFrame containing daily returns, risk-free rates, and market excess returns.
    """
    ret = prices.set_index('Date').pct_change().dropna()
    ret['rf'] = rf.set_index('Date').reindex(ret.index)['rf']

    # calculate market excess as difference between SPY and risk-free rate
    ret['mkt_excess'] = ret['SPY'] - ret['rf']

    # drop rows with NaN values in rf and mkt_excess
    ret = ret.dropna(subset=['rf', 'mkt_excess'])
    return ret
    
def get_split_train_holding(ret: pd.DataFrame, d: pd.Timestamp = '2023-12-29') -> tuple:
    """Splits the data into regression training and holding DataFrames.

    Args:
        ret (pd.DataFrame): DataFrame containing daily returns.
        d (pd.Timestamp, optional): Date to split the data. Defaults to '2023-12-29'.

    Returns:
        tuple: Tuple containing training and holding DataFrames.
    """

    train = ret[ret.index < d]
    holding = ret[ret.index >= d]
    return train, holding

def get_capm_coefficients(ret: pd.DataFrame, train: pd.DataFrame) -> pd.DataFrame:
    """Calculate alpha, beta, and residual variance for each asset using CAPM.

    Args:
        ret (pd.DataFrame): DataFrame containing daily returns for each asset, market, and risk free.
        train (pd.DataFrame): DataFrame containing training data.

    Returns:
        tuple: DataFrame containing CAPM coefficients for each asset. 
    """
    coefs = {}

    for col in ret.columns:
        if col in ['rf', 'mkt_excess', 'SPY']:
            continue

        y = train[col] - train['rf']
        X = sm.add_constant(train['mkt_excess'])

        model = sm.OLS(y, X, missing='drop').fit()

        coefs[col] = {
            'alpha': model.params['const'],
            'beta': model.params['mkt_excess'],
            'resid_var': model.resid.var(),
        }

    return pd.DataFrame(coefs).T

def calculate_sys_idio_returns(holding: pd.DataFrame, coef_df: pd.DataFrame) -> tuple:
    """Calculates systematic and idiosyncratic returns for the holding period.

    Args:
        holding (pd.DataFrame): DataFrame containing returns during holding period.
        coef_df (pd.DataFrame): DataFrame containing CAPM coefficients.

    Returns:
        tuple: DataFrames containing daily systematic and idiosyncratic returns.
    """
    sys_ret = pd.DataFrame(index=holding.index)
    idio_ret = pd.DataFrame(index=holding.index)

    # iterate over each asset in the coef_df
    for col in coef_df.index:
        # extract alpha and beta from the coefficients DataFrame
        alpha = coef_df.loc[col, 'alpha']
        beta = coef_df.loc[col, 'beta']

        # calculate and store systematic and idiosyncratic returns
        sys_ret[col] = holding['mkt_excess'] * beta
        idio_ret[col] = holding[col] - sys_ret[col] - holding['rf'] + alpha

    return sys_ret, idio_ret

def calculate_cumulative_returns(holding: pd.DataFrame, sys_ret: pd.DataFrame, idio_ret: pd.DataFrame) -> pd.DataFrame:
    """Calculate cumulative returns for total, systematic, and idiosyncratic components.

    Args:
        holding (pd.DataFrame): Daily returns during holding period.
        sys_ret (pd.DataFrame): Daily systematic returns during holding period.
        idio_ret (pd.DataFrame): Daily idiosyncratic returns during holding period.

    Returns:
        pd.DataFrame: Cumulative returns for total, systematic, and idiosyncratic components.
    """
    cum_total = (holding.drop(columns=['rf','mkt_excess','SPY']) - holding['rf'].values[:,None] + 1).prod() - 1
    cum_sys   = (sys_ret + 1).prod() - 1
    cum_idio  = (idio_ret + 1).prod() - 1

    cumrets = pd.DataFrame({
        'total_excess': cum_total,
        'systematic':   cum_sys,
        'idiosyncratic':cum_idio
    })

    return cumrets

def calculate_portfolio_weights(ports: pd.DataFrame, prices: pd.DataFrame, d: pd.Timestamp = '2023-12-29') -> pd.DataFrame:
    """Calculate weight of each asset in the portfolio based on entry price.

    Args:
        ports (pd.DataFrame): Portfolio DataFrame.
        prices (pd.DataFrame): Daily Prices DataFrame.
        d (pd.Timestamp, optional): Date for entry price extraction. Defaults to '2023-12-29'.

    Returns:
        pd.DataFrame: DataFrame containing portfolio weights.
    """
    # extract entry prices
    entry_prices = prices.loc[prices['Date']==d].set_index('Date').iloc[0]

    # create columns for entry price and entry value
    ports['EntryPrice'] = entry_prices[ports['Symbol']].values
    ports['EntryValue'] = ports['Holding'] * ports['EntryPrice']

    # calculate weight for each asset as a fraction of the total entry value
    weights_tbl = (
        ports
        .groupby('Portfolio', group_keys=False)
        .apply(lambda df: df.assign(weight=df['EntryValue']/df['EntryValue'].sum()))
        .reset_index(drop=True)
    )

    return weights_tbl

def get_attribution_part_one(cumrets: pd.DataFrame, weights_tbl: pd.DataFrame) -> pd.DataFrame:
    """Calculate the attribution of returns for each portfolio.

    Args:
        cumrets (pd.DataFrame): DataFrame containing cumulative returns.
        weights_tbl (pd.DataFrame): DataFrame containing portfolio weights.

    Returns:
        pd.DataFrame: DataFrame containing attribution of returns for each portfolio.
    """
    def attrib(group):
        # extract weights
        w = group.set_index('Symbol')['weight']

        # multiply weights with cumulative returns
        # and sum them up for each component
        port_total = (w * cumrets.loc[w.index,'total_excess']).sum()
        port_sys   = (w * cumrets.loc[w.index,'systematic']).sum()
        port_idio  = (w * cumrets.loc[w.index,'idiosyncratic']).sum()
        return pd.Series({'Excess':port_total,'Systematic':port_sys,'Idiosyncratic':port_idio})

    # calculate attribution for each portfolio
    # and concatenate them into a single DataFrame
    attrib_p1 = pd.concat({p: attrib(g) for p,g in weights_tbl.groupby('Portfolio')}, axis=1).T
    attrib_p1.loc['TOTAL'] = attrib(weights_tbl)

    return attrib_p1