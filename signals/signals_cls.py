import datetime as dt
import itertools as ittl
import multiprocessing as mp
import numpy as np
import pandas as pd
from skyrim.whiterun import CCalendar, SetFontGreen
from struct_lib.struct_lib import CLibInterfaceAvailableUniverse, CLibInterfaceFactor


class CSignal(object):
    def __init__(self, sig_id: str, sig_save_dir: str, calendar: CCalendar):
        self.sig_id = sig_id
        self.sig_save_dir = sig_save_dir
        self.sig_lib_interface = CLibInterfaceFactor(sig_save_dir, sig_id)
        self.calendar = calendar

    def __check_continuity(self, run_mode: str, bgn_date: str) -> int:
        if run_mode in ["A"]:
            reader = self.sig_lib_interface.get_lib_reader()
            res = reader.check_continuity(bgn_date, self.calendar)
            reader.close()
            return res
        return 0

    def _get_update_df(self, run_mode: str, bgn_date: str, stp_date: str) -> pd.DataFrame:
        pass

    def __save(self, update_df: pd.DataFrame, run_mode: str, use_index: bool):
        sig_lib_writer = self.sig_lib_interface.get_lib_writer(run_mode)
        sig_lib_writer.update(update_df, use_index)
        sig_lib_writer.close()
        return 0

    def main(self, run_mode: str, bgn_date: str, stp_date: str):
        if self.__check_continuity(run_mode, bgn_date) == 0:
            update_df = self._get_update_df(run_mode, bgn_date, stp_date)
            self.__save(update_df, run_mode, use_index=False)
        return 0

    def get_id(self) -> str:
        return self.sig_id


class CSignalReader(CSignal):
    def get_signal_data(self, bgn_date: str, stp_date: str) -> pd.DataFrame:
        sig_lib_reader = self.sig_lib_interface.get_lib_reader()
        sig_df = sig_lib_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "instrument", "value"])
        sig_lib_reader.close()
        return sig_df


class CSignalMA(CSignalReader):
    def __init__(self, src_sig_id: str, src_sig_save_dir: str, mov_ave_win: int, **kwargs):
        sig_id = f"{src_sig_id}_MA{mov_ave_win:02d}"
        self.src_sig_lib_interface = CLibInterfaceFactor(src_sig_save_dir, src_sig_id)
        self.mov_ave_win = mov_ave_win
        super().__init__(sig_id=sig_id, **kwargs)

    def __get_src_signal(self, bgn_date: str, stp_date: str) -> pd.DataFrame:
        src_lib_reader = self.src_sig_lib_interface.get_lib_reader()
        src_sig_df = src_lib_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "instrument", "value"])
        src_lib_reader.close()
        return src_sig_df

    def _get_update_df(self, run_mode: str, bgn_date: str, stp_date: str) -> pd.DataFrame:
        iter_dates = self.calendar.get_iter_list(bgn_date, stp_date, True)
        base_date = self.calendar.get_next_date(iter_dates[0], -self.mov_ave_win + 1)
        src_sig_df = self.__get_src_signal(base_date, stp_date)
        src_sig_pivot_df = pd.pivot_table(data=src_sig_df, index="trade_date", columns="instrument", values="value")
        mov_ave_df = src_sig_pivot_df.rolling(window=self.mov_ave_win, min_periods=1).mean()
        wgt_abs_sum = mov_ave_df.abs().sum(axis=1)
        mov_ave_df_norm = mov_ave_df.div(wgt_abs_sum, axis=0).fillna(0)
        update_df = mov_ave_df_norm.stack(dropna=False).reset_index()
        return update_df


class CSignalWithAvailableUniverse(CSignalReader):
    def __init__(self, available_universe_dir: str, **kwargs):
        self.available_universe_lib_interface = CLibInterfaceAvailableUniverse(available_universe_dir)
        super().__init__(**kwargs)

    def _get_available_universe_df(self, bgn_date: str, stp_date: str) -> pd.DataFrame:
        lib_reader = self.available_universe_lib_interface.get_lib_reader()
        df = lib_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "instrument"])
        lib_reader.close()
        return df


class CSignalFromSrcFactor(CSignalWithAvailableUniverse):
    def __init__(self, src_factor_id: str, src_factor_dir: str, sig_id: str, **kwargs):
        """

        :param src_factor_id: ("BASISA147", "BASISA147_WS")
        :param src_factor_dir:
        :param kwargs:
        """
        self.src_factor_lib_interface = CLibInterfaceFactor(src_factor_dir, src_factor_id)
        super().__init__(sig_id=sig_id, **kwargs)

    def _get_factor_exposure_df(self, bgn_date: str, stp_date: str):
        lib_reader = self.src_factor_lib_interface.get_lib_reader()
        df = lib_reader.read_by_conditions(t_conditions=[
            ("trade_date", ">=", bgn_date),
            ("trade_date", "<", stp_date),
        ], t_value_columns=["trade_date", "instrument", "value"])
        lib_reader.close()
        return df


class CSignalHedge(CSignalFromSrcFactor):
    def __init__(self, uni_prop: float, src_factor_id: str, src_factor_dir: str, **kwargs):
        self.uni_prop = uni_prop
        sig_id = f"{src_factor_id}_UHP{int(uni_prop * 10):02d}"
        super().__init__(src_factor_id, src_factor_dir, sig_id, **kwargs)

    def __cal_signal(self, df: pd.DataFrame):
        sorted_df = df[["instrument", "value"]].sort_values(["value", "instrument"], ascending=[False, True])
        k = len(df)
        k0 = int(np.round(k * self.uni_prop))
        rel_wgt = np.array([1] * k0 + [0] * (k - 2 * k0) + [-1] * k0)
        wgt = rel_wgt / np.abs(rel_wgt).sum()
        return pd.Series(data=wgt, index=sorted_df["instrument"])

    def _get_update_df(self, run_mode: str, bgn_date: str, stp_date: str) -> pd.DataFrame:
        available_universe_df = self._get_available_universe_df(bgn_date, stp_date)
        factor_exposure_df = self._get_factor_exposure_df(bgn_date, stp_date)
        merged_df = pd.merge(left=available_universe_df, right=factor_exposure_df, on=["trade_date", "instrument"], how="inner")
        merged_df.dropna(axis=0, subset=["value"], inplace=True)
        res_agg = merged_df.groupby(by="trade_date").apply(self.__cal_signal)
        if isinstance(res_agg, pd.Series):
            update_df = res_agg.reset_index()
        elif isinstance(res_agg, pd.DataFrame):
            update_df = res_agg.stack(dropna=False).reset_index()
        else:
            print("... Wrong type of result when calculate factors neutral.")
            print("... The result is neither a pd.Series nor a pd.DataFrame.")
            update_df = pd.DataFrame()
        return update_df


def cal_signals_hedge_mp(proc_num: int, factors: tuple[str], uni_props: tuple[str],
                         available_universe_dir: str, signals_save_dir: str, src_factor_dir: str,
                         calendar: CCalendar, tips: str, **kwargs):
    t0 = dt.datetime.now()
    pool = mp.Pool(processes=proc_num)
    for factor, uni_prop in ittl.product(factors, uni_props):
        s = CSignalHedge(uni_prop=uni_prop, src_factor_dir=src_factor_dir, src_factor_id=factor,
                         available_universe_dir=available_universe_dir, sig_save_dir=signals_save_dir, calendar=calendar)
        pool.apply_async(s.main, kwds=kwargs)
    pool.close()
    pool.join()
    t1 = dt.datetime.now()
    print(f"... {SetFontGreen(tips)} calculated")
    print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
    return 0


def cal_signals_hedge_ma_mp(proc_num: int, factors: tuple[str], uni_props: tuple[str], mov_ave_wins: tuple[int],
                            src_signals_save_dir: str, signals_save_dir: str,
                            calendar: CCalendar, tips: str, **kwargs):
    t0 = dt.datetime.now()
    pool = mp.Pool(processes=proc_num)
    for factor, uni_prop, mov_ave_win in ittl.product(factors, uni_props, mov_ave_wins):
        src_sig_id = f"{factor}_UHP{int(uni_prop * 10):02d}"
        s = CSignalMA(src_sig_id=src_sig_id, src_sig_save_dir=src_signals_save_dir, mov_ave_win=mov_ave_win,
                      sig_save_dir=signals_save_dir, calendar=calendar)
        pool.apply_async(s.main, kwds=kwargs)
    pool.close()
    pool.join()
    t1 = dt.datetime.now()
    print(f"... {SetFontGreen(tips)} calculated")
    print(f"... total time consuming: {SetFontGreen(f'{(t1 - t0).total_seconds():.2f}')} seconds")
    return 0
