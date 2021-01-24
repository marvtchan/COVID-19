# coronavirus.py
import pandas as pd
import numpy as np
from numpy import median, average
import seaborn as sns
import matplotlib.pyplot as plt

import sqlite3  
from sqlalchemy import create_engine, select, MetaData, Table, Integer, String, inspect, Column, ForeignKey
import os

pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 300)
pd.set_option('display.width', 1000)
import altair as alt

# SOURCE:  https://data.ca.gov/dataset/covid-19-cases

cali = pd.read_csv('statewide_cases.csv')  
pop = pd.read_csv('county_pop.csv')

pop = pop.rename(columns={'County': 'county', "Population": "population"})

cali_numbers = cali[['date','county','newcountconfirmed', 'newcountdeaths']]

top_10 = cali_numbers.groupby(['county'], as_index=False).sum().sort_values(['newcountconfirmed', 'newcountdeaths'], ascending=False)
top = top_10.nlargest(10, "newcountconfirmed")
top = top[['county']]

cali_numbers.groupby(['county','date'], as_index=False).sum().sort_values(['newcountconfirmed', 'newcountdeaths'], ascending=False)
cali_total = cali_numbers.melt(id_vars=["county","date"], var_name="Type", value_name="Value")
cali_total['date'] = pd.to_datetime(cali_total['date'])
cali_total['Value'] = cali_total['Value'].astype(float)

cali_top_10 = cali_total[cali_total['county'].isin(top['county'])]

la_ala = cali_top_10[cali_top_10['county'].isin(['Alameda', 'Los Angeles'])]
la_ala['county'] =  la_ala['county'] + ' County'
la_ala = la_ala.merge(pop, how='left', on=['county'])
la_ala['per_capita'] = la_ala['Value'] / la_ala['population'] * 100000
la_ala['SMA_7'] = 0
alameda_case = la_ala[(la_ala['Type'] == 'newcountconfirmed') & (la_ala['county'] == 'Alameda County')]
alameda_death = la_ala[(la_ala['Type'] == 'newcountdeaths') & (la_ala['county'] == 'Alameda County')]
la_case = la_ala[(la_ala['Type'] == 'newcountconfirmed') & (la_ala['county'] == 'Los Angeles County')]
la_death = la_ala[(la_ala['Type'] == 'newcountdeaths') & (la_ala['county'] == 'Los Angeles County')]

alameda_death_percent = alameda_case.merge(alameda_death, on='date')
alameda_death_percent['death_percent'] = alameda_death_percent['SMA_7_y'] / alameda_death_percent['SMA_7_x'] 
la_death_percent = la_case.merge(la_death, on='date')
la_death_percent['death_percent'] = la_death_percent['SMA_7_y'] / la_death_percent['SMA_7_x']
death = [la_death_percent, alameda_death_percent]
death_percent = pd.concat(death)

def simple_moving_ave(df):
	# This is a function to add a column for 7 day moving average 

    for i in range (0, df.shape[0]-6):
        df.loc[df.index[i+6],'SMA_7'] = np.round(((df.iloc[i,5] + df.iloc[i+1,5] + df.iloc[i+2,5] + df.iloc[i+3,5] + df.iloc[i+4,5] + df.iloc[i+5,5] + df.iloc[i+6,5])/7),5)
    return df
    
sma = [simple_moving_ave(alameda_case), simple_moving_ave(alameda_death), simple_moving_ave(la_case), simple_moving_ave(la_death)]
       
result = pd.concat(sma)

# Create a selection that chooses the nearest point & selects based on x-value
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['date'], empty='none')

line = alt.Chart(result).mark_line(point=True).encode(
    x = alt.X('date', axis = alt.Axis(title = 'date'.upper(), format = ("%b %Y"), tickMinStep = 2, labelAngle=0)),
    y=alt.Y('per_capita', axis = alt.Axis(title='Value')),
    color='county',
    strokeDash='Type'
)# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = alt.Chart(result).mark_point().encode(
    x='date',
    opacity=alt.value(0),
).add_selection(
    nearest
)

# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'per_capita', alt.value(' '))
)

# Draw a rule at the location of the selection
rules = alt.Chart(result).mark_rule(color='gray').encode(
    x='date'
).transform_filter(
    nearest
)

# Put the five layers into a chart and bind the data
alt.layer(
    line, selectors, points, rules, text
).properties(
    width=900,
    height=600
).configure_axis(
    labelFontSize=20,
    titleFontSize=20,
).configure_legend(
    titleFontSize=10,
    labelFontSize=15,
).interactive()


alt.data_transformers.disable_max_rows()
# Create a selection that chooses the nearest point & selects based on x-value
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['date'], empty='none')

line = alt.Chart(result, title="7-Day Moving Average LA vs Alameda COVID-19").mark_line(point=True).encode(
    x = alt.X('date:T', axis = alt.Axis(title = 'date'.upper(), format = ("%b %Y"), tickMinStep = 2, labelAngle=0)),
    y=alt.Y('SMA_7', axis = alt.Axis(title='Per 100,000 Population')),
    color='county',
    strokeDash='Type',
)# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = alt.Chart(result).mark_point().encode(
    x='date:T',
    opacity=alt.value(0),
).add_selection(
    nearest
)

# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'SMA_7', alt.value(' '))
)

# Draw a rule at the location of the selection
rules = alt.Chart(result).mark_rule(color='gray').encode(
    x='date'
).transform_filter(
    nearest
)

# Put the five layers into a chart and bind the data
alt.layer(
    line, selectors, points, rules, text
).properties(
    width=900,
    height=600
).configure_axis(
    labelFontSize=20,
    titleFontSize=20,
).configure_legend(
    titleFontSize=10,
    labelFontSize=15,
).configure_title(fontSize=24).interactive()