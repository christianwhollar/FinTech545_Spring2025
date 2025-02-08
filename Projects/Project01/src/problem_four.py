import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_process import ArmaProcess
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA

def problem_four():
    df = pd.read_csv("problem4.csv")
    y = df["y"].values

    # Part A
    simulate_process([], [0.5], "MA(1)")
    simulate_process([], [0.5, 0.3], "MA(2)")
    simulate_process([], [0.5, 0.3, 0.2], "MA(3)")

    # Part B
    simulate_process([0.5], [], "AR(1)")
    simulate_process([0.5, 0.3], [], "AR(2)")
    simulate_process([0.5, 0.3, 0.2], [], "AR(3)")

    # Part C
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(y, ax=axes[0], lags=20)
    plot_pacf(y, ax=axes[1], lags=20)
    axes[0].set_title("ACF of Actual Data")
    axes[1].set_title("PACF of Actual Data")
    # plt.show()
    fig.savefig("img/actual_data.png")

    # Part D
    # AR(1), AR(2), AR(3) => (p,0,0)
    # MA(1), MA(2), MA(3) => (0,0,q)
    orders = [(1, 0, 0), (2, 0, 0), (3, 0, 0),
                        (0, 0, 1), (0, 0, 2), (0, 0, 3)]
    
    results = {}
    n = len(y)

    for order in orders:
        # Fit ARIMA with the given (p,d,q)
        model = ARIMA(y, order=order)
        fitted_model = model.fit()

        # calculate the number of parameters
        k = len(fitted_model.params)

        # calculate AIC and AICc
        aic_value = fitted_model.aic
        aicc_value = calculate_aicc(aic_value, k, n)
        results[order] = (aic_value, aicc_value)

    best_order = min(results, key=lambda x: results[x][1])
    best_aic, best_aicc = results[best_order]

    print("PROBLEM FOUR:")
    print("\tPart D:")
    for ord_, (aic_val, aicc_val) in results.items():
        print(f"\t\t{ord_} => (AIC={aic_val:.3f}, AICc={aicc_val:.3f})")

def simulate_process(ar_params, ma_params, title):
    # define the AR and MA parameters
    ar = np.r_[1, -np.array(ar_params)]
    ma = np.r_[1, np.array(ma_params)]

    # simulate the ARMA process
    arma_process = ArmaProcess(ar, ma)
    simulated_data = arma_process.generate_sample(nsample=200)

    # plot ACF and PACF
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(simulated_data, ax=axes[0], lags=20)
    plot_pacf(simulated_data, ax=axes[1], lags=20)
    axes[0].set_title(f"ACF of {title}")
    axes[1].set_title(f"PACF of {title}")
    # plt.show()
    fig.savefig(f"img/{title}.png")

def calculate_aicc(aic, num_params, n):
    """
    AICc = AIC + 2k(k+1)/(n - k - 1)
    k = number of parameters
    n = sample size
    """
    return aic + (2.0 * num_params * (num_params + 1)) / (n - num_params - 1)