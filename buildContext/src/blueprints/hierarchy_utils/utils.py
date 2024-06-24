import pandas as pd
from utils.database_connection import ConnectDatabase

class BaseTableHierarchy():
    def __init__(self, ):
        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()
        self.hierarchy_id_to_csv_id = {
            'curve_datatype': 'curve_datatype',
            'control_area': 'Control Area',
            'state': 'State',
            'load_zone': 'Load Zone',
            'capacity_zone': 'Capacity Zone',
            'utility': 'Utility',
            'block_type': 'Block Type',
            'cost_group': 'Cost Group',
            'cost_component': 'Cost Component',
            'customer_type': 'Customer Type'
        }

    def get_hierarchy_id_csv(self, fileName, curveType):
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
        
        hierarchy_id_frame = self.get_hierarchy_id(df_info, curveType)
        
        return hierarchy_id_frame

    def get_hierarchy_id(self, df, curveType):
        df['curve_datatype'] = curveType
        hierarchy = {}
        mapping_dfs = {}
        curve_datatype = "select id, name from trueprice.curve_datatype;"
        control_area = "select id, name from trueprice.control_area;"
        state = "select id, name from trueprice.state;"
        load_zone = "select id, name from trueprice.load_zone;"
        capacity_zone = "select id, name from trueprice.capacity_zone;"
        utility = "select id, name from trueprice.utility;"
        block_type = "select id, name from trueprice.block_type;"
        cost_group = "select id, name from trueprice.cost_group;"
        cost_component = "select id, name from trueprice.cost_component;"
        customer_type = "select id, name from trueprice.customer_type;"
        hierarchy_table = "select * from trueprice.hierarchy"

        curve_datatype = pd.read_sql(curve_datatype, self.engine)
        if curveType not in list(curve_datatype['name']):
            hierarchy["curve_datatype"] = [curveType]
            values_str = f"('{curveType}')"
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.curve_datatype (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                curve_datatype = pd.concat([curve_datatype, temp_df])
        mapping_dfs['curve_datatype'] = curve_datatype

        control_area = pd.read_sql(control_area, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['control_area']].isin(list(control_area['name']))][self.hierarchy_id_to_csv_id['control_area']])
        if len(values_list)>0:
            hierarchy["control_area"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.control_area (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                control_area = pd.concat([control_area, temp_df])
        mapping_dfs['control_area'] = control_area

        state = pd.read_sql(state, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['state']].isin(list(state['name']))][self.hierarchy_id_to_csv_id['state']])
        if len(values_list)>0:
            hierarchy["state"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.state (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                state = pd.concat([state, temp_df])
        mapping_dfs['state'] = state

        load_zone = pd.read_sql(load_zone, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['load_zone']].isin(list(load_zone['name']))][self.hierarchy_id_to_csv_id['load_zone']])
        if len(values_list)>0:
            hierarchy["load_zone"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.load_zone (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                load_zone = pd.concat([load_zone, temp_df])
        mapping_dfs['load_zone'] = load_zone

        capacity_zone = pd.read_sql(capacity_zone, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['capacity_zone']].isin(list(capacity_zone['name']))][self.hierarchy_id_to_csv_id['capacity_zone']])
        if len(values_list)>0:
            hierarchy["capacity_zone"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.capacity_zone (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                capacity_zone = pd.concat([capacity_zone, temp_df])
        mapping_dfs['capacity_zone'] = capacity_zone

        utility = pd.read_sql(utility, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['utility']].isin(list(utility['name']))][self.hierarchy_id_to_csv_id['utility']])
        if len(values_list)>0:
            hierarchy["utility"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.utility (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                utility = pd.concat([utility, temp_df])
        mapping_dfs['utility'] = utility

        block_type = pd.read_sql(block_type, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['block_type']].isin(list(block_type['name']))][self.hierarchy_id_to_csv_id['block_type']])
        if len(values_list)>0:
            hierarchy["block_type"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.block_type (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                block_type = pd.concat([block_type, temp_df])
        mapping_dfs['block_type'] = block_type

        cost_group = pd.read_sql(cost_group, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['cost_group']].isin(list(cost_group['name']))][self.hierarchy_id_to_csv_id['cost_group']])
        if len(values_list)>0:
            hierarchy["cost_group"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.cost_group (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                cost_group = pd.concat([cost_group, temp_df])
        mapping_dfs['cost_group'] = cost_group

        cost_component = pd.read_sql(cost_component, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['cost_component']].isin(list(cost_component['name']))][self.hierarchy_id_to_csv_id['cost_component']])
        if len(values_list)>0:
            hierarchy["cost_component"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.cost_component (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                cost_component = pd.concat([cost_component, temp_df])
        mapping_dfs['cost_component'] = cost_component

        customer_type = pd.read_sql(customer_type, self.engine)
        values_list = set(df.loc[~df[self.hierarchy_id_to_csv_id['customer_type']].isin(list(customer_type['name']))][self.hierarchy_id_to_csv_id['customer_type']])
        if len(values_list)>0:
            hierarchy["customer_type"] = values_list
            values_str = ", ".join(f"('{value}')" for value in values_list)
            with self.engine.connect() as con:
                query = f"INSERT INTO trueprice.customer_type (name) VALUES {values_str} RETURNING id, name;"
                result = con.execute(query)
                temp_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                customer_type = pd.concat([customer_type, temp_df])
        mapping_dfs['customer_type'] = customer_type

        if len(hierarchy)>0:
            # Create a filter condition
            condition = pd.Series([False] * len(df))

            for col, values in hierarchy.items():
                condition |= df[self.hierarchy_id_to_csv_id[col]].isin(values)
            distinct_df = df[condition]
            distinct_df = distinct_df[list(self.hierarchy_id_to_csv_id.values())].drop_duplicates()
            distinct_df.columns = list(self.hierarchy_id_to_csv_id.keys())
            distinct_df = self.replace_strings_with_ids(distinct_df, mapping_dfs, )
            distinct_df.to_sql(f"hierarchy", con = self.engine, if_exists = 'append', chunksize=1000, schema="trueprice", index=False)
        df = df[list(self.hierarchy_id_to_csv_id.values())]
        df.columns = list(self.hierarchy_id_to_csv_id.keys())
        main_df = self.replace_strings_with_ids(df, mapping_dfs, )
        hierarchy_table_df = pd.read_sql(hierarchy_table, self.engine)
        main_df = main_df.merge(hierarchy_table_df, on=list(main_df.columns), how='left')
        return main_df[['id']]
    
    def replace_strings_with_ids(self, main_df, mapping_dfs):
        for column in mapping_dfs.keys():
            # Get the corresponding mapping DataFrame
            mapping_df = mapping_dfs[column]
            # Merge main_df with the mapping_df
            main_df = main_df.merge(mapping_df.rename(columns={'name': column, 'id': f'{column}_id'}), on=column, how='left')
            # Drop the original string column
            main_df.drop(column, axis=1, inplace=True)
        return main_df