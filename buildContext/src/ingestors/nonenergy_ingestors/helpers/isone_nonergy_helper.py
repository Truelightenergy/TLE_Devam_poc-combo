"""
Helper function for isone
"""
import pandas as pd
class IsoneNonEngerHelper:
    def __init__(self):
        """
        constructor
        """
        pass

    def setup_dataframe(self, data_frame):
        """
        formats the data frame into proper format
        """
        try:
            df = data_frame
            # setting up the data's dataframe
            df_data = df.iloc[10:]
            df_data.reset_index(inplace=True, drop=True)
            df_data.columns = df_data.iloc[0]
            df_data = df_data.drop(df_data.index[0])


            # making the headers dataframe and tranposing it
            df_info = df.iloc[1:9]
            df_info.reset_index(inplace=True, drop=True)
            df_info = df_info.transpose()
            df_info.columns = df_info.iloc[0]
            df_info = df_info.drop(df_info.index[0])
            df_info.reset_index(inplace=True, drop=True)

            # formating the dataframe
            dataframes = []
            for index, col in enumerate(df_data.columns[1:]):
                
                tmp_df = df_data[["Date"]].copy()
                tmp_df.loc[:, 'Data'] = df_data.iloc[:, index+1]
                labels = ["Control Area", "State", "Load Zone", "Capacity Zone", "Utility", "Block Type", "Cost Group", "Cost Component"]
                for label in labels:
                    tmp_df[label] = df_info.at[index, label]
                tmp_df["Sub Cost Component"] = col
                tmp_df = tmp_df.reset_index(drop=True)
                dataframes.append(tmp_df)

            resultant_df = pd.concat(dataframes, axis=0)
            resultant_df=resultant_df.sort_values("Date")
            resultant_df.reset_index(drop=True, inplace=True)

            # column renaming
            resultant_df = resultant_df.rename(columns=lambda x: x.replace(' ', '_').lower())
            return resultant_df
        except:
            return None

        