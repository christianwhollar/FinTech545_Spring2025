# Final Project
**Christian Hollar**

## Part 1
The analysis followed a structured approach. First, daily prices, risk-free rates, and portfolio holdings were loaded and processed to compute returns and market excess returns. The CAPM was then estimated for each stock using pre-2024 training data, with OLS regression determining alpha, beta, and residual variance.  

For the holding period, returns were decomposed into systematic (market-driven) and idiosyncratic (stock-specific) components. Cumulative returns were calculated for each, and portfolio-level attribution was derived by weighting individual stock returns by their allocation shares.

This returned the following:

| Portfolio | Excess Return | Systematic Return | Idiosyncratic Return |  
|-----------|---------------|-------------------|-----------------------|  
| A         | 0.075446      | 0.189207          | -0.049520             |  
| B         | 0.140546      | 0.179351          | 0.019313              |  
| C         | 0.213817      | 0.190422          | 0.142389              |  
| TOTAL     | 0.429809      | 0.558980          | 0.112182              |  


Portfolio A exhibited the lowest overall excess return at 7.54%, primarily due to its negative idiosyncratic contribution (-4.95%), which dragged down performance despite a reasonable systematic return. Portfolio B delivered moderate excess returns of 14.05%, with a slightly positive idiosyncratic contribution (1.93%), indicating that stock selection added marginal value. Portfolio C was the standout performer with an excess return of 21.38%, driven by both strong systematic exposure and a significant positive idiosyncratic contribution (14.24%), suggesting excellent stock selection.  

The systematic component was relatively stable across all portfolios, ranging between 17.9% and 19.0%, reflecting consistent market-driven performance. In contrast, the idiosyncratic component showed substantial variation. Portfolio A suffered from poor stock-specific performance, while Portfolios B and C benefited from positive idiosyncratic effects. This divergence highlights the impact of individual stock selection, with Portfolio C’s alpha generation being particularly noteworthy.  

The combined portfolio achieved an excess return of 42.98%, with systematic factors contributing 55.90% and idiosyncratic factors contributing 11.22%. The dominance of systematic returns underscores the strong market performance during the holding period, while the net positive idiosyncratic contribution indicates that, on aggregate, active stock selection added value despite Portfolio A’s underperformance.  

The market exhibited strong performance during the holding period, as evidenced by the high systematic returns across all portfolios. Portfolio C’s exceptional results were driven by both market exposure and superior stock selection, while Portfolio A’s negative idiosyncratic return suggests misaligned picks that underperformed even in a favorable market.  

Notably, the aggregate idiosyncratic return was positive, demonstrating that active management added value overall.

## Part 2
The analysis for Part 2 utilized the CAPM estimates from Part 1 but assumed an alpha of zero for each stock. Expected returns for each asset were calculated as the product of the stock's beta and the historical average excess return of the market (SPY) observed prior to the holding period. The covariance matrix was computed by combining systematic and idiosyncratic components based on CAPM betas, the market variance, and residual variances.

Using these parameters, optimal portfolios were constructed to maximize the Sharpe ratio for each of the three sub-portfolios. Optimal portfolio weights were obtained by applying mean-variance optimization, specifically solving for weights as the product of the inverse covariance matrix and expected returns, normalized to sum to one. Portfolio attribution for the holding period was recalculated with these optimal weights.

The optimized portfolios showed improved performance compared to Part 1. Portfolio A's excess return increased to 15.33% (from 7.54%), Portfolio B increased to 17.33% (from 14.05%), and Portfolio C increased to 24.98% (from 21.38%). Systematic returns remained stable, while idiosyncratic contributions improved relative to Part 1 results.

| Portfolio | Excess Return | Systematic Return | Idiosyncratic Return |  
|-----------|---------------|-------------------|-----------------------|  
| A         | 0.153339      | 0.204712          | -0.028295             |  
| B         | 0.173328      | 0.189077          | 0.012317              |  
| C         | 0.249837      | 0.204209          | 0.096611              |  
| TOTAL     | 0.624657      | 0.639763          | 0.074721              |  

The improvement in idiosyncratic contributions indicates more effective stock selection and allocation through mean-variance optimization, particularly in Portfolio C. The systematic returns across portfolios remained relatively consistent with Part 1, reflecting stable market conditions during the holding period. Portfolio A continued to exhibit a negative idiosyncratic contribution, although reduced in magnitude compared to Part 1.

Additionally, the analysis compared expected versus realized idiosyncratic risk. Using CAPM residual variance estimates, the model's expected annualized idiosyncratic risk for stocks averaged 22%, close to the realized average of 24%. Individual stock risk estimates displayed similar distributions, with minor variations.

The similarity between expected and realized idiosyncratic risks demonstrates the accuracy and reliability of the CAPM-based risk estimation method. This alignment provides confidence in the risk modeling approach and supports the effectiveness of the mean-variance optimization applied to these portfolios.

## Part 3
The Normal Inverse Gaussian (NIG) and Skew Normal distributions are alternatives to the traditional normal distribution in financial modeling due to their ability to better represent features of financial returns. Empirical evidence demonstrates that asset returns often exhibit asymmetry (skewness) and extreme observations (heavy tails). These characteristics challenge the symmetry and thin-tail assumptions of the normal distribution, making it insufficient for accurately modeling financial data. As a result, distributions such as the NIG and Skew Normal have become relevant in finance.

The Normal Inverse Gaussian distribution is useful because it can model both skewness and heavy tails through distinct parameters. It includes separate parameters that control asymmetry and tail thickness, providing flexibility when fitting empirical return distributions. This flexibility enables financial analysts and risk managers to better represent rare but impactful market events, such as sharp price movements, significant drawdowns, or market crashes. The explicit inclusion of skewness and kurtosis parameters makes the NIG distribution effective in measuring portfolio risk, calculating Value-at-Risk (VaR) and Expected Shortfall (ES), and pricing derivatives where tail risks affect valuations.

The Skew Normal distribution modifies the standard normal distribution by adding a shape parameter to capture asymmetry. While it addresses skewness, it typically maintains lighter tails compared to the NIG and Student’s T distributions. This characteristic makes the Skew Normal distribution suitable in scenarios where financial returns exhibit moderate asymmetry without strong extreme events. Typical applications include modeling aggregated returns over longer periods, portfolio-level returns, or cases where simpler computational approaches are preferred. Despite its simpler structure, the Skew Normal still provides improvements over the normal distribution, better aligning with observed data while remaining computationally straightforward.

Both the NIG and Skew Normal distributions have advantages for financial modeling. The choice between these distributions depends on factors such as the observed features of the returns data, the severity of tail events, the relevance of skewness, and computational considerations. The NIG distribution generally offers a more flexible approach for modeling asymmetry and tail risk in complex market conditions. The Skew Normal provides an alternative for situations where asymmetry is present, but heavy tails are less important.



## Part 4  
The risk modeling analysis compared four distributions (Normal, Student's T, Skew Normal, and Normal Inverse Gaussian) for each stock, selecting the best fit via Akaike Information Criterion (AIC) which penalizes log-likelihood by parameter count. The Gaussian copula approach produced slightly higher tail risk estimates than multivariate normal, particularly for expected shortfall.

##### VaR/ES Results  
| Method          | Portfolio | VaR    | ES     |  
|-----------------|-----------|--------|--------|  
| MV Normal       | A         | 1.4396%| 1.7960%|  
| MV Normal       | B         | 1.3390%| 1.6741%|  
| MV Normal       | C         | 1.3944%| 1.7372%|  
| MV Normal       | TOTAL     | 3.8617%| 4.8071%|  
| Gaussian Copula | A         | 1.3873%| 1.8597%|  
| Gaussian Copula | B         | 1.2644%| 1.6630%|  
| Gaussian Copula | C         | 1.3403%| 1.7298%|  
| Gaussian Copula | TOTAL     | 3.8237%| 5.0130%|  

##### Best Fit Distributions
| Stock | Best Fit | Parameters |  
|-------|----------|------------|  
| AAPL  | T        | df=7.35, loc=0, scale=0.0107 |  
| NVDA  | T        | df=4.90, loc=0, scale=0.0219 |  
| MSFT  | T        | df=7.85, loc=0, scale=0.0137 |  
| AMZN  | T        | df=5.91, loc=0, scale=0.0169 |  
| META  | T        | df=4.31, loc=0, scale=0.0159 |  
| GOOGL | T        | df=4.46, loc=0, scale=0.0143 |  
| AVGO  | T        | df=4.61, loc=0, scale=0.0151 |  
| TSLA  | T        | df=6.56, loc=0, scale=0.0279 |  
| GOOG  | T        | df=4.63, loc=0, scale=0.0146 |  
| BRK-B | T        | df=6.79, loc=0, scale=0.0073 |  
| JPM   | T        | df=3.63, loc=0, scale=0.0090 |  
| LLY   | T        | df=3.25, loc=0, scale=0.0113 |  
| V     | T        | df=9.67, loc=0, scale=0.0088 |  
| XOM   | T        | df=8.16, loc=0, scale=0.0137 |  
| UNH   | T        | df=3.37, loc=0, scale=0.0087 |  
| MA    | T        | df=6.54, loc=0, scale=0.0089 |  
| COST  | T        | df=4.60, loc=0, scale=0.0091 |  
| PG    | T        | df=5.53, loc=0, scale=0.0076 |  
| WMT   | T        | df=6.22, loc=0, scale=0.0075 |  
| HD    | T        | df=4.58, loc=0, scale=0.0103 |  
| NFLX  | T        | df=3.68, loc=0, scale=0.0158 |  
| JNJ   | T        | df=3.71, loc=0, scale=0.0071 |  
| ABBV  | T        | df=4.04, loc=0, scale=0.0087 |  
| CRM   | T        | df=5.17, loc=0, scale=0.0142 |  
| BAC   | T        | df=4.31, loc=0, scale=0.0128 |  
| ORCL  | T        | df=3.09, loc=0, scale=0.0109 |  
| MRK   | T        | df=8.37, loc=0, scale=0.0104 |  
| CVX   | T        | df=4.69, loc=0, scale=0.0111 |  
| KO    | T        | df=5.31, loc=0, scale=0.0066 |  
| CSCO  | T        | df=4.03, loc=0, scale=0.0086 |  
| WFC   | T        | df=4.98, loc=0, scale=0.0137 |  
| ACN   | T        | df=7.12, loc=0, scale=0.0116 |  
| NOW   | NIG      | a=0.92, b=-5.8e-7, loc=0, scale=0.0194 |  
| MCD   | T        | df=10.67, loc=0, scale=0.0080 |  
| PEP   | T        | df=5.86, loc=0, scale=0.0077 |  
| IBM   | T        | df=4.88, loc=0, scale=0.0076 |  
| DIS   | T        | df=5.01, loc=0, scale=0.0129 |  
| TMO   | T        | df=5.17, loc=0, scale=0.0114 |  
| LIN   | T        | df=3.22, loc=0, scale=0.0084 |  
| ABT   | T        | df=6.21, loc=0, scale=0.0100 |  
| AMD   | T        | df=4.79, loc=0, scale=0.0228 |  
| ADBE  | T        | df=5.93, loc=0, scale=0.0164 |  
| PM    | T        | df=8.55, loc=0, scale=0.0091 |  
| ISRG  | T        | df=4.81, loc=0, scale=0.0139 |  
| GE    | T        | df=7.64, loc=0, scale=0.0131 |  
| GS    | T        | df=5.59, loc=0, scale=0.0123 |  
| INTU  | T        | df=5.68, loc=0, scale=0.0150 |  
| CAT   | T        | df=4.51, loc=0, scale=0.0133 |  
| QCOM  | T        | df=5.22, loc=0, scale=0.0156 |  
| TXN   | T        | df=9.37, loc=0, scale=0.0134 |  
| VZ    | T        | df=3.28, loc=0, scale=0.0091 |  
| AXP   | T        | df=4.73, loc=0, scale=0.0123 |  
| T     | T        | df=3.02, loc=0, scale=0.0101 |  
| BKNG  | T        | df=8.26, loc=0, scale=0.0136 |  
| SPGI  | T        | df=4.30, loc=0, scale=0.0101 |  
| MS    | T        | df=4.52, loc=0, scale=0.0123 |  
| RTX   | T        | df=3.21, loc=0, scale=0.0091 |  
| PLTR  | T        | df=3.28, loc=0, scale=0.0285 |  
| PFE   | T        | df=4.12, loc=0, scale=0.0106 |  
| BLK   | T        | df=8.02, loc=0, scale=0.0121 |  
| DHR   | T        | df=5.29, loc=0, scale=0.0119 |  
| NEE   | T        | df=2.94, loc=0, scale=0.0107 |  
| HON   | T        | df=5.91, loc=0, scale=0.0094 |  
| CMCSA | T        | df=4.55, loc=0, scale=0.0106 |  
| PGR   | T        | df=2.67, loc=0, scale=0.0100 |  
| LOW   | T        | df=4.20, loc=0, scale=0.0112 |  
| AMGN  | T        | df=6.29, loc=0, scale=0.0109 |  
| UNP   | T        | df=4.00, loc=0, scale=0.0100 |  
| TJX   | T        | df=10.11, loc=0, scale=0.0091 |  
| AMAT  | T        | df=10.42, loc=0, scale=0.0193 |  
| UBER  | T        | df=9.16, loc=0, scale=0.0200 |  
| C     | T        | df=4.21, loc=0, scale=0.0119 |  
| BSX   | T        | df=3.55, loc=0, scale=0.0086 |  
| ETN   | T        | df=3.98, loc=0, scale=0.0122 |  
| COP   | T        | df=5.86, loc=0, scale=0.0146 |  
| BA    | T        | df=4.66, loc=0, scale=0.0131 |  
| BX    | T        | df=6.20, loc=0, scale=0.0182 |  
| SYK   | T        | df=2.69, loc=0, scale=0.0087 |  
| PANW  | T        | df=3.35, loc=0, scale=0.0157 |  
| ADP   | T        | df=3.42, loc=0, scale=0.0086 |  
| FI    | T        | df=3.70, loc=0, scale=0.0089 |  
| ANET  | T        | df=2.75, loc=0, scale=0.0157 |  
| GILD  | T        | df=8.56, loc=0, scale=0.0112 |  
| BMY   | T        | df=4.34, loc=0, scale=0.0091 |  
| SCHW  | T        | df=2.83, loc=0, scale=0.0159 |  
| TMUS  | T        | df=5.67, loc=0, scale=0.0096 |  
| DE    | T        | df=5.68, loc=0, scale=0.0138 |  
| ADI   | T        | df=6.39, loc=0, scale=0.0136 |  
| VRTX  | T        | df=4.00, loc=0, scale=0.0104 |  
| SBUX  | T        | df=4.24, loc=0, scale=0.0097 |  
| MMC   | T        | df=5.62, loc=0, scale=0.0085 |  
| MDT   | T        | df=4.57, loc=0, scale=0.0104 |  
| CB    | T        | df=5.69, loc=0, scale=0.0104 |  
| LMT   | T        | df=3.66, loc=0, scale=0.0074 |  
| KKR   | T        | df=7.28, loc=0, scale=0.0171 |  
| MU    | T        | df=5.06, loc=0, scale=0.0181 |  
| PLD   | T        | df=6.54, loc=0, scale=0.0139 |  
| LRCX  | T        | df=5.53, loc=0, scale=0.0185 |  
| EQIX  | T        | df=5.22, loc=0, scale=0.0122 |  

The AIC selection overwhelmingly favored the Student's T distribution (98/99 stocks), indicating financial returns exhibit heavier tails than normal distributions can capture. NOW was the sole exception best modeled by NIG distribution (α=0.92), suggesting mild asymmetry. The Gaussian copula produced 4.3% higher total portfolio ES than multivariate normal, better capturing tail dependence. Portfolio C showed the most divergence between methods (VaR -3.9%, ES -0.4%), while Portfolio B was most stable. All fitted distributions had location parameters constrained to zero per the problem requirements.

## Part 5
The analysis in Part 5 constructed optimal risk parity portfolios using Expected Shortfall (ES) as the primary risk measure. Risk parity optimization was implemented by adjusting asset weights so that each asset contributed equally to the portfolio’s overall ES risk. Asset returns were simulated based on their fitted best-distribution models and correlated using a Gaussian copula approach. Portfolio optimization involved iteratively recalculating ES contributions and minimizing the variance between these contributions across assets. Once optimized weights were obtained, portfolio attribution for the holding period was recomputed using the previously fitted CAPM betas and decomposed into systematic and idiosyncratic components.

The risk parity portfolios, optimized using Expected Shortfall (ES) as the risk measure, yielded mixed performance compared to earlier results. Portfolio A's excess return was slightly lower at approximately 7.47%, similar to its original return of 7.54% in Part 1. However, its idiosyncratic contribution deteriorated further from -4.95% to -10.47%, indicating that the revised weights failed to mitigate negative stock-specific performance. Portfolio B showed a minor increase in excess returns from 14.05% in Part 1 to 14.66%, but the idiosyncratic component turned negative (-1.62%), suggesting weaker active stock selection.

Portfolio C, already the strongest performer, improved slightly, with excess returns increasing from 21.38% in Part 1 to 22.40% under the new risk parity approach. Systematic returns remained stable, and the idiosyncratic contribution remained strongly positive at 10.94%, demonstrating continued effective stock selection despite more conservative risk-based weight adjustments.

Overall, the combined portfolio showed lower total excess returns (33.88%) compared to Part 1 (42.98%) and Part 2 (62.47%), reflecting mixed results from the diversification strategy of the risk parity approach. The total idiosyncratic contribution (2.07%) also decreased relative to Part 1 (11.22%) and Part 2 (7.47%), indicating that the risk parity method primarily emphasized systematic factors and resulted in less favorable outcomes from active stock selection.
