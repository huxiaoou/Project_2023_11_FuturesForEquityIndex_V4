import os
import datetime as dt
import pandas as pd
from struct_lib.struct_lib import CLibInterfaceTestReturn
from skyrim.whiterun import CCalendar, SetFontGreen, SetFontRed


def cal_test_return(run_mode: str, bgn_date: str, stp_date: str | None,
                    instruments_return_dir: str,
                    test_return_dir: str,
                    calendar: CCalendar):
    # load raw return
    raw_return_file = "instruments_return.csv.gz"
    raw_return_path = os.path.join(instruments_return_dir, raw_return_file)
    raw_return_df = pd.read_csv(raw_return_path, dtype={"trade_date": str}).set_index("trade_date")
    filter_dates = (raw_return_df.index >= bgn_date) & (raw_return_df.index < stp_date)
    raw_return_df = raw_return_df.loc[filter_dates]
    update_df = raw_return_df.stack().reset_index(level=1)

    # --- initialize lib
    test_return_lib = CLibInterfaceTestReturn(test_return_dir).get_lib_writer(run_mode)
    dst_lib_is_continuous = test_return_lib.check_continuity(append_date=bgn_date, t_calendar=calendar) if run_mode in ["A"] else 0
    if dst_lib_is_continuous == 0:
        test_return_lib.update(t_update_df=update_df, t_using_index=True)
        print(f"... @ {dt.datetime.now()} {SetFontGreen('test return')} updated")
    else:
        print(f"... {SetFontGreen('test return')} {SetFontRed('FAILED')} to update")
    test_return_lib.close()
    return 0
