# query.py

# import pandas as pd 
import requests
import pandas as pd
from psqlconnection import psqlconnector

pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 300)
pd.set_option('display.width', 1000)


# filter parameters
params = params={
    'resource_id': '926fd08f-cc91-4828-af38-bd45de97f8c3', 
    'limit': 50000,
    'include_total': True
}

# source: https://data.ca.gov/dataset/covid-19-cases
url = 'https://data.ca.gov/api/3/action/datastore_search'
r = requests.get(url, params=params).json()

# Convert JSON to pandas Dataframe
df = pd.DataFrame(r['result']['records']).set_index(['_id'])

# Rearrange columns
county = df[['county', 'date', 'totalcountconfirmed', 'newcountconfirmed', 'totalcountdeaths', 'newcountdeaths']]

print(county)

import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey, inspect
import pandas as pd


engine = create_engine(psqlconnector)
connection = engine.raw_connection()

inspector = inspect(engine)

print(inspector.get_table_names())


def update_table(df,table_name):
	df.to_sql(table_name, engine, if_exists='replace')



update_table(county, 'county')

if __name__ == "__main__": 
	from new_clean import result, top_data, mortality_rate, pop_den, coords

	print(result)
	
	update_table(result, 'counties_aggregated')
	update_table(top_data, 'top_counties_aggregated')
	update_table(mortality_rate, 'mortality_rate_aggregated')
	update_table(pop_den, 'population_density_aggregated')
	update_table(coords, 'coords_aggregated')

connection.close()