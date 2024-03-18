"""
Helper functions for PTC
"""
import pandas as pd
class PTCHelper:
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
            df_data = df.iloc[27:]
            df_data = df_data.dropna(axis = 1, how = 'all')
            df_data = df_data.dropna(axis = 0, how = 'all')
            df_data.reset_index(inplace=True, drop=True)
            df_data.columns = df_data.iloc[0]
            # df_data = df_data.drop(df_data.index[0])
            df_data.reset_index(inplace=True, drop=True)
            df_data = df_data.fillna(0)
            df_data = self.renaming_columns(df_data)
            
            # making the headers dataframe and tranposing it
            df_info = df.iloc[0:27]
            # df_info = df.iloc[[1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 15]]
            df_info = df_info.reset_index(drop=True)
            df_info = df_info.dropna(axis = 1, how = 'all')
            df_info = df_info.dropna(axis = 0, how = 'all')
            df_info.reset_index(inplace=True, drop=True)
            df_info = df_info.transpose()
            df_info.columns = df_info.iloc[0]
            df_info = df_info.drop(df_info.index[0])
            
            
            df_info.columns = [column.lower() for column in df_info.columns]
            df_info =  df_info[['matching id', 'lookup id1', 'control area', 'state', 'load zone', 
                                'capacity zone', 'utility', 'block type', 'cost group', 
                                'cost component', 'utility name', 'rate class/load profile']]
            df_info = df_info.loc[:, ~df_info.columns.duplicated()]
            df_info.reset_index(inplace=True, drop=True)

            # filling matching id
            df_info['matching id'] = df_info['matching id'].fillna('N/A')
            if df_info.isnull().values.any():
                raise Exception("File Format Not Matched")
            

            # formating the dataframe
            dataframes = []
            for index, col in enumerate(df_data.columns[1:]):
                
                
                tmp_df = df_data[["Date"]].copy()
                tmp_df.loc[:, 'Data'] = df_data.iloc[:, index+1]
                labels = ['matching id', 'lookup id1', 'control area', 'state', 'load zone', 
                            'capacity zone', 'utility', 'block type', 'cost group', 
                            'cost component', 'utility name', 'rate class/load profile']
                for label in labels:
                    tmp_df[label] = df_info.at[index, label]
                if isinstance(col, float):
                    tmp_df["sub cost component"] = tmp_df["cost component"]
                else:
                    tmp_df["sub cost component"] = col
                tmp_df = tmp_df.reset_index(drop=True)
                dataframes.append(tmp_df)

            resultant_df = pd.concat(dataframes, axis=0)
            resultant_df=resultant_df.sort_values("Date")
            resultant_df['Data'].fillna(0, inplace=True)
            # resultant_df['Data'].replace('-', '0', regex=True, inplace=True)
            resultant_df['Data'].replace(' ', '0', regex=True, inplace=True)
            resultant_df['Data'].replace('', '0', regex=True, inplace=True)
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

        