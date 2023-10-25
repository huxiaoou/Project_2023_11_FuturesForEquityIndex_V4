import os
import numpy as np
import datetime as dt
import pandas as pd
from struct_lib.struct_lib import get_lib_struct_available_universe
from skyrim.whiterun import CCalendar, SetFontGreen
from skyrim.falkreath import CManagerLibReader



def cal_market_return(run_mode: str, bgn_date: str, stp_date: str,
                      market_return_dir:str
                      calendar: CCalendar):

    def __check_continuity(run_mode:str, bgn_date:str):
        if run_mode == "O":


        return 0
    def __load()->pd.DataFrame:

    print(f"... @ {dt.datetime.now()} {SetFontGreen('market index return')} calculated")
    return 0
