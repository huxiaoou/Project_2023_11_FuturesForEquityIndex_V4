import os
import datetime as dt
import pandas as pd
import WindPy as wApi
from struct_lib.struct_lib import CLibInterfaceMarketReturn
from skyrim.whiterun import CCalendar, SetFontGreen, SetFontRed


def cal_market_return(run_mode: str, bgn_date: str, stp_date: str,
                      raw_data_dir: str, raw_data_file: str, market_index_id: str,
                      market_return_dir: str,
                      calendar: CCalendar):
    """

    :param run_mode:
    :param bgn_date:
    :param stp_date:
    :param raw_data_dir:
    :param raw_data_file: suggestion = "market_index.xlsx"
    :param market_index_id: suggestion = "881001.WI"
    :param market_return_dir:
    :param calendar:
    :return:
    """

    def __load_from_file() -> pd.DataFrame:
        src_path = os.path.join(raw_data_dir, raw_data_file)
        src_df = pd.read_excel(src_path, sheet_name=market_index_id)
        src_df["trade_date"] = src_df["Date"].map(lambda _: _.strftime("%Y%m%d"))
        return src_df[["trade_date", "pct_chg"]].set_index("trade_date").truncate(before=_d0, after=_d1).reset_index(drop=False)

    def __download_from_wapi() -> pd.DataFrame:
        wApi.w.start()
        download_data = wApi.w.wsd(market_index_id, "pct_chg", _d0, _d1, "")
        if download_data.ErrorCode == 0:
            dwnld_df = pd.DataFrame({"trade_date": iter_dates, "return": download_data.Data[0]})
            print(dwnld_df)
            return dwnld_df
        else:
            print(f"... {SetFontRed('Error!')} When download data from Wind-API, ErrorCode = {download_data.ErrorCode}")
            return pd.DataFrame({"trade_date": [], "return": []})

    iter_dates = calendar.get_iter_list(bgn_date, stp_date, True)
    _d0, _d1 = iter_dates[0], iter_dates[-1]
    lib_writer_market_return = CLibInterfaceMarketReturn(lib_save_dir=market_return_dir).get_lib_writer(run_mode)
    dst_lib_is_continuous = lib_writer_market_return.check_continuity(bgn_date, calendar) if run_mode in ["A"] else 0
    if dst_lib_is_continuous == 0:
        df = __load_from_file() if run_mode in ["O"] else __download_from_wapi()
        if not df.empty:
            lib_writer_market_return.update(df)
            lib_writer_market_return.close()
            print(f"... @ {dt.datetime.now()} {SetFontGreen('market index return')} calculated")
    else:
        print(f"... {SetFontGreen('available universe')} {SetFontRed('FAILED')} to update")
    return 0
