# data_clean.py

import pandas as pd
import numpy as np
from numpy import median, average
import seaborn as sns
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 300)
pd.set_option('display.width', 1000)
import altair as alt
from connection import county

# This class provides functions that can be used to clean, organize, and prepare COVID data for analysis
# Data is pulled with API from government websites
class COVID:
	def __init__(self, df):
		self.df = df
		self.pop = pd.read_csv('county_pop.csv')
		self.pop = self.pop.rename(columns={'County': 'county', "Population": "population"})

	def top_10(self):
		# This function groups California counties by county and sorta by counts confirmed for a top 10 list.

		cali_numbers = self.df[['date','county','newcountconfirmed', 'newcountdeaths']]
		top_10 = cali_numbers.groupby(['county'], as_index=False).sum().sort_values(['newcountconfirmed', 'newcountdeaths'], ascending=False)
		top = top_10.nlargest(10, "newcountconfirmed")
		top = top[['county']]
		return top

	def convert(self, top):
		# This function converts the table from columns to rows using the df.melt method.
		# Pass the dataframe and top country names for a filtered version of the table with top countries

		self.df.groupby(['county','date'], as_index=False).sum().sort_values(['newcountconfirmed', 'newcountdeaths'], ascending=False)
		total = self.df.melt(id_vars=["county","date"], var_name="Type", value_name="Value")
		total['date'] = pd.to_datetime(total['date'])
		total['Value'] = total['Value'].astype(float)
		top_total = total[total['county'].isin(top['county'])]
		return total, top_total
		

	def compare(self, top_total, counties):
		# This function filters counties, adds population, and finds the 7 day moving average for comparison.
		# Pass only 2 counties
		# Should compare a county to LA since LA is the highest
		comparison_df = top_total[top_total['county'].isin(counties)]
		comparison_df['county'] =  comparison_df['county'] + ' County'
		comparison_df = comparison_df.merge(self.pop, how='left', on=['county'])
		comparison_df['per_capita'] = comparison_df['Value'] / comparison_df['population'] * 100000
		comparison_df['pop_density'] = comparison_df['population'] / comparison_df['Square_Miles']
		comparison_df['SMA_7'] = 0
		return comparison_df

	def simple_moving_ave(self, df):
		# Calculate 7-day moving average 
		df = df.sort_values(by='date')
		for i in range (0, df.shape[0]-6):
			df.loc[df.index[i+6],'SMA_7'] = np.round(((df.iloc[i,6] + df.iloc[i+1,6] + df.iloc[i+2,6] + df.iloc[i+3,6] + df.iloc[i+4,6] + df.iloc[i+5,6] + df.iloc[i+6,6])/7),6)
		return df


	def split(self, comparison_df, county):
		# Split comparison_df by county & type
		county_case = comparison_df[(comparison_df['Type'] == 'newcountconfirmed') & (comparison_df['county'] == county)]
		county_death = comparison_df[(comparison_df['Type'] == 'newcountdeaths') & (comparison_df['county'] == county)]
		county_case = self.simple_moving_ave(county_case)
		county_death = self.simple_moving_ave(county_death)
		sma = [county_case, county_death]
		result =pd.concat(sma)
		return result, county_case, county_death


	def mortality_rate(self, county_one_case, county_one_death, county_two_case, county_two_death):
		# Calculate Mortality Rates for 7 day moving average
		county_one_death_percent = county_one_case.merge(county_one_death, on='date')
		county_one_death_percent['death_percent'] = county_one_death_percent['SMA_7_y'] / county_one_death_percent['SMA_7_x'] 
		county_two_death_percent = county_two_case.merge(la_death, on='date')
		county_two_death_percent['death_percent'] = county_two_death_percent['SMA_7_y'] / county_two_death_percent['SMA_7_x']
		death = [county_one_death_percent, county_two_death_percent]
		death_percent = pd.concat(death)

		return death_percent

	def population_density(self, result):
		result['per_density'] = (result['SMA_7'] / result['pop_density']) * 100
		return result



# pop = pd.read_csv('county_pop.csv')

# pop = pop.rename(columns={'County': 'county', "Population": "population"})

top = COVID(county).top_10()
# print(top)
converted, top_converted = COVID(county).convert(top)
# print (converted)

top_counties =top['county'].to_list()

counties = ['Alameda', 'Los Angeles']
comparison = COVID(county).compare(converted, counties)
print(comparison)
alameda,  alameda_case, alameda_death = COVID(county).split(comparison, 'Alameda County')
la, la_case, la_death = COVID(county).split(comparison, 'Los Angeles County')

result = pd.concat([alameda, la])

mortality_rate = COVID(county).mortality_rate(alameda_case, alameda_death, la_case, la_death)

pop_den = COVID(county).population_density(result)

top_comparison = COVID(county).compare(converted, top_counties)

print(type(result))

appended_data = []

for area in top_counties:
	county_sma = COVID(county).split(top_comparison, area + ' County')[0]
	print(type(county_sma))
	appended_data.append(county_sma)
	print(type(appended_data))

top_data = pd.concat(appended_data)
print(top_data)




	       
# result = pd.concat(sma)
# print(result)
