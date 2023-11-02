import datetime as dt
import numpy as np
import pandas as pd
from struct_lib.struct_lib import CLibInterfaceAvailableUniverse, CLibInterfaceTestReturn, CLibInterfaceTestReturnNeu
from factors.factors_shared import neutralize_by_sector
from skyrim.whiterun import CCalendar, SetFontGreen, SetFontRed


def cal_test_return_neutral(
        run_mode: str, bgn_date: str, stp_date: str | None,
        instruments_universe: list[str],
        available_universe_dir,
        sector_classification: dict[str, str],
        test_return_dir: str,
        calendar: CCalendar,
):
    _weight_id = "amount"

    # --- available universe
    available_universe_lib = CLibInterfaceAvailableUniverse(available_universe_dir).get_lib_reader()

    # --- mother universe
    mother_universe_df = pd.DataFrame({"instrument": instruments_universe})

    # --- sector df
    sector_df = pd.DataFrame.from_dict({z: {sector_classification[z]: 1} for z in instruments_universe}, orient="index").fillna(0)

    # --- test return library
    test_return_lib = CLibInterfaceTestReturn(test_return_dir).get_lib_reader()

    # --- test return neutral library
    test_return_neutral_lib = CLibInterfaceTestReturnNeu(test_return_dir).get_lib_writer(run_mode)
    dst_lib_is_continuous = test_return_neutral_lib.check_continuity(append_date=bgn_date, t_calendar=calendar) if run_mode in ["A"] else 0
    if dst_lib_is_continuous == 0:
        for trade_date in calendar.get_iter_list(t_bgn_date=bgn_date, t_stp_date=stp_date, t_ascending=True):
            test_return_df = test_return_lib.read_by_date(
                t_trade_date=trade_date,
                t_value_columns=["instrument", "value"]
            )
            if len(test_return_df) == 0:
                print(f"... Warning! trade_date = {trade_date} Not enough test return")
                continue
            weight_df = available_universe_lib.read_by_date(
                t_trade_date=trade_date,
                t_value_columns=["instrument", _weight_id]
            )
            if len(weight_df) == 0:
                print(f"... Warning! trade_date = {trade_date} Not enough weight data")
                continue

            input_df = mother_universe_df.merge(
                right=weight_df, on=["instrument"], how="inner").merge(
                right=test_return_df, on=["instrument"], how="inner").set_index("instrument")
            input_df[_weight_id] = np.sqrt(input_df[_weight_id])
            test_return_neutral_srs = neutralize_by_sector(
                t_raw_data=input_df["value"],
                t_sector_df=sector_df,
                t_weight=input_df[_weight_id]
            )
            test_return_neutral_lib.update_by_date(
                t_date=trade_date,
                t_update_df=pd.DataFrame({"value": test_return_neutral_srs}),
                t_using_index=True
            )
        print(f"... @ {dt.datetime.now()} {SetFontGreen('test return neutral')} updated")
    else:
        print(f"... {SetFontGreen('test return neutral')} {SetFontRed('FAILED')} to update")

    test_return_lib.close()
    test_return_neutral_lib.close()
    available_universe_lib.close()
    return 0
