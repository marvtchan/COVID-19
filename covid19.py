# apartment_streamlit.py
# streamlit
import streamlit as st
from streamlit import caching

#database

import os
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey, inspect
import pandas as pd

#datetime
import datetime as dt
from datetime import datetime
from datetime import timedelta
import dateutil.relativedelta
from dateutil.relativedelta import relativedelta

#analysis and visualization
import pandas as pd
import numpy as np
from numpy import median, average
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import pydeck as pdk
import altair as alt
alt.data_transformers.disable_max_rows()
from data_visualization import comparison_chart, mortality_chart, pop_density_chart, comparison_chart_all, density_relationship



def main():
	### Allows user to switch between pages ###
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Analysis", "Visualize Map"])

    if page == "Homepage":
        st.title("COVID-19 in California Counties")
        st.markdown(
        """
   			This is an exploratory page analyzing COVID-19 in California.
            In the "Analysis" page counties are normalized by population, population density, and can be filtered to compare against one another.
        """)
        st.markdown(
        """
            The data presented is sourced from :https://data.ca.gov/dataset/covid-19-cases & https://covid-19.acgov.org/index.page. 
        """)
        st.markdown(
        """
      
        """)
        st.subheader("Analyze")
        st.markdown(
        """
        We can analyze the COVID-19 data on the 'Analysis' page.
        """)
        st.subheader("Top 10 Counties")
        top_data = load_data()[3]
        data = load_data()[0]

        display_top = top_data[['county', 'date', 'Type', 'Value']]

        display_top['Running Totals'] = display_top.groupby(['county', 'Type'])['Value'].apply(lambda x: x.cumsum())
        display_top = display_top.nlargest(20,'date').sort_values(by=['Type', 'Value'], ascending=False)
        display_top['Daily Value'] = display_top['Value']

        display_top = display_top.pivot_table(index=['county', 'date'], columns='Type', values=['Daily Value', 'Running Totals'], aggfunc=np.sum)
        display_top = display_top.sort_values(('Running Totals', 'newcountconfirmed'), ascending=False)

        st.table(display_top)
        if st.checkbox("Display total data", False):
            st.subheader("Raw Data")
            st.write(data)
        st.subheader("Visualize")
        st.markdown(
        """
        Proceed to the Visualize Map page to filter for confirmed cases by zip codes.
        """)
        st.markdown(
        """
        Below is a map of all confirmed cases in Alameda County:
        """)
        # df = load_data()

        st.sidebar.text(" ")
        st.sidebar.text(" ")
        st.sidebar.text(" ")
        st.sidebar.success('Explore the datasets with the \'Analysis\' page or visualize the listing with the \'Visualize Map\' page.')
    elif page == "Analysis":
        # data = load_data()
        st.title("📈Analysis📉")
        st.markdown(
        """
        The analysis below shows time-series analysis of COVID-19 cases and deaths.

        Analysis:

           1. Alameda County vs Los Angeles County 

           Los Angeles County is the #1 hot spot in California. The data displayed is normalized per capita on a 7-day moving average.
        
        """)

        data, pop_den, result, top_data, mortality_rate = load_data()

        start_date, end_date, today = get_dates()

        filtered_result = filter_data(result, start_date, end_date)


        comparison_chart(filtered_result, 'date:T', 'SMA_7', 'county', 'Type', "7-Day Moving Average, Alameda County vs LA County COVID-19")
        

        st.markdown(
        """
           2. Alameda County vs Los Angeles County COVID-19 Density

        """)

        pop_density_chart(filtered_result, 'date:T', 'per_density', 'county', 'Type')

        st.markdown(
        """
           Below we can see the relationship between population density and total confirmed cases of COVID-19 by County.

        """)
        
        density = relationships(data, pop_den)

        density_relationship(density, 'pop_density', 'totalcountdeaths')

 
        if st.checkbox("Display total data", False, key=result):
            st.subheader("Raw Data")
            st.write(result)

        st.markdown(
        """
           3. Alameda County vs Los Angeles County Mortality Rate

        """)

        filtered_mortality_rate = filter_data(mortality_rate, start_date, end_date)

        mortality_chart(filtered_mortality_rate, 'date:T', 'death_percent', 'county')

        st.markdown(
        """
           4. Top 10 Absolute Confirmed Cases Normalzied Per Capita

        """)

        comparison_chart_all(top_data, 'date:T', 'SMA_7', 'county', 'Type', "7-Day Moving Average, Top 10 California Counties COVID-19")


        if st.checkbox("Display total data", False, key=data):
            st.subheader("Raw Data")
            st.write(county)

    elif page == "Visualize Map":
        df = load_data()
        st.title("COVID-19 Cases & Deaths in Alameda County")
        st.markdown(
        """
        We can visualize COVID-19 on a map here.

        """)



# Load Data from database
@st.cache(persist=True, allow_output_mutation=True)
def load_data():
    engine = create_engine('postgresql://marvinchan:shadow8@localhost:5432/covid', echo=False)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    data = pd.read_sql_query('SELECT * FROM county', connection)
    data['county'] = data['county'] + ' County'
    pop_den = pd.read_sql_query('SELECT * FROM population_density_aggregated', connection)
    result = pd.read_sql_query('SELECT * FROM counties_aggregated', connection)
    top_data = pd.read_sql_query('SELECT * FROM top_counties_aggregated', connection)
    mortality_rate = pd.read_sql_query('SELECT * FROM mortality_rate_aggregated', connection)
    return data, pop_den, result, top_data, mortality_rate


#Function for dates
def get_dates():
    today = datetime.today()
    first = today.replace(day=1)
    start = first
    end = first + relativedelta(day=31)
    start_date = st.sidebar.date_input('Start Date', dt.date(2020,3,18))
    end_date = st.sidebar.date_input('End Date', today)
    if start_date < end_date:
        st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')
    return start_date, end_date, today


# Filter data with location
def filter_data(data, start_date, end_date):
    filtered = data[
    (data['date'].dt.date >= start_date) & (data['date'].dt.date <= (end_date))
    ]
    location = st.multiselect("Enter Location", sorted(data['county'].unique()), default=["Los Angeles County", "Alameda County"], key=data)
    filtered = filtered[filtered['county'].isin(location)]
    return filtered
  
def relationships(data, pop_den):
    density = data
    density = pd.merge(density, pop_den[['county', 'pop_density']], on='county', how='left').drop_duplicates('_id').reset_index()
    density = density[['county', 'date', 'totalcountconfirmed', 'totalcountdeaths', 'pop_density']]
    density['date'] = pd.to_datetime(density['date'])
    density = density[density['date'] == density['date'].max()]
    return density

if __name__ == "__main__":
    main()
