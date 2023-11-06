"""
Helper functions for MATRIX
"""
import pandas as pd
class MatrixHelper:
    def __init__(self):
        """
        constructor
        """
        pass

    def feature_selection(self, df):
        """
        select the feature of importance
        """

        df = df[[ 'Control Area', 'State', 'Load Zone', 'Capacity Zone',
                'Utility', 'Block Type', 'Cost Group', 'Cost Component',
                'Term (Months)', 'Beginning Date', 'Load Profile', 'Address', 'Energy',
                'Variable Load Risk (VLR)', 'Line Losses', 'NCPC', 'DA Economic',
                'DA LSCPR', 'RT Economic', 'RT LSCPR', 'Ancillaries', 'Regulation',
                'Fwd Reserve', 'RT Reserve', 'Inadvertent Energy',
                'Marginal Loss Revenue Fund', 'Price Responsive Demand',
                'Schedule 2 - Energy Admin Svc', 'Schedule 3 - Reliability Admin Svc',
                'GIS', 'ISO Fees', 'Capacity', 'ARR (Credit) ', 'RPS Charge',
                'Renewable Power', 'Sleeve Fee', 'Utility Billing Surcharge ',
                'Credit ', 'Other 1', 'Other 2', 'Total Full Requirements Price',
                'cents/kWh', 'Margin ', 'Total Bundled Price ',
                'Total Contract Load (kWh)']]
        return df

    def renaming_columns(self, df):
        """
        rename the columns accordingly
        """
        df.columns  = ['Control Area', 'State', 'Load Zone',
                    'Capacity Zone','Utility', 'Block Type', 'Cost Group',
                    'Cost Component', 'Term', 'Beginning Date', 'Load Profile',
                    'Address', 'Energy', 'Variable Load Risk', 'Line Losses', 'NCPC',
                    'DA Economic', 'DA LSCPR', 'RT Economic', 'RT LSCPR', 'Ancillaries',
                    'Regulation', 'Fwd Reserve', 'RT Reserve', 'Inadvertent Energy',
                    'Marginal Loss Revenue Fund', 'Price Responsive Demand',
                    'Schedule 2 Energy Admin Svc', 'Schedule 3 Reliability Admin Svc',
                    'GIS', 'ISO Fees', 'Capacity', 'ARR', 'RPS Charge',
                    'Renewable Power', 'Sleeve Fee', 'Utility Billing Surcharge',
                    'Credit', 'Other 1', 'Other 2', 'Total Full Requirements Price',
                    'cents', 'Margin', 'Total Bundled Price',
                    'Total Contract Load']
        
        return df

    def setup_dataframe(self, data_frame):
        """
        formats the data frame into proper format
        """
        try:
            df = data_frame
            df_data = df.iloc[24:]
            df_data = df_data.dropna(axis = 1, how = 'all')
            df_data = df_data.dropna(axis = 0, how = 'all')
            df_data.reset_index(inplace=True, drop=True)
            df_data = df_data.transpose()
            df_data.columns = df_data.iloc[0]
            df_data = df_data.drop(df_data.index[0])
            df_data.reset_index(inplace=True, drop=True)
            df_data = df_data.fillna(0)
            df_data = df_data.replace({'\$': ''}, regex=True)
            df_data = df_data.replace({'\(|\)': ''}, regex=True)
            df_data= df_data.astype(float)
            
            # making the headers dataframe and tranposing it
            df_info = df.iloc[0:24]
            df_info = df_info.reset_index(drop=True)
            df_info = df_info.dropna(axis = 1, how = 'all')
            df_info = df_info.dropna(axis = 0, how = 'all')
            df_info.reset_index(inplace=True, drop=True)
            df_info = df_info.transpose()
            df_info.columns = df_info.iloc[0]
            df_info = df_info.drop(df_info.index[0])
            df_info.reset_index(inplace=True, drop=True)

            if df_info.isnull().values.any():
                raise Exception("File Format Not Matched")
            

            resultant_df = pd.concat([df_info, df_data], axis=1)
            # column renaming
            resultant_df = self.feature_selection(resultant_df)
            resultant_df = resultant_df.replace({'\$': ''}, regex=True)
            resultant_df = resultant_df.replace({'\(|\)': ''}, regex=True)
            resultant_df = resultant_df.loc[:, ~resultant_df.columns.duplicated()]
            resultant_df = self.renaming_columns(resultant_df)
            resultant_df = resultant_df.rename(columns=lambda x: x.replace(' ', '_').lower())
            return resultant_df
        except Exception as e:

            import traceback, sys
            print(traceback.format_exc())
            return "File Format Not Matched"

        