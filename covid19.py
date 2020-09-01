# apartment_streamlit.py
# streamlit
import streamlit as st
from streamlit import caching

#database
from connection import county
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
from data_visualization import comparison_chart, mortality_chart, pop_density_chart, comparison_chart_all

from data_clean import result, mortality_rate, pop_den, top_data


def main():
	### Allows user to switch between pages ###
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Analysis", "Visualize Map"])

    if page == "Homepage":
        st.title("COVID-19 in Alameda County")
        st.markdown(
        """
   			This is an exploratory page for searching an COVID-19 in the Bay Area.
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

        comparison_chart(result, 'date:T', 'SMA_7', 'county', 'Type', "7-Day Moving Average, Alameda County vs LA County COVID-19")

        comparison_chart_all(top_data, 'date:T', 'SMA_7', 'county', 'Type', "7-Day Moving Average, California Counties COVID-19")

        st.markdown(
        """
           2. Alameda County vs Los Angeles County Mortality Rate

        """)

        mortality_chart(mortality_rate, 'date:T', 'death_percent', 'county_x')

        st.markdown(
        """
           3. Alameda County vs Los Angeles County Per Population Density

        """)
        
        pop_density_chart(pop_den, 'date:T', 'per_density', 'county', 'Type')


        if st.checkbox("Display total data", False):
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
@st.cache(persist=True)
def load_data():
    engine = create_engine('postgresql://marvinchan:shadow8@localhost:5432/covid', echo=False)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    data = pd.read_sql_query('SELECT * FROM county', connection)
    return data


#Function for dates
def get_dates():
    today = datetime.today()
    first = today.replace(day=1)
    start = first
    end = first + relativedelta(day=31)
    start_date = st.sidebar.date_input('Listing Created Date Range Start', start)
    end_date = st.sidebar.date_input('End', end)
    if start_date < end_date:
        st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')
    return start_date, end_date  


# Filter data with location
def filter_data(data, start_date, end_date):
    filtered = data[
    (data['Date'].dt.date  >= start_date) & (data['Date'].dt.date <= (end_date))
    ]
    location = st.multiselect("Enter Location", sorted(data['city'].unique()))
    bedroom = st.multiselect("Enter Bedrooms", sorted(data['bedrooms'].unique()))
    selected_filtered_data = filtered[(filtered['city'].isin(location))&(filtered['bedrooms'].isin(bedroom))]
    return selected_filtered_data, location, bedroom
  


if __name__ == "__main__":
    main()
