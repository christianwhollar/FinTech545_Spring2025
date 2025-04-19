import pandas as pd

def attrib_series(w: pd.Series, holding: pd.DataFrame, sys_ret: pd.DataFrame, idio_ret: pd.DataFrame) -> pd.DataFrame:
    # calulate the attribution for each portfolio
    # calculate each as a product of the weights and the returns
    # accounting for the risk-free rate
    tot  = (holding[w.index].sub(holding['rf'],axis=0).mul(w,axis=1).sum(axis=1)+1).prod()-1
    sys  = (sys_ret[w.index].mul(w,axis=1).sum(axis=1)+1).prod()-1
    idio = (idio_ret[w.index].mul(w,axis=1).sum(axis=1)+1).prod()-1
    return pd.Series({'Excess':tot,'Systematic':sys,'Idio':idio})