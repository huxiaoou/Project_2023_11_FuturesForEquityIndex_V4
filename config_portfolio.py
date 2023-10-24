# unilateral hold proportion
uni_props = (0.2, 0.3, 0.4)
mov_ave_wins = (5, 10, 15)

selected_raw_factors = (
    "BASISA120",
    "CTP120",
    "CSP180LD020",
    "CVP120",
    "RSBR010",
    "RSBR240",
    "TSA120",
    "MTMS240",
    "SKEW010",
    "SKEW120",
    "BETA020",
    "NETDOI",
    "SIZEBR010",
    "SRLD240",
    "VOL020",
    "IBETA240LD024",
    "LIQUIDBD010",
    "LIQUIDBD180",
    "RVOL060",
)

selected_raw_factors_and_uni_prop_ma = (
    ("RSBR240", 0.4, 5),
    ("RSLR240", 0.3, 5),
    ("BASISA060", 0.2, 15),
    ("CVP180LD020", 0.4, 15),
    ("CTP180LD020", 0.4, 15),
    ("CSP180LD020", 0.4, 5),
    ("CTP120", 0.3, 5),
    ("CVP120", 0.2, 15),
    ("CSP120", 0.3, 5),
    ("SKEW120", 0.2, 15),
    ("SKEW180LD020", 0.2, 15),
    ("TSA060", 0.4, 15),
    ("NETDOIBD020", 0.2, 10),
    ("HRA060", 0.4, 10),
)
selected_src_signal_ids_raw = [f"{fac}_UHP{int(uhp * 10):02d}_MA{maw:02d}" for fac, uhp, maw in selected_raw_factors_and_uni_prop_ma]
size_raw = len(selected_src_signal_ids_raw)

trn_win, lbd = 3, 20  # optimized
min_model_days = int(trn_win * 20 * 0.9)
test_portfolio_ids = [
    "RF",  # "raw_fix",
    "RD",  # "raw_min_uty_con",
]

# secondary parameters
cost_rate_hedge_test = 0e-4
cost_rate_portfolios = 5e-4
risk_free_rate = 0
performance_indicators = [
    "hold_period_return",
    "annual_return",
    "annual_volatility",
    "sharpe_ratio",
    "calmar_ratio",
    "max_drawdown_scale",
    "max_drawdown_scale_idx",
]

if __name__ == "__main__":
    from config_factor import factors_raw

    print("\n".join(factors_raw))
    print("Total number of factors = {}".format(len(factors_raw)))  # 410
