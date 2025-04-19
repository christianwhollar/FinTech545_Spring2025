from final_project.part_one import load_data, calculate_daily_returns, get_split_train_holding, get_capm_coefficients, calculate_sys_idio_returns, calculate_cumulative_returns, calculate_portfolio_weights, get_attribution_part_one
from final_project.part_two import get_expected_return, get_cov_matrix, get_optimal_sharpe_ratio_weights, get_attribution_part_two, print_idio_risk
from final_project.part_four import get_var_es_normal_copula, print_best_fit
from final_project.part_five import get_attribution_part_five

def part_one():
    prices, rf, ports = load_data()
    ret = calculate_daily_returns(prices, rf)
    train, holding = get_split_train_holding(ret)
    coef_df = get_capm_coefficients(ret, train)
    sys_ret, idio_ret = calculate_sys_idio_returns(holding, coef_df)
    cumrets = calculate_cumulative_returns(holding, sys_ret, idio_ret)
    weights_tbl = calculate_portfolio_weights(ports, prices)
    attrib_p1 = get_attribution_part_one(cumrets, weights_tbl)

    print("PART ONE")
    print(f"{attrib_p1}")

def part_two():
    # part one repeats
    prices, rf, ports = load_data()
    ret = calculate_daily_returns(prices, rf)
    train, holding = get_split_train_holding(ret)
    coef_df = get_capm_coefficients(ret, train)
    sys_ret, idio_ret = calculate_sys_idio_returns(holding, coef_df)

    # part two specific function calls
    mu_exp = get_expected_return(train, coef_df)
    Sigma = get_cov_matrix(train, coef_df)
    op_weights = get_optimal_sharpe_ratio_weights(Sigma, mu_exp, ports)
    attrib_p2 = get_attribution_part_two(holding, op_weights, sys_ret, idio_ret)

    print("PART TWO")
    print(f"{attrib_p2}")
    print_idio_risk(coef_df, idio_ret)
    
def part_four():
    # part one repeats
    prices, rf, ports = load_data()
    ret = calculate_daily_returns(prices, rf)
    train, _ = get_split_train_holding(ret)
    coef_df = get_capm_coefficients(ret, train)
    weights_tbl = calculate_portfolio_weights(ports, prices)

    # part four specific function calls
    var_es_normal, var_es_copula = get_var_es_normal_copula(train, coef_df, weights_tbl)

    print("PART FOUR")
    for tag, dat in [('MV Normal', var_es_normal), ('Gaussian Copula', var_es_copula)]:
            print(tag)
            for k,v in dat.items():
                print(f' {k:>6}: VaR {v[0]:.4%} | ES {v[1]:.4%}')

    print_best_fit(train, coef_df)

def part_five():
    # part one repeats
    prices, rf, ports = load_data()
    ret = calculate_daily_returns(prices, rf)
    train, holding = get_split_train_holding(ret)
    coef_df = get_capm_coefficients(ret, train)
    sys_ret, idio_ret = calculate_sys_idio_returns(holding, coef_df)
    weights_tbl = calculate_portfolio_weights(ports, prices)

    # part five specific function calls
    attrib_p3 = get_attribution_part_five(weights_tbl, holding, sys_ret, idio_ret, train, coef_df)

    print("PART FIVE")
    print(f"{attrib_p3}")

if __name__ == "__main__":
    part_one()
    part_two()
    part_four()
    part_five()