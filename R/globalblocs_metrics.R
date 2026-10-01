# GlobalBLOCS R Analytics Library
metric_return <- function(beginning, ending) (ending / beginning) - 1
metric_cagr <- function(beginning, ending, years) (ending / beginning)^(1 / years) - 1
metric_volatility <- function(returns, annualization=252) sd(returns, na.rm=TRUE) * sqrt(annualization)
metric_sharpe <- function(returns, risk_free=0, annualization=252) (mean(returns,na.rm=TRUE)-risk_free) / sd(returns,na.rm=TRUE) * sqrt(annualization)
metric_max_drawdown <- function(prices) min(prices / cummax(prices) - 1, na.rm=TRUE)
# Python metric knowledge base is the canonical metadata contract.
