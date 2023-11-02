import os
import datetime as dt
import pandas as pd
from struct_lib.struct_lib import CLibInterfaceTestReturnOpn
from skyrim.whiterun import CCalendar, SetFontGreen, SetFontRed, SetFontYellow
from skyrim.falkreath import CManagerLibReader


class CReaderMd(object):
    def __init__(self, universe: list[str], by_instru_md_dir: str, md_file_format: str = "{}.md.{}.csv.gz", price_type: str = "open"):
        self.universe = universe
        self.price_type = price_type
        self.md: dict[str, pd.DataFrame] = {}
        for instrument in universe:
            md_file = md_file_format.format(instrument, price_type)
            md_path = os.path.join(by_instru_md_dir, md_file)
            self.md[instrument] = pd.read_csv(md_path, dtype={"trade_date": str}).set_index("trade_date")

    def inquire_price(self, contract: str, instrument: str, trade_date: str):
        try:
            return self.md[instrument].at[trade_date, contract]
        except KeyError:
            print(f"... {SetFontRed(self.price_type)} price of {SetFontRed(f'{instrument}-{contract}')} at {SetFontYellow(trade_date)} is not available")
            return None

    def get_price_type(self) -> str:
        return self.price_type


class CReaderMajor(object):
    def __init__(self, major_minor_db_dir: str, major_minor_db_name: str = "major_minor.db"):
        self.reader = CManagerLibReader(major_minor_db_dir, major_minor_db_name)

    def get_major(self, instrument: str, bgn_date: str, stp_date: str) -> pd.DataFrame:
        self.reader.set_default(instrument.replace(".", "_"))
        major_df = self.reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "n_contract"])
        return major_df


def cal_test_return_opn(universe: list[str], reader_md: CReaderMd, reader_major: CReaderMajor,
                        run_mode: str, bgn_date: str, stp_date: str, test_return_dir: str,
                        calendar: CCalendar):
    test_return_dfs: list[pd.DataFrame] = []

    for instrument in universe:
        major_df = reader_major.get_major(instrument, bgn_date, stp_date)
        iter_dates = major_df["trade_date"].tolist()
        prev_iter_dates = [calendar.get_next_date(iter_dates[0], -1)] + iter_dates[:-1]

        major_df["prev_date"] = prev_iter_dates
        major_df["this_open"] = major_df.apply(
            lambda _: reader_md.inquire_price(_["n_contract"], instrument, _["trade_date"]), axis=1)
        major_df["prev_open"] = major_df.apply(
            lambda _: reader_md.inquire_price(_["n_contract"], instrument, _["prev_date"]), axis=1)
        major_df["test_return"] = (major_df["this_open"] / major_df["prev_open"] - 1).fillna(0)
        major_df["instrument"] = instrument
        test_return_df = major_df[["trade_date", "instrument", "test_return"]]
        test_return_dfs.append(test_return_df)
    update_df = pd.concat(test_return_dfs, axis=0, ignore_index=True)
    update_df.sort_values(by=["trade_date", "instrument"], ascending=True, inplace=True)

    # --- initialize lib
    test_return_lib = CLibInterfaceTestReturnOpn(test_return_dir).get_lib_writer(run_mode)
    dst_lib_is_continuous = test_return_lib.check_continuity(append_date=bgn_date, t_calendar=calendar) if run_mode in ["A"] else 0
    if dst_lib_is_continuous == 0:
        test_return_lib.update(t_update_df=update_df, t_using_index=False)
        print(f"... @ {dt.datetime.now()} {SetFontGreen(f'test return {reader_md.get_price_type()}')} updated")
    else:
        print(f"... {SetFontGreen(f'test return {reader_md.get_price_type()}')} {SetFontRed('FAILED')} to update")
    test_return_lib.close()

    return 0
