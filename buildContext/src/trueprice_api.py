from flask import Flask
import trueprice_database as tpdb

app = Flask(__name__)

@app.route("/")
def hello_world():
    df = tpdb.get_all_data()
    print(df)
    return f"<p>Hello, World!</p>{df}"