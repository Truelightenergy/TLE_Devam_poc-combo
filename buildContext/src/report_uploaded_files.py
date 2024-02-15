from utils.database_connection import ConnectDatabase
from utils.configs import read_config
import csv
from datetime import datetime

config = read_config()


if __name__=="__main__":

    data_base = ConnectDatabase()
    engine = data_base.get_engine()
    query = """
                SELECT 
                    UPPER(split_part(filename, '_', 1)) AS "File Type",
                    UPPER(REPLACE(filename, '_cob', '')) AS "File Name",
                    CASE
                        WHEN POSITION('COB' IN filename) > 0 THEN 'Y'
                        ELSE 'N'
                    END AS "COB(Y/N)"
                FROM 
                    trueprice.uploads u
                ORDER BY 
                    "File Type", "File Name";
            """
    
    results = engine.execute(query).fetchall()

    # Generate the CSV file name with the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"report_uploads_{timestamp}.csv"

    # Open a CSV file and write the results
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Optionally, write headers to the CSV file
        headers = ["File Type", "File Name", "COB(Y/N)"]
        writer.writerow(headers)
        
        # Write the data
        for row in results:
            writer.writerow(row)

    print(f"Report saved to {file_name}")


  
