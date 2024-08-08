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
from flask import make_response
import datetime
import zipfile
from io import BytesIO
import json


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
    
    def data_loading(self, query_strings = {}):
        energy, status = self.energy.extraction(query_strings)

        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], query_strings["iso"]+"_nonenergy")
        non_energy, status = self.non_energy.extraction(query_strings)

        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], query_strings["iso"]+"_rec")
        rec, status = self.rec.extraction(query_strings)

        query_strings["curve_type"] = "loadprofile"
        query_strings["curvestart"], query_strings["curveend"] = self.curve_date(query_strings["operating_day_end"], query_strings["iso"]+"_loadprofile")
        loadprofile, status = self.loadprofile.extraction(query_strings, pricing=True)

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
        shaping['HourType'] = 'OnPeak'
        shaping.loc[offpeak_condition, 'HourType'] = 'OffPeak'
        energy['merge_month'] = energy.month.dt.to_period('M')
        shaping['merge_month'] = shaping.month.dt.to_period('M')
        shaping['Year'] = shaping.month.dt.year
        energy_shaping = shaping.merge(energy, on=['merge_month'], how='inner')
        energy_shaping['data_energy_shaped'] = energy_shaping['data_x']*energy_shaping['data_y']
        energy_shaping["Month"] = energy_shaping.month_x.dt.month
        vlr = vlr.rename(columns= {'datemonth': 'Month'})
        energy_shaped = energy_shaping.merge(vlr, on=['Month', 'he'], how='inner')
        energy_shaped['data_vlr_shaped'] = energy_shaped['data_energy_shaped']*energy_shaped['data']
        energy_shaped['data_vlr_shaped'] = energy_shaped['data_vlr_shaped']/100
        energy_shaped = energy_shaped.rename(columns={'curvestart_x': 'curvestart_shaping', 'curvestart_y': 'curvestart_energy', 'curvestart': 'curvestart_vlr', 'month_x': 'datemonth', 'strip_x': 'BlockType', 'merge_month': 'Cal Date', 'day_of_week': 'Day'})
        energy_shaped = energy_shaped[['datemonth', 'he', 'BlockType', 'Cal Date', 'Year', 'Day', 'HourType', 'curvestart_shaping', 'curvestart_energy', 'curvestart_vlr', 'data_energy_shaped', 'data_vlr_shaped']]
        return energy_shaped

    def nonenergy_shaping(self, nonenergy, loadprofile):
        nonenergy = nonenergy.loc[nonenergy.sub_cost_component != 'HH']
        nonenergy['merge_month'] = nonenergy.month.dt.to_period('M')
        loadprofile['merge_month'] = loadprofile.datemonth.dt.to_period('M')
        nonenergy_shaped = loadprofile.merge(nonenergy, on=['merge_month'], how='inner')
        scaling_components = ["ECRS", "NSRS", "RRS", "Reg Down", "Reg Up"]
        nonenergy_shaped.loc[nonenergy_shaped.sub_cost_component.isin(scaling_components), 'data_y'] = nonenergy_shaped.data_y/(1000*nonenergy_shaped.data_x)
        nonenergy_shaped = pd.pivot_table(nonenergy_shaped, values='data_y', index=['curvestart_x', 'curvestart_y', 'datemonth', 'he', 'yeartype', 'Month', 'daytype'], columns=['sub_cost_component'], aggfunc='first')
        sub_cost_components_list_for_aggregate = list(nonenergy_shaped.columns)
        nonenergy_shaped.columns.name = None
        nonenergy_shaped.index.name = None
        nonenergy_shaped.reset_index(inplace=True)
        nonenergy_shaped = nonenergy_shaped.rename(columns={'curvestart_x': 'curvestart_loadprofile', 'curvestart_y': 'curvestart_nonenergy', 'yeartype': 'YearType', 'daytype': 'DayType'})
        return nonenergy_shaped, sub_cost_components_list_for_aggregate

    def rec_shaping(self, rec, loadprofile):
        rec['merge_month'] = rec.month.dt.to_period('M')
        loadprofile['merge_month'] = loadprofile.datemonth.dt.to_period('M')
        rec_shaped = loadprofile.merge(rec, on=['merge_month'], how='inner')
        rec_shaped = rec_shaped.rename(columns={'data_x':'data_loadprofile', 'data_y':'data_rec', 'curvestart_y': 'curvestart_rec'})
        rec_shaped['data_loadprofile_avg'] = rec_shaped['data_loadprofile'].mean()
        rec_shaped['data_loadprofile_max'] = rec_shaped['data_loadprofile'].max()
        rec_shaped = rec_shaped[['datemonth', 'he', 'data_loadprofile', 'data_loadprofile_avg', 'data_loadprofile_max', 'curvestart_rec', 'data_rec']]
        return rec_shaped
    
    def calculate_price(self, price_request = pd.DataFrame(), iso = 'ERCOT'):
        iso = iso.upper()
        final_df = pd.DataFrame()
        if price_request.empty:
            return None, 'Request form is empty'
        try:
            query_strings = {'iso': iso.lower(),
                             'strip': ['strip_7x24'],
                             'start': datetime.datetime.strptime(price_request['Start Date'].iat[0],'%m/%d/%Y').strftime('%Y%m%d'),
                             'end': datetime.datetime.strptime(price_request['End Date'].iat[0], '%m/%d/%Y').strftime('%Y%m%d'),
                             'idcob': 'latestall',
                             'offset': 0,
                             'operating_day': datetime.datetime.strptime(price_request['Curve Date'].iat[0],'%m/%d/%Y').strftime('%Y-%m-%d'),
                             'operating_day_end': datetime.datetime.strptime(price_request['Curve Date'].iat[0],'%m/%d/%Y').strftime('%Y-%m-%d'),
                             'curvestart': datetime.datetime.strptime(price_request['Curve Date'].iat[0],'%m/%d/%Y').strftime('%Y%m%d'),
                             'curveend': datetime.datetime.strptime(price_request['Curve Date'].iat[0],'%m/%d/%Y').strftime('%Y%m%d')}

            # Loading the data
            energy, nonenergy, rec, loadprofile, shaping, vlr, lineloss = self.data_loading(query_strings)

            # Making filter parameters from price request
            load_zone = price_request['Load Zone'].iat[0]
            capacity_zone = price_request['Capacity Zone'].iat[0]
            loadprofile_cost_component = price_request['Load Profile'].iat[0]
            lineloss_utility = price_request['Utility'].iat[0]
            lineloss_cost_component = price_request['Voltage'].iat[0]
            filename = price_request['Lookup ID4'].iat[0]

            # Removing Reedundancy that restrict joining of curves
            energy.drop(['id'], axis=1, inplace=True)
            nonenergy.drop(['id'], axis=1, inplace=True)
            rec.drop(['id'], axis=1, inplace=True)
            shaping.drop(['id'], axis=1, inplace=True)
            vlr.drop(['id'], axis=1, inplace=True)
            lineloss.drop(['id'], axis=1, inplace=True)

            # Only lineloss needs control_area filter
            lineloss = lineloss.loc[lineloss.control_area == iso]

            # Filter for Shaping the data
            shaping_filtered = shaping.loc[shaping.load_zone == load_zone].reset_index(drop=True)
            vlr_filtered = vlr.loc[vlr.load_zone == capacity_zone].reset_index(drop=True) # needs refinement
            energy_filtered = energy.loc[energy.load_zone == load_zone].reset_index(drop=True)
            loadprofile_filtered = loadprofile.loc[loadprofile.cost_component == loadprofile_cost_component].reset_index(drop=True)
            rec_filtered = rec.loc[rec.sub_cost_component == 'tx_total_cost_per_mWh'].reset_index(drop=True)
            lineloss = lineloss.loc[(lineloss.utility == lineloss_utility) & (lineloss.cost_component == lineloss_cost_component)]
            lineloss_factor = lineloss['data'].iat[0]
            lineloss_curvestart = lineloss['curvestart'].iat[0]

            # Shaping the Data
            shaped_energy = self.energy_shaping(energy_filtered, shaping_filtered, vlr_filtered)
            shaped_nonenergy, sub_cost_components_list_for_aggregate = self.nonenergy_shaping(nonenergy, loadprofile_filtered)
            shaped_rec = self.rec_shaping(rec_filtered, loadprofile_filtered)

            # date format for join
            shaped_energy['datemonth'] = shaped_energy.datemonth.dt.date
            shaped_nonenergy['datemonth'] = shaped_nonenergy['datemonth'].astype(str)
            shaped_energy['datemonth'] = shaped_energy['datemonth'].astype(str)
            shaped_rec['datemonth'] = shaped_rec['datemonth'].astype(str)

            # Merging the actual data
            merged_df = pd.merge(shaped_energy, shaped_nonenergy, on=['datemonth', 'he'])
            final_df = pd.merge(merged_df, shaped_rec, on=['datemonth', 'he'])

            # Adding factor values
            final_df['data_nonenergy_shaped'] = final_df[sub_cost_components_list_for_aggregate].sum(axis=1)
            final_df['curvestart_lineloss'] = lineloss_curvestart
            final_df['lineloss_factor'] = lineloss_factor-1
            final_df['lineloss_factor'] = final_df['lineloss_factor'] * (final_df['data_energy_shaped'] + final_df['data_nonenergy_shaped'])
            final_df['margin'] = float(price_request['Margin ($/MWh)'].iat[0].replace('$', ''))
            final_df['sleeve_fee'] = float(price_request['Sleeve Fee ($/MWh)'].iat[0].replace('$', ''))
            final_df['utility_billing_surcharge'] = float(price_request['Utility Billing Surcharge ($/MWh)'].iat[0].replace('$', ''))
            final_df['other1'] = float(price_request['Other 1 ($/MWh)'].iat[0].replace('$', ''))
            final_df['other2'] = float(price_request['Other 2 ($/MWh)'].iat[0].replace('$', ''))

            # Calculating PRice model
            # aggregate_cols_list = list(set(final_df.columns) - set({'datemonth', 'he', 'curvestart_shaping', 'curvestart_energy', 'curvestart_vlr','curvestart_loadprofile', 'curvestart_nonenergy', 'curvestart_rec', 'curvestart_lineloss', 'data_loadprofile', 'data_loadprofile_avg','data_loadprofile_max'}))
            final_df['fr_price_hourly'] = final_df['data_energy_shaped'] + final_df['data_vlr_shaped'] + final_df['data_nonenergy_shaped']+\
                                          final_df['data_rec'] + final_df['lineloss_factor'] + final_df['margin'] + \
                                          final_df['sleeve_fee'] + final_df['utility_billing_surcharge'] + final_df['other1'] + final_df['other2']
            final_df['ffr_price'] = sum(final_df['fr_price_hourly'] * final_df['data_loadprofile_max']) / sum(final_df['data_loadprofile_max'])
            final_df = final_df.sort_values(by=['datemonth', 'he']).reset_index(drop=True)
            
            # Column sorting

            # Redundant Info for QA
            final_df['lookup ID4'] = filename
            final_df['lookup ID3'] = lineloss_utility + " " + lineloss_cost_component
            final_df['lookup ID2'] = final_df['YearType'] +" "+ final_df['Month'].astype(str) +" "+\
                                     final_df['DayType'] +" "+ final_df['he'].astype(str)
            final_df['lookup ID1'] = final_df['datemonth'] +" "+ final_df['he'].astype(str)
            final_df['Validation'] = 'y'
            graph_df = pd.DataFrame(final_df)
            index_items = ['lookup ID4', 'lookup ID3', 'lookup ID2', 'lookup ID1',
                           'Validation', 'datemonth', 'Cal Date', 'Year', 'YearType', 'Month',
                           'Day', 'DayType', 'he', 'HourType', 'BlockType',
                           'curvestart_shaping', 'curvestart_energy', 'curvestart_vlr', 'curvestart_loadprofile',
                           'curvestart_nonenergy', 'curvestart_rec', 'curvestart_lineloss']
            
            price_summary_cols = list(set(final_df.columns) - set(index_items+['data_nonenergy_shaped', 'data_loadprofile', 'data_loadprofile_avg', 'data_loadprofile_max', 'fr_price_hourly', 'ffr_price']))
            graph_df = graph_df[price_summary_cols+['data_loadprofile']]
            
            for i in price_summary_cols:
                graph_df[i] = graph_df[i]*graph_df["data_loadprofile"]
            
            graph_df = pd.DataFrame(graph_df.sum()).T
            
            for i in price_summary_cols:
                graph_df[i] = graph_df[i]/graph_df["data_loadprofile"]
            graph_df.drop(['data_loadprofile'], axis=1, inplace=True)
            component_labels = list(graph_df.columns)
            component_summary = graph_df.iloc[0, :].tolist()
            fr_price_hourly = list(final_df['fr_price_hourly'])
            fr_price_hourly_label = list(final_df['lookup ID1'])
            data_loadprofile = list(final_df['data_loadprofile'])
            final_df.set_index(index_items, inplace=True)
            curve_types = ['energy' if i in ['data_energy_shaped','data_vlr_shaped']
                           else 'nonenergy' if i in sub_cost_components_list_for_aggregate
                           else 'rec' if i in ['data_rec'] else 'line_loss' if i in ['lineloss_factor']
                           else 'loadprofile' if i in ['data_loadprofile', 'data_loadprofile_avg','data_loadprofile_max']
                           else 'FR Price' if i in ['fr_price_hourly', 'ffr_price']
                           else i for i in final_df.columns]
            cost_components = final_df.columns
            final_df.columns = pd.MultiIndex.from_arrays([curve_types, cost_components],
                                                         names=['curve_type', 'cost_component'])
            # return Response(final_df.to_csv(),
            #                 mimetype="text/csv",
            #                 headers={"Content-disposition":
            #                 f"attachment; filename={filename}.csv"}), 'success'
            # zip_buffer = BytesIO()
            # with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            #     zip_file.writestr(f"Summary_{filename}.csv", graph_df.to_csv())
            #     zip_file.writestr(filename+".csv", final_df.to_csv())
            # # Reset buffer position
            # zip_buffer.seek(0)

            # return Response(
            #     zip_buffer,
            #     mimetype='application/zip',
            #     headers={"Content-disposition": "attachment; filename=data.zip"}
            # ), 'success'
            # response = make_response(final_df.to_csv())
            # response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
            # response.headers['Content-Type'] = 'text/csv'
            return json.dumps({"final_df":final_df.to_csv(),
                               "filename_final_df":filename+".csv",
                               "summary_final_df":graph_df.to_csv(),
                               "filename_summary_final_df":"summary_"+filename+".csv",
                               "component_labels": component_labels,
                               "component_summary": component_summary,
                               "fr_price_hourly":fr_price_hourly,
                               "fr_price_hourly_label":fr_price_hourly_label,
                               "data_loadprofile":data_loadprofile,
                               }), 'success'
        
        except Exception as exp:
            import traceback, sys
            print('Exception line.')
            print(traceback.format_exc())
            print('exception :', exp)
            return None, 'Exception in price calculation'
