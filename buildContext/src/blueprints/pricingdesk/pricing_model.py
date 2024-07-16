import pandas as pd
from utils.database_connection import ConnectDatabase

from ..extractors.helper.nonenergy import NonEnergy
from ..extractors.helper.energy import Energy
from ..extractors.helper.rec import Rec

import re
from ..extractors.helper.loadprofile import LoadProfile
from ..extractors.helper.shaping import Shaping
from ..extractors.helper.vlr import Vlr
from ..extractors.helper.lineloss import LineLoss



class PricingDesk:
    """
    PricingDesk
    """
    
    def __init__(self) -> None:
        self.non_energy = NonEnergy()
        self.energy = Energy()
        self.rec= Rec()
        self.loadprofile = LoadProfile()
        self.shaping = Shaping()
        self.vlr = Vlr()
        self.lineloss = LineLoss()
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def curve_date(self, control_area, curve_date, curve):
        query = f"""select curvestart from trueprice.{control_area}_{curve} where curvestart <= '{curve_date} 00:00:00.000 +0500' limit 1"""
        df = pd.read_sql(query, self.engine)
        return df.curvestart[0].strftime("%Y-%m-%d")
        
    def load_data(self, ):
        query_strings = {'iso': 'ercot',
                        'strip': ['strip_7x24'],
                        'start': '20200201',
                        'end': '20250201',
                        'idcob': 'latestall',
                        'offset': 0,
                        'operating_day': '2025-01-02',
                        'operating_day_end': '2025-01-02',
                        'curvestart': '20250102',
                        'curveend': '20250102'}
        energy, status = self.energy.extraction(query_strings)
        query_strings["curvestart"] = self.curve_date(query_strings["iso"], query_strings["operating_day_end"], "nonenergy")
        non_energy, status = self.non_energy.extraction(query_strings)
        query_strings["curvestart"] = self.curve_date(query_strings["iso"], query_strings["operating_day_end"], "rec")
        rec, status = self.rec.extraction(query_strings)
        query_strings["curve_type"] = "loadprofile"
        loadprofile, status = self.loadprofile.extraction(query_strings)
        query_strings["curve_type"] = "shaping"
        shaping, status = self.shaping.extraction(query_strings)
        query_strings["curve_type"] = "vlr"
        vlr, status = self.vlr.extraction(query_strings)
        query_strings["curve_type"] = "lineloss"
        lineloss, status = self.lineloss.extraction(query_strings)
        return None

    def calculate_price(self, ):
        self.load_data()
        return "calculate pricing"
