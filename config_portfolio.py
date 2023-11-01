# unilateral hold proportion
uni_props = (0.4,)
mov_ave_wins = (5, 10, 15)

selected_raw_factors = (
    "CBETA060",
    "BETA120LD020",
    "NETOIA240",
    "NETDOIA240",
    "CTP060",
    "CTP120LD060",
    "CSP120LD060",
    "BASIS",
    "RVOL060LD060",
    "TSA180",
    "SKEW180",
    "SKEW010LD060",
    "HRA240",
    "OI",
    "MTMSP020",
)

selected_raw_factors_and_uni_prop_ma = (
    ("CTP120LD060", 0.4, 10),
    ("CBETA060", 0.4, 15),
    ("BASISBD010", 0.4, 5),
    ("CBETA120LD060", 0.4, 5),
    ("LIQUIDBD120", 0.4, 15),
    ("VOL010LD020", 0.4, 5),
    ("NETDOILD060", 0.4, 15),
    ("CSP120LD060", 0.4, 15),
    ("SRBD010", 0.4, 5),
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
