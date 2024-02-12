from utils.database_connection import ConnectDatabase
from sqlalchemy import text

class Rules:
    """
    Managing Database operations
    """

    def __init__(self):
        """
        connection database here 
        """

        data_base = ConnectDatabase()
        self.engine = data_base.get_engine()

    def filter_data(self, table, email):
        """
        filter the data based on the user's subscription
        """

        try:
            query = f"SELECT * from trueprice.column_authorization where email = '{email}' AND control_table = '{table}';"
            results = self.engine.execute(query).fetchall()
            return results
        except:
            return None
        
    def fetch_module_rules(self, table, email):
        """
        filter the data based on the user's subscription
        """

        try:
            query = f"SELECT * from trueprice.column_authorization where email = '{email}' AND control_table LIKE '%{table}%';"
            results = self.engine.execute(text(query)).fetchall()
            return results
        except:
            return None
        
    def check_admin_privileges(self, email):
        """
        check admin rights
        """
        flag = False
        try:
            query = f"SELECT * from trueprice.users where email = '{email}';"
            results = self.engine.execute(text(query)).fetchall()
            for row in results:
                if (row["privileged_level"] != 'read_only_user') and (row['status']=='enabled'):
                    flag = True
                    break
            return flag
        except:
            return flag



