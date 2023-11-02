import datetime as dt
import numpy as np
import pandas as pd
import multiprocessing as mp
from struct_lib.struct_lib import (CLibInterfaceAvailableUniverse, CLibInterfaceFactor,
                                   CLibInterfaceTestReturnOpn, CLibInterfaceTestReturnNeu, CLibInterfaceICTest)
from skyrim.whiterun import CCalendar, SetFontGreen


class CICTests(object):
    def __init__(self, factor: str, ic_tests_dir: str,
                 available_universe_dir: str, exposure_dir: str, test_return_dir: str,
                 calendar: CCalendar,
                 ):
        self.factor = factor
        self.available_universe_dir = available_universe_dir

        self.calendar = calendar
        self.dst_dir = ic_tests_dir

        self.exposure_dir = exposure_dir
        self.test_return_dir = test_return_dir

        self.lib_available_universe = CLibInterfaceAvailableUniverse(self.available_universe_dir)
        self.lib_factor_exposure: CLibInterfaceFactor | None = None
        self.lib_test_return: CLibInterfaceTestReturnOpn | CLibInterfaceTestReturnNeu | None = None
        self.lib_ic_test: CLibInterfaceICTest | None = None

    @staticmethod
    def corr_one_day(df: pd.DataFrame, x: str, y: str, method: str):
        res = df[[x, y]].corr(method=method).at[x, y] if len(df) > 2 else 0
        return 0 if np.isnan(res) else res

    def get_bridge_dates(self, bgn_date: str, stp_date: str) -> (str, str, pd.DataFrame):
        __test_lag = 1
        __test_window = 1
        iter_dates = self.calendar.get_iter_list(bgn_date, stp_date, True)
        base_bgn_date = self.calendar.get_next_date(iter_dates[0], -__test_lag - __test_window)
        base_stp_date = self.calendar.get_next_date(iter_dates[-1], -__test_lag - __test_window + 1)
        base_dates = self.calendar.get_iter_list(base_bgn_date, base_stp_date, True)
        bridge_dates_df = pd.DataFrame({"base_date": base_dates, "trade_date": iter_dates})
        return base_bgn_date, base_stp_date, bridge_dates_df

    def get_available_universe(self, base_bgn_date: str, base_stp_date: str) -> pd.DataFrame:
        available_universe_lib = CLibInterfaceAvailableUniverse(self.available_universe_dir).get_lib_reader()
        available_universe_df = available_universe_lib.read_by_conditions(t_conditions=[
            ("trade_date", ">=", base_bgn_date),
            ("trade_date", "<", base_stp_date),
        ], t_value_columns=["trade_date", "instrument"])
        available_universe_lib.close()
        return available_universe_df

    def get_factor_exposure(self, base_bgn_date: str, base_stp_date: str) -> pd.DataFrame:
        factor_lib = self.lib_factor_exposure.get_lib_reader()
        factor_df = factor_lib.read_by_conditions(t_conditions=[
            ("trade_date", ">=", base_bgn_date),
            ("trade_date", "<", base_stp_date),
        ], t_value_columns=["trade_date", "instrument", "value"])
        factor_lib.close()
        return factor_df

    def get_test_return(self, bgn_date: str, stp_date: str) -> pd.DataFrame:
        test_return_lib = self.lib_test_return.get_lib_reader()
        test_return_df = test_return_lib.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "instrument", "value"])
        test_return_lib.close()
        return test_return_df

    def check_continuity(self, run_mode: str, bgn_date: str):
        if run_mode == "A":
            ic_test_lib = self.lib_ic_test.get_lib_reader()
            return ic_test_lib.check_continuity(bgn_date, self.calendar, False, self.lib_ic_test.get_lib_struct().m_tab.m_table_name)
        else:
            return 0

    def save(self, update_df: pd.DataFrame, run_mode: str):
        ic_test_lib = self.lib_ic_test.get_lib_writer(run_mode)
        ic_test_lib.update(t_update_df=update_df, t_using_index=True)
        ic_test_lib.close()
        return 0

    def main(self, run_mode: str, bgn_date: str, stp_date: str):
        if self.check_continuity(run_mode, bgn_date) == 0:
            base_bgn_date, base_stp_date, bridge_dates_df = self.get_bridge_dates(bgn_date, stp_date)
            available_universe_df = self.get_available_universe(base_bgn_date, base_stp_date)
            factor_df = self.get_factor_exposure(base_bgn_date, base_stp_date)
            test_return_df = self.get_test_return(bgn_date, stp_date)
            factors_exposure_df = pd.merge(
                left=available_universe_df, right=factor_df, on=["trade_date", "instrument"], how="inner"
            ).rename(mapper={"trade_date": "base_date"}, axis=1)
            test_return_df_expand = pd.merge(left=bridge_dates_df, right=test_return_df, on="trade_date", how="right")
            test_input_df = pd.merge(left=factors_exposure_df, right=test_return_df_expand,
                                     on=["base_date", "instrument"], how="inner", suffixes=("_e", "_r"))
            res_srs = test_input_df.groupby(by="trade_date", group_keys=True).apply(self.corr_one_day, x="value_e", y="value_r", method="spearman")
            update_df = pd.DataFrame({"value": res_srs})
            self.save(update_df, run_mode)
        return 0


class CICTestsRaw(CICTests):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lib_factor_exposure = CLibInterfaceFactor(self.exposure_dir, self.factor)
        self.lib_test_return = CLibInterfaceTestReturnOpn(self.test_return_dir)
        self.lib_ic_test = CLibInterfaceICTest(self.dst_dir, self.factor)


class CICTestsNeu(CICTests):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lib_factor_exposure = CLibInterfaceFactor(self.exposure_dir, f"{self.factor}_NEU")
        self.lib_test_return = CLibInterfaceTestReturnNeu(self.test_return_dir)
        self.lib_ic_test = CLibInterfaceICTest(self.dst_dir, f"{self.factor}_neu")


def cal_ic_tests_mp(proc_num: int, factors: list[str],
                    ic_tests_dir: str,
                    available_universe_dir: str, exposure_dir: str, test_return_dir: str,
                    calendar: CCalendar,
                    neutral_tag: str, **kwargs):
    t0 = dt.datetime.now()
    pool = mp.Pool(processes=proc_num)
    for factor in factors:
        if neutral_tag.upper() == "RAW":
            agent_tests = CICTestsRaw(factor=factor, ic_tests_dir=ic_tests_dir, available_universe_dir=available_universe_dir,
                                      exposure_dir=exposure_dir, test_return_dir=test_return_dir, calendar=calendar)
            pool.apply_async(agent_tests.main, kwds=kwargs)
        elif neutral_tag.upper() == "NEU":
            agent_tests = CICTestsNeu(factor=factor, ic_tests_dir=ic_tests_dir, available_universe_dir=available_universe_dir,
                                      exposure_dir=exposure_dir, test_return_dir=test_return_dir, calendar=calendar)
            pool.apply_async(agent_tests.main, kwds=kwargs)
    pool.close()
    pool.join()
    t1 = dt.datetime.now()
    tips = f'IC-test-{neutral_tag}'
    print(f"... {SetFontGreen(tips)} calculated")
    print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
    return 0
