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

        df = df[['Beginning Date', 'Control Area', 'State', 'Load Zone',
                    'Capacity Zone','Utility', 'Block Type', 'Cost Group',
                    'Cost Component', 'Load Profile', 'Term (Months)', 'Sub Cost Component', 'Data']]
        return df

    def renaming_columns(self, df):
        """
        rename the columns accordingly
        """
        df.columns  = ['Beginning Date', 'Control Area', 'State', 'Load Zone',
                    'Capacity Zone','Utility', 'Block Type', 'Cost Group',
                    'Cost Component', 'Load Profile', 'Term', 'Sub Cost Component', 'Data']
        
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
            

            resultant_df = pd.DataFrame()

            # Iterating over rows and columns, adding each column value to df_info
            for index, row in df_info.iterrows():
                for column in df_data.columns:
                    # Creating a new row for each column value
                    new_row = row.copy()
                    new_row['Sub Cost Component'] = column
                    new_row['Data'] = df_data.at[index, column]
                    
                    # Appending the new row to the temporary dataframe
                    resultant_df = pd.concat([resultant_df, new_row.to_frame().T], ignore_index=True)

            resultant_df['Data'].fillna(0, inplace=True)
            resultant_df['Data'].replace('-', '0', regex=True, inplace=True)
            resultant_df['Data'].replace(' ', '0', regex=True, inplace=True)
            resultant_df['Data'].replace('', '0', regex=True, inplace=True)
            resultant_df['Data'].replace('[\$,]', '', regex=True, inplace=True)
            resultant_df['Data'].replace('[\%,]', '', regex=True, inplace=True)

            # column renaming
            resultant_df = self.feature_selection(resultant_df)
            resultant_df = resultant_df.loc[:, ~resultant_df.columns.duplicated()]
            resultant_df = self.renaming_columns(resultant_df)
            resultant_df = resultant_df.rename(columns=lambda x: x.replace(' ', '_').lower())
            return resultant_df
        except Exception as e:

            import traceback, sys
            print(traceback.format_exc())
            return "File Format Not Matched"

        