from utils.database_connection import ConnectDatabase


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


