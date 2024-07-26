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

    def curve_date(self, curve_date, table):
        query = f"""select curvestart from trueprice.{table} where curvestart <= '{curve_date} 23:59:59.999 +0500' order by curvestart desc limit 1"""
        try:
            df = pd.read_sql(query, self.engine)
            return df.curvestart[0].strftime("%Y%m%d"), df.curvestart[0].strftime("%Y%m%d")
        except Exception as exp:
            print('exp in curve date: ', exp)
            return None, None
    def data_loading(self, ):
        query_strings = {'iso': 'ercot',
                        'strip': ['strip_7x24'],
                        'start': '20200201',
                        'end': '20250201',
                        'idcob': 'latestall',
                        'offset': 0,
                        'operating_day': '2025-01-03',
                        'operating_day_end': '2025-01-03',
                        'curvestart': '20250103',
                        'curveend': '20250103'}
        energy, status = self.energy.extraction(query_strings)

        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], query_strings["iso"]+"_nonenergy")
        non_energy, status = self.non_energy.extraction(query_strings)

        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], query_strings["iso"]+"_rec")
        rec, status = self.rec.extraction(query_strings)

        query_strings["curve_type"] = "loadprofile"
        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], query_strings["iso"]+"_loadprofile")
        loadprofile, status = self.loadprofile.extraction(query_strings)

        query_strings["curve_type"] = "shaping"
        query_strings["strip"] = ['strip_5x16', 'strip_2x16', 'strip_7x8']
        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], query_strings["iso"]+"_shaping")
        shaping, status = self.shaping.extraction(query_strings)
        query_strings["strip"] = ['strip_7x24']

        query_strings["curve_type"] = "vlr"
        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], query_strings["iso"]+"_vlr")
        vlr, status = self.vlr.extraction(query_strings)

        query_strings["curve_type"] = "lineloss"
        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], "lineloss")
        lineloss, status = self.lineloss.extraction(query_strings)
        return energy, non_energy, rec, loadprofile, shaping, vlr, lineloss

    def energy_shaping(self, energy, shaping, vlr):
        shaping = shaping.loc[shaping.load_zone == 'NORTH ZONE'].reset_index(drop=True)
        vlr = vlr.loc[vlr.load_zone == 'NORTH'].reset_index(drop=True)
        # Lets Prepare shaping
        shaping['day_of_week'] = shaping['month'].dt.dayofweek
        # Define the conditions
        weekday_condition = (shaping['day_of_week'] < 5) & (shaping['he'].between(7, 22))
        weekend_condition = (shaping['day_of_week'] >= 5) & (shaping['he'].between(7, 22))
        offpeak_condition = (shaping['he'].between(1, 6)) | (shaping['he'].between(23, 24))

        # Apply conditions to filter the DataFrame
        shaping = shaping[
            ((shaping['strip'] == '5x16') & weekday_condition) |
            ((shaping['strip'] == '2x16') & weekend_condition) |
            ((shaping['strip'] == '7x8') & offpeak_condition)
        ]
        energy = energy.loc[energy.load_zone == 'NORTH ZONE'].reset_index(drop=True)
        energy['merge_month'] = energy.month.dt.to_period('M')
        shaping['merge_month'] = shaping.month.dt.to_period('M')
        energy_shaping = shaping.merge(energy, on=['merge_month'], how='inner')
        energy_shaping["Month"] = energy_shaping.month_x.dt.month
        vlr = vlr.rename(columns= {'datemonth': 'Month'})
        energy_shaped = energy_shaping.merge(vlr, on=['Month', 'he'], how='inner')
        return energy_shaped

    def nonenergy_shaping(self, nonenergy, loadprofile):
        nonenergy['merge_month'] = nonenergy.month.dt.to_period('M')
        loadprofile['merge_month'] = loadprofile.datemonth.dt.to_period('M')
        nonenergy_shaped = loadprofile.merge(nonenergy, on=['merge_month'], how='inner')
        scaling_components = ["ECRS", "NSRS", "RRS", "Reg Down", "Reg Up"]
        nonenergy_shaped.loc[nonenergy_shaped.cost_component_y.isin(scaling_components), 'data_y'] = nonenergy_shaped.data_y/(1000*nonenergy_shaped.data_x)
        return nonenergy_shaped

    def rec_shaping(self, rec, loadprofile):
        rec = rec.loc[rec.sub_cost_component == 'tx_total_cost_per_mWh'].reset_index(drop=True)
        rec['merge_month'] = rec.month.dt.to_period('M')
        loadprofile['merge_month'] = loadprofile.datemonth.dt.to_period('M')
        rec_shaped = loadprofile.merge(rec, on=['merge_month'], how='inner')
        return rec_shaped
    
    def calculate_price(self, ):
        energy, nonenergy, rec, loadprofile, shaping, vlr, lineloss = self.data_loading()
        loadprofile = loadprofile.loc[loadprofile.cost_component == 'DS3MH-CILCO'].reset_index(drop=True)
        shaped_energy = self.energy_shaping(energy, shaping, vlr)
        shaped_nonenergy = self.nonenergy_shaping(nonenergy, loadprofile)
        shaped_rec = self.rec_shaping(rec, loadprofile)
        shaped_energy['datemonth'] = shaped_energy.month_x.dt.date
        merged_df = pd.merge(shaped_energy, shaped_nonenergy, on=['datemonth', 'he'])
        # Merge the result with the third DataFrame
        final_df = pd.merge(merged_df, shaped_rec, on=['datemonth', 'he'])
        return "calculate pricing"
