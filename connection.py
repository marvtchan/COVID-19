# connection.py
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey, inspect
import pandas as pd
from psqlconnection import DATABASE_URL
pd.set_option('display.max_columns', 300)
pd.set_option('display.width', 1000)


# engine = create_engine('postgresql://marvinchan:shadow8@localhost:5432/covid')
engine = create_engine(DATABASE_URL)
connection = engine.raw_connection()

inspector = inspect(engine)

print(inspector.get_table_names())

county = pd.read_sql_query('SELECT * FROM county', connection)

pop_den = pd.read_sql_query('SELECT * FROM population_density_aggregated', connection)

result = pd.read_sql_query('SELECT * FROM counties_aggregated', connection)

top_data = pd.read_sql_query('SELECT * FROM top_counties_aggregated', connection)

mortality_rate = pd.read_sql_query('SELECT * FROM mortality_rate_aggregated', connection)

coords = pd.read_sql_query('SELECT * FROM coords_aggregated', connection)

print(coords)

connection.close()