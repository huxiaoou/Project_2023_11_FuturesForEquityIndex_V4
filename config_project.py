# begin date for argument bgn in main.py
bgn_dates_in_overwrite_mod = {
    "IR": "20150416",  # instrument_return
    "AU": "20150416",  # available_universe
    "TR": "20150416",  # test_return

    "FEB": "20150416",  # factor_exposure basic
    "FE": "20160601",  # factor_exposure

    "IC": "20160701",  # ic-test
    "FECOR": "20160701",  # factors correlation

    "SIG": "20160701",  # signals
    "SIMU": "20160701",  # signals
}

# universe
concerned_instruments_universe = [
    "IH.CFE",
    "IF.CFE",
    "IC.CFE",
    "IM.CFE",
]
ciu_size = len(concerned_instruments_universe)  # should be 4

# available universe
available_universe_options = {
    "rolling_window": 20,
    "amount_threshold": 5,
}