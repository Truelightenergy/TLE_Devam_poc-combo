"""
Implements the Slowly Changed Dimensions to insert the data into database
"""

import pandas as pd
import datetime
from database_conection import ConnectDatabase

class Pjm_Rec:
    """
    constructor which will makes the connection to the database
    """
    
    def __init__(self):
        """
        makes the 
        """
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def pre_processings(self, df):
        """
        makes some pre-processing to the dataframe
        """
        # remove post-fixes from the column names
        df.columns = df.columns.str.replace('\.\d+', '', regex=True)
        # replace the spaces with under-scores from the column names
        df.iloc[0] = df.iloc[0].str.replace(" ", "_")
        # removing the parathesis
        df.iloc[0] = df.iloc[0].str.replace('[()]', '', regex=True)
        # replace % with PER in dataframe columns
        df.iloc[0] = df.iloc[0].str.replace("%", "PER")
        # Merging the row 1 and row 2 into dataframe column
        df.columns = df.columns.astype(str) +'_'+ df.iloc[0].astype(str)
        # droping states row
        df = df.drop(df.index[0])

        # fill missing values with specified values for each column
        fill_values = {
            col: '$0' if '$' in str(df[col]) else '0%'
            for col in df.columns
        }
        df.fillna(fill_values, inplace=True)

        # removing $ and % signs
        df[df.columns[2:]] = df[df.columns[2:]].replace('[\$,%]', '', regex=True).astype(float)

        # date parsing
        df['NJ_EY'] = pd.to_datetime(df['NJ_EY'])

        return df
    
    def renaming_columns(self, df, iso):
        """
        rename the columns accordingly
        """
        df = df.rename(columns={'NJ_EY': 'Month',
            df.columns[1]: 'strip',
            'NJ_Total_Cost_per_MWh':'NJ_Total_Cost_per_MWh_amount',
            'NJ_Solar':'NJ_Solar_percent',
            'NJ_Solar_Price':'NJ_Solar_amount',
            'NJ_Class_I':'NJ_Class_I_percent',
            'NJ_Class_I_Price':'NJ_Class_I_amount', 
            'NJ_Class_II':'NJ_Class_II_percent', 
            'NJ_Class_II_Price':'NJ_Class_II_amount',
            'OH_Total_Cost_per_MWh':'OH_Total_Cost_per_MWh_amount',
            'OH_Solar':'OH_Solar_percent', 
            'OH_Solar_In_State':'OH_Solar_In_State_amount',
            'OH_Solar_Adj':'OH_Solar_Adj_amount', 
            'OH_RECs':'OH_RECs_percent',
            'OH_In_State_Price':'OH_In_State_amount', 
            'OH_Adj_Price':'OH_Adj_amount',
            'PA_Total_Cost_per_MWh':'PA_Total_Cost_per_MWh_amount',
            'PA_Solar':'PA_Solar_percent',
            'PA_Solar_Price':'PA_Solar_amount', 
            'PA_Tier_I':'PA_Tier_I_percent',
            'PA_Tier_I_Price':'PA_Tier_I_amount', 
            'PA_Tier_II':'PA_Tier_II_percent',
            'PA_Tier_II_Price':'PA_Tier_II_amount',
            'MD_Total_Cost_per_MWh':'MD_Total_Cost_per_MWh_amount',
            'MD_Solar':'MD_Solar_percent', 
            'MD_Solar_Price':'MD_Solar_amount', 
            'MD_Tier_I':'MD_Tier_I_percent',
            'MD_Tier_I_Price':'MD_Tier_I_amount', 
            'MD_Tier_II':'MD_Tier_II_percent', 
            'MD_Tier_II_Price':'MD_Tier_II_amount',
            'DC_Total_Cost_per_MWh':'DC_Total_Cost_per_MWh_amount',
            'DC_Solar':'DC_Solar_percent',
            'DC_Solar_Price':'DC_Solar_amount',
            'DC_Tier_I':'DC_Tier_I_percent',
            'DC_Tier_I_Price':'DC_Tier_I_amount',
            'DC_Tier_II':'DC_Tier_II_percent',
            'DC_Tier_II_Price':'DC_Tier_II_amount',
            'DE_Total_Cost_per_MWh':'DE_Total_Cost_per_MWh_amount',
            'DE_Solar':'DE_Solar_percent', 
            'DE_Solar_Price':'DE_Solar_amount',
            'DE_RECs':'DE_RECs_percent',
            'DE_REC_Price':'DE_REC_amount', 
            'IL_Total_Cost_per_MWh':'IL_Total_Cost_per_MWh_amount',
            'IL_prct_o_load__covered_by_Supplier_vs_Utility':'IL_PER_o_load_covered_by_Supplier_vs_Utility_percent',
            'IL_Total_Standard':'IL_Total_Standard_percent',
            'IL_Solar':'IL_Solar_percent',
            'IL_Solar_Price':'IL_Solar_amount',
            'IL_Wind':'IL_Wind_percent', 
            'IL_Wind_Price':'IL_Wind_amount',
            'IL_ACP_prct':'IL_ACP_percent',
            'IL_ACP':'IL_ACP_amount'
            })
        df.columns = df.columns.str.lower()
            
        return df
    
    def ingestion(self, data):
        """
        Handling Ingestion for rec
        """
        try:
            df = pd.read_csv(data.fileName)
            # some pre processings
            df = self.pre_processings(df)
            # renaming columns
            df = self.renaming_columns(df, data.controlArea)

            df.insert(0, 'curvestart', data.curveStart) # date on file, not the internal zone/month column
            # df.insert(0, 'strip', data.strip) # stored as object, don't freak on dtypes
            


            # using exists always return true or false versus empty/None
            sod = data.curveStart.strftime('%Y-%m-%d') # drop time, since any update should be new
            now = data.curveStart
            eod = (data.curveStart + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

            check_query = f"""
                -- if nothing found, new data, insert it, or do one of these
                
                select exists(select 1 from trueprice.{data.controlArea}_rec where curvestart='{now}') -- ignore, db == file based on timestamp
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_rec where curvestart>='{sod}' and curvestart<'{now}') -- update, db is older
                UNION ALL
                select exists(select 1 from trueprice.{data.controlArea}_rec where curvestart>'{now}' and curvestart<'{eod}') -- ignore, db is newer
            """
            query_result = pd.read_sql(check_query, self.engine)
            same, old_exists, new_exists = query_result.exists[0], query_result.exists[1], query_result.exists[2]

            if same: # if data already exists neglect it
                return "Data already exists based on timestamp and strip"
            
            elif not same and not new_exists and not old_exists: # if data is new then insert it
                r = df.to_sql(f"{data.controlArea}_rec", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
                if r is not None:
                    return "Data Inserted"
                return "Failed to insert"         

            elif old_exists: # if there exists old data, handle it with slowly changing dimensions
                tmp_table_name = f"{data.controlArea}_rec{data.snake_timestamp()}" # temp table to hold new csv data so we can work in SQL
                r = df.to_sql(f'{tmp_table_name}', con = self.engine, if_exists = 'replace', chunksize=1000, schema="trueprice", index=False)
                if r is None:
                    return "Unable to create data"

                with self.engine.connect() as con:
                    curveend = data.curveStart # the new data ends the old data
                    backup_query = f'''
                        with current as (
                            -- get the current rows in the database, all of them, not just things that will change

                            select id, strip, curvestart, Month, NJ_Total_Cost_per_MWh_amount, NJ_Solar_percent, NJ_Solar_amount, NJ_Class_I_percent, NJ_Class_I_amount, 
                            NJ_Class_II_percent, NJ_Class_II_amount, OH_Total_Cost_per_MWh_amount, OH_Solar_percent, OH_Solar_In_State_amount,
                            OH_Solar_Adj_amount, OH_RECs_percent, OH_In_State_amount, OH_Adj_amount, PA_Total_Cost_per_MWh_amount,
                            PA_Solar_percent, PA_Solar_amount, PA_Tier_I_percent, PA_Tier_I_amount, PA_Tier_II_percent, PA_Tier_II_amount,
                            MD_Total_Cost_per_MWh_amount, MD_Solar_percent, MD_Solar_amount, MD_Tier_I_percent, MD_Tier_I_amount, 
                            MD_Tier_II_percent, MD_Tier_II_amount, DC_Total_Cost_per_MWh_amount, DC_Solar_percent, DC_Solar_amount,
                            DC_Tier_I_percent, DC_Tier_I_amount, DC_Tier_II_percent, DC_Tier_II_amount, DE_Total_Cost_per_MWh_amount,
                            DE_Solar_percent, DE_Solar_amount, DE_RECs_percent, DE_REC_amount, IL_Total_Cost_per_MWh_amount,
                            IL_PER_o_load_covered_by_Supplier_vs_Utility_percent, IL_Total_Standard_percent, IL_Solar_percent,
                            IL_Solar_amount, IL_Wind_percent, IL_Wind_amount, IL_ACP_percent, IL_ACP_amount from trueprice.{data.controlArea}_rec where curvestart>='{sod}' and curvestart<='{eod}'
                        ),
                        backup as (
                            -- take current rows and insert into database but with a new "curveend" timestamp

                            insert into trueprice.{data.controlArea}_rec_history (id, strip, curvestart, curveend, Month, NJ_Total_Cost_per_MWh_amount, NJ_Solar_percent, NJ_Solar_amount, NJ_Class_I_percent, NJ_Class_I_amount, 
                            NJ_Class_II_percent, NJ_Class_II_amount, OH_Total_Cost_per_MWh_amount, OH_Solar_percent, OH_Solar_In_State_amount,
                            OH_Solar_Adj_amount, OH_RECs_percent, OH_In_State_amount, OH_Adj_amount, PA_Total_Cost_per_MWh_amount,
                            PA_Solar_percent, PA_Solar_amount, PA_Tier_I_percent, PA_Tier_I_amount, PA_Tier_II_percent, PA_Tier_II_amount,
                            MD_Total_Cost_per_MWh_amount, MD_Solar_percent, MD_Solar_amount, MD_Tier_I_percent, MD_Tier_I_amount, 
                            MD_Tier_II_percent, MD_Tier_II_amount, DC_Total_Cost_per_MWh_amount, DC_Solar_percent, DC_Solar_amount,
                            DC_Tier_I_percent, DC_Tier_I_amount, DC_Tier_II_percent, DC_Tier_II_amount, DE_Total_Cost_per_MWh_amount,
                            DE_Solar_percent, DE_Solar_amount, DE_RECs_percent, DE_REC_amount, IL_Total_Cost_per_MWh_amount,
                            IL_PER_o_load_covered_by_Supplier_vs_Utility_percent, IL_Total_Standard_percent, IL_Solar_percent,
                            IL_Solar_amount, IL_Wind_percent, IL_Wind_amount, IL_ACP_percent, IL_ACP_amount)

                            select id, strip, curvestart, '{curveend}' as curveend, Month, NJ_Total_Cost_per_MWh_amount, NJ_Solar_percent, NJ_Solar_amount, NJ_Class_I_percent, NJ_Class_I_amount, 
                            NJ_Class_II_percent, NJ_Class_II_amount, OH_Total_Cost_per_MWh_amount, OH_Solar_percent, OH_Solar_In_State_amount,
                            OH_Solar_Adj_amount, OH_RECs_percent, OH_In_State_amount, OH_Adj_amount, PA_Total_Cost_per_MWh_amount,
                            PA_Solar_percent, PA_Solar_amount, PA_Tier_I_percent, PA_Tier_I_amount, PA_Tier_II_percent, PA_Tier_II_amount,
                            MD_Total_Cost_per_MWh_amount, MD_Solar_percent, MD_Solar_amount, MD_Tier_I_percent, MD_Tier_I_amount, 
                            MD_Tier_II_percent, MD_Tier_II_amount, DC_Total_Cost_per_MWh_amount, DC_Solar_percent, DC_Solar_amount,
                            DC_Tier_I_percent, DC_Tier_I_amount, DC_Tier_II_percent, DC_Tier_II_amount, DE_Total_Cost_per_MWh_amount,
                            DE_Solar_percent, DE_Solar_amount, DE_RECs_percent, DE_REC_amount, IL_Total_Cost_per_MWh_amount,
                            IL_PER_o_load_covered_by_Supplier_vs_Utility_percent, IL_Total_Standard_percent, IL_Solar_percent,
                            IL_Solar_amount, IL_Wind_percent, IL_Wind_amount, IL_ACP_percent, IL_ACP_amount
                            from current
                        ),
                        single as (
                            select curvestart from current limit 1
                        )
                        -- update the existing "current" with the new "csv"

                        update trueprice.{data.controlArea}_rec set
                        curvestart = newdata.curveStart, -- this reflects the intra update, should only be the time not the date
                        strip = newdata.strip,
                        Month = newdata.Month,
                        NJ_Total_Cost_per_MWh_amount = newdata.NJ_Total_Cost_per_MWh_amount,
                        NJ_Solar_percent = newdata.NJ_Solar_percent,
                        NJ_Solar_amount = newdata.NJ_Solar_amount,
                        NJ_Class_I_percent = newdata.NJ_Class_I_percent,
                        NJ_Class_I_amount = newdata.NJ_Class_I_amount, 
                        NJ_Class_II_percent = newdata.NJ_Class_II_percent, 
                        NJ_Class_II_amount = newdata.NJ_Class_II_amount,
                        OH_Total_Cost_per_MWh_amount = newdata.OH_Total_Cost_per_MWh_amount,
                        OH_Solar_percent = newdata.OH_Solar_percent, 
                        OH_Solar_In_State_amount = newdata.OH_Solar_In_State_amount,
                        OH_Solar_Adj_amount = newdata.OH_Solar_Adj_amount, 
                        OH_RECs_percent = newdata.OH_RECs_percent,
                        OH_In_State_amount = newdata.OH_In_State_amount, 
                        OH_Adj_amount = newdata.OH_Adj_amount,
                        PA_Total_Cost_per_MWh_amount = newdata.PA_Total_Cost_per_MWh_amount,
                        PA_Solar_percent = newdata.PA_Solar_percent,
                        PA_Solar_amount = newdata.PA_Solar_amount, 
                        PA_Tier_I_percent = newdata.PA_Tier_I_percent,
                        PA_Tier_I_amount = newdata.PA_Tier_I_amount, 
                        PA_Tier_II_percent = newdata.PA_Tier_II_percent,
                        PA_Tier_II_amount = newdata.PA_Tier_II_amount,
                        MD_Total_Cost_per_MWh_amount = newdata.MD_Total_Cost_per_MWh_amount,
                        MD_Solar_percent = newdata.MD_Solar_percent, 
                        MD_Solar_amount = newdata.MD_Solar_amount, 
                        MD_Tier_I_percent = newdata.MD_Tier_I_percent,
                        MD_Tier_I_amount = newdata.MD_Tier_I_amount, 
                        MD_Tier_II_percent = newdata.MD_Tier_II_percent, 
                        MD_Tier_II_amount = newdata.MD_Tier_II_amount,
                        DC_Total_Cost_per_MWh_amount = newdata.DC_Total_Cost_per_MWh_amount,
                        DC_Solar_percent = newdata.DC_Solar_percent,
                        DC_Solar_amount = newdata.DC_Solar_amount,
                        DC_Tier_I_percent = newdata.DC_Tier_I_percent,
                        DC_Tier_I_amount = newdata.DC_Tier_I_amount,
                        DC_Tier_II_percent = newdata.DC_Tier_II_percent,
                        DC_Tier_II_amount = newdata.DC_Tier_II_amount,
                        DE_Total_Cost_per_MWh_amount = newdata.DE_Total_Cost_per_MWh_amount,
                        DE_Solar_percent = newdata.DE_Solar_percent, 
                        DE_Solar_amount = newdata.DE_Solar_amount,
                        DE_RECs_percent = newdata.DE_RECs_percent,
                        DE_REC_amount = newdata.DE_REC_amount, 
                        IL_Total_Cost_per_MWh_amount = newdata.IL_Total_Cost_per_MWh_amount,
                        IL_PER_o_load_covered_by_Supplier_vs_Utility_percent = newdata.IL_PER_o_load_covered_by_Supplier_vs_Utility_percent,
                        IL_Total_Standard_percent = newdata.IL_Total_Standard_percent,
                        IL_Solar_percent = newdata.IL_Solar_percent,
                        IL_Solar_amount = newdata.IL_Solar_amount,
                        IL_Wind_percent = newdata.IL_Wind_percent, 
                        IL_Wind_amount = newdata.IL_Wind_amount,
                        IL_ACP_percent = newdata.IL_ACP_percent,
                        IL_ACP_amount= newdata.IL_ACP_amount

                        from 
                            trueprice.{tmp_table_name} as newdata -- our csv data
                        where 
                            trueprice.{data.controlArea}_rec.strip = newdata.strip 
                            and trueprice.{data.controlArea}_rec.month = newdata.month 
                            and trueprice.{data.controlArea}_rec.curvestart=(select curvestart from single)
                    '''        
                

                    # finally execute the query
                    r = con.execute(backup_query)            
                    con.execute(f"drop table trueprice.{tmp_table_name}")
                return "Data Inserted"

            elif new_exists:
                return "Newer data in database, abort"
            else:
                return "Ingestion logic error, we should not be here"
        except:
            import traceback, sys
            print(traceback.format_exc())
            return traceback.format_exc()
            