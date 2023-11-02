import pandas as pd
from skyrim.falkreath import CLib1Tab1, CTable, CManagerLibReader, CManagerLibWriterByDate


class CLibInterface(object):
    def __init__(self, lib_save_dir: str, lib_id: str):
        self.lib_save_dir = lib_save_dir
        self.lib_id = lib_id
        self.lib_struct: CLib1Tab1 = self.get_lib_struct()

    def get_lib_struct(self) -> CLib1Tab1:
        pass

    def get_lib_reader(self) -> CManagerLibReader:
        lib_reader = CManagerLibReader(self.lib_save_dir, self.lib_struct.m_lib_name)
        lib_reader.set_default(self.lib_struct.m_tab.m_table_name)
        return lib_reader

    def get_lib_writer(self, run_mode: str) -> CManagerLibWriterByDate:
        lib_writer = CManagerLibWriterByDate(self.lib_save_dir, self.lib_struct.m_lib_name)
        lib_writer.initialize_table(self.lib_struct.m_tab, t_remove_existence=run_mode in ["O"], t_set_as_default=True)
        return lib_writer


class CLibInterfaceMarketReturn(CLibInterface):
    def __init__(self, lib_save_dir: str):
        super().__init__(lib_save_dir=lib_save_dir, lib_id="market_return")

    def get_lib_struct(self) -> CLib1Tab1:
        return CLib1Tab1(
            t_lib_name=f"{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT"},
                "value_columns": {"market": "REAL"}
            })
        )


class CLibInterfaceAvailableUniverse(CLibInterface):
    def __init__(self, lib_save_dir: str):
        super().__init__(lib_save_dir=lib_save_dir, lib_id="available_universe")

    def get_lib_struct(self) -> CLib1Tab1:
        return CLib1Tab1(
            t_lib_name=f"{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
                "value_columns": {"return": "REAL", "amount": "REAL"}
            })
        )


class CLibInterfaceTestReturn(CLibInterface):
    def __init__(self, lib_save_dir: str):
        super().__init__(lib_save_dir=lib_save_dir, lib_id="test_return")

    def get_lib_struct(self) -> CLib1Tab1:
        return CLib1Tab1(
            t_lib_name=f"{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
                "value_columns": {"value": "REAL"},
            })
        )


class CLibInterfaceTestReturnNeu(CLibInterface):
    def __init__(self, lib_save_dir: str):
        super().__init__(lib_save_dir=lib_save_dir, lib_id="test_return_neu")

    def get_lib_struct(self) -> CLib1Tab1:
        return CLib1Tab1(
            t_lib_name=f"{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
                "value_columns": {"value": "REAL"},
            })
        )


class CLibInterfaceTestReturnOpn(CLibInterface):
    def __init__(self, lib_save_dir: str):
        super().__init__(lib_save_dir=lib_save_dir, lib_id="test_return_opn")

    def get_lib_struct(self) -> CLib1Tab1:
        return CLib1Tab1(
            t_lib_name=f"{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
                "value_columns": {"value": "REAL"},
            })
        )


class CLibInterfaceFactor(CLibInterface):
    def get_lib_struct(self) -> CLib1Tab1:
        # lib_id format like ("BASISA147", "BASISA147_NEU")
        return CLib1Tab1(
            t_lib_name=f"{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
                "value_columns": {"value": "REAL"},
            })
        )


class CLibInterfaceICTest(CLibInterface):
    def get_lib_struct(self) -> CLib1Tab1:
        # lib_id format like ("BASISA147", "BASISA147_NEU")
        return CLib1Tab1(
            t_lib_name=f"ic-{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT"},
                "value_columns": {"value": "REAL"},
            })
        )


class CLibInterfaceSignal(CLibInterface):
    def get_lib_struct(self) -> CLib1Tab1:
        return CLib1Tab1(
            t_lib_name=f"{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT", "instrument": "TEXT"},
                "value_columns": {"value": "REAL"},
            })
        )


class CLibInterfaceSignalOpt(CLibInterface):
    def get_lib_struct(self) -> CLib1Tab1:
        return CLib1Tab1(
            t_lib_name=f"{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT", "signal": "TEXT"},
                "value_columns": {"value": "REAL"},
            })
        )


class CLibInterfaceNAV(CLibInterface):
    def get_lib_struct(self) -> CLib1Tab1:
        return CLib1Tab1(
            t_lib_name=f"nav-{self.lib_id}.db",
            t_tab=CTable({
                "table_name": self.lib_id,
                "primary_keys": {"trade_date": "TEXT"},
                "value_columns": {"rawRet": "REAL", "dltWgt": "REAL", "fee": "REAL",
                                  "netRet": "REAL", "nav": "REAL"},
            })
        )

    def get_nav_df(self) -> pd.DataFrame:
        nav_lib_reader = self.get_lib_reader()
        simu_nav_df = nav_lib_reader.read(["trade_date", "rawRet", "dltWgt", "fee", "netRet", "nav"])
        simu_nav_df.set_index("trade_date", inplace=True)
        nav_lib_reader.close()
        return simu_nav_df
