import pandas as pd
from utils.database_connection import ConnectDatabase

class BaseTableHierarchy():
    def __init__(self, ):
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def get_hierarchy_id_csv(self, fileName):
        df = pd.read_csv(fileName, header=None)

        df_info = df.iloc[1:12]
        df_info = df_info.dropna(axis = 1, how = 'all')
        df_info = df_info.dropna(axis = 0, how = 'all')
        df_info.reset_index(inplace=True, drop=True)
        df_info = df_info.transpose()
        df_info.columns = df_info.iloc[0]
        df_info = df_info.drop(df_info.index[0])
        df_info.reset_index(inplace=True, drop=True)

        if df_info.isnull().values.any():
            raise Exception("File Format Not Matched")
        
        self.get_hierarchy_id(df_info)

    def get_hierarchy_id(self, df):
        hierarchy = {}
        # curve_datatype = "select name from trueprice.curve_datatype;"
        control_area = "select name from trueprice.control_area;"
        state = "select name from trueprice.state;"
        load_zone = "select name from trueprice.load_zone;"
        capacity_zone = "select name from trueprice.capacity_zone;"
        utility = "select name from trueprice.utility;"
        block_type = "select name from trueprice.block_type;"
        cost_group = "select name from trueprice.cost_group;"
        cost_component = "select name from trueprice.cost_component;"
        customer_type = "select name from trueprice.customer_type;"

        temp_df = pd.read_sql(control_area, self.engine)
        values_list = set(df.loc[~df['Control Area'].isin(list(temp_df['name']))]['Control Area'])
        if len(values_list)>0:
            hierarchy["control_area"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.control_area (name) VALUES {values_str};"
                con.execute(query)
        
        temp_df = pd.read_sql(state, self.engine)
        values_list = set(df.loc[~df['State'].isin(list(temp_df['name']))]['State'])
        if len(values_list)>0:
            hierarchy["state"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.state (name) VALUES {values_str};"
                con.execute(query)
        
        temp_df = pd.read_sql(load_zone, self.engine)
        values_list = set(df.loc[~df['Load Zone'].isin(list(temp_df['name']))]['Load Zone'])
        if len(values_list)>0:
            hierarchy["load_zone"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.load_zone (name) VALUES {values_str};"
                con.execute(query)
        
        temp_df = pd.read_sql(capacity_zone, self.engine)
        values_list = set(df.loc[~df['Capacity Zone'].isin(list(temp_df['name']))]['Capacity Zone'])
        if len(values_list)>0:
            hierarchy["capacity_zone"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.capacity_zone (name) VALUES {values_str};"
                con.execute(query)
        
        temp_df = pd.read_sql(utility, self.engine)
        values_list = set(df.loc[~df['Utility'].isin(list(temp_df['name']))]['Utility'])
        if len(values_list)>0:
            hierarchy["utility"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.utility (name) VALUES {values_str};"
                con.execute(query)
        
        temp_df = pd.read_sql(block_type, self.engine)
        values_list = set(df.loc[~df['Block Type'].isin(list(temp_df['name']))]['Block Type'])
        if len(values_list)>0:
            hierarchy["block_type"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.block_type (name) VALUES {values_str};"
                con.execute(query)
        
        temp_df = pd.read_sql(cost_group, self.engine)
        values_list = set(df.loc[~df['Cost Group'].isin(list(temp_df['name']))]['Cost Group'])
        if len(values_list)>0:
            hierarchy["cost_group"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.cost_group (name) VALUES {values_str};"
                con.execute(query)
        
        temp_df = pd.read_sql(cost_component, self.engine)
        values_list = set(df.loc[~df['Cost Component'].isin(list(temp_df['name']))]['Cost Component'])
        if len(values_list)>0:
            hierarchy["cost_component"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.cost_component (name) VALUES {values_str};"
                con.execute(query)
        
        temp_df = pd.read_sql(customer_type, self.engine)
        values_list = set(df.loc[~df['Customer Type'].isin(list(temp_df['name']))]['Customer Type'])
        if len(values_list)>0:
            hierarchy["customer_type"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.customer_type (name) VALUES {values_str};"
                con.execute(query)
        
        if len(hierarchy)>0:
            pass
        
        return None