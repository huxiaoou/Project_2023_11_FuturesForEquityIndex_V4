# begin date for argument bgn in main.py
bgn_dates_in_overwrite_mod = {
    "IR": "20150416",  # instrument_return
    "AU": "20150416",  # available_universe
    "MR": "20120101",  # market return
    "TR": "20150416",  # test_return

    "FEB": "20150416",  # factor_exposure basic
    "FE": "20160601",  # factor_exposure

    "IC": "20170701",  # ic-test
    "FECOR": "20170701",  # factors correlation

    "SIG": "20170701",  # signals
    "SIMU": "20170701",  # signals
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

#
market_index_id = "881001.WI"
