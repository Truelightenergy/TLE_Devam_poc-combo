"""
Helper functions for Miso
"""
import pandas as pd
class MisoEnergyHelper:
    def __init__(self):
        """
        constructor
        """
        pass

    def renaming_columns(self, df):
        """
        rename the columns accordingly
        """

        df.columns =  df.iloc[0].astype(str)
        df = df.drop([df.index[0]])
        df.reset_index(inplace=True, drop=True)
        
        df.rename(inplace=True, columns={
                df.columns[0]: 'Date'
            })
    
        return df

    def setup_dataframe(self, data_frame):
        """
        formats the data frame into proper format
        """
        try:
            df = data_frame
            df_data = df.iloc[10:]
            df_data = df_data.dropna(axis = 1, how = 'all')
            df_data = df_data.dropna(axis = 0, how = 'all')
            df_data.reset_index(inplace=True, drop=True)
            df_data = self.renaming_columns(df_data)
        
            
            # making the headers dataframe and tranposing it
            df_info = df.iloc[1:9]
            df_info = df_info.dropna(axis = 1, how = 'all')
            df_info = df_info.dropna(axis = 0, how = 'all')
            df_info.reset_index(inplace=True, drop=True)
            df_info = df_info.transpose()
            df_info.columns = df_info.iloc[0]
            df_info = df_info.drop(df_info.index[0])
            df_info.reset_index(inplace=True, drop=True)
            if df_info.isnull().values.any():
                raise Exception("File Format Not Matched")
            

            # formating the dataframe
            dataframes = []
            for index, col in enumerate(df_data.columns[1:]):
                
                
                tmp_df = df_data[["Date"]].copy()
                tmp_df.loc[:, 'Data'] = df_data.iloc[:, index+1]
                labels = ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component"]
                for label in labels:
                    tmp_df[label] = df_info.at[index, label]
                if isinstance(col, float):
                    tmp_df["Sub Cost Component"] = tmp_df["Cost Component"]
                else:
                    tmp_df["Sub Cost Component"] = col
                tmp_df = tmp_df.reset_index(drop=True)
                dataframes.append(tmp_df)

            resultant_df = pd.concat(dataframes, axis=0)
            resultant_df=resultant_df.sort_values("Date")
            resultant_df['Data'].fillna(0, inplace=True)
            resultant_df['Data'].replace('[\$,]', '', regex=True, inplace=True)
            resultant_df['Data'].replace('[\%,]', '', regex=True, inplace=True)
            resultant_df.reset_index(drop=True, inplace=True)

            # column renaming
            resultant_df = resultant_df.rename(columns=lambda x: x.replace(' ', '_').lower())
            return resultant_df
        except Exception as e:

            import traceback, sys
            print(traceback.format_exc())
            return "File Format Not Matched"

        