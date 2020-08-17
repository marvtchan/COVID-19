# apartment_streamlit.py
# streamlit
import streamlit as st
from streamlit import caching

#database
from query import county
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

from data_clean import result, mortality_rate, pop_den


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

        comparison_chart()

        st.markdown(
        """
           2. Alameda County vs Los Angeles County Mortality Rate

        """)

        mortality_chart()

        st.markdown(
        """
           3. Alameda County vs Los Angeles County Per Population Density

        """)
        
        pop_density_chart()


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
    (data['Date'] >= start_date) & (data['Date'].dt.date <= (end_date))
    ]
    location = st.multiselect("Enter Location", sorted(data['city'].unique()))
    bedroom = st.multiselect("Enter Bedrooms", sorted(data['bedrooms'].unique()))
    selected_filtered_data = filtered[(filtered['city'].isin(location))&(filtered['bedrooms'].isin(bedroom))]
    return selected_filtered_data, location, bedroom
  
def comparison_chart():
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
    chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=1200,
        height=600,
        autosize=alt.AutoSizeParams(
        type='fit',
        contains='padding'
    )
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20,
    ).configure_legend(
        titleFontSize=10,
        labelFontSize=15,
    ).configure_title(fontSize=24).interactive()
    st.altair_chart(chart)


def mortality_chart():
    alt.data_transformers.disable_max_rows()
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    line = alt.Chart(mortality_rate, title="Mortality Rate, 7-Day Moving Average LA vs Alameda COVID-19").mark_line(point=True).encode(
        x = alt.X('date:T', axis = alt.Axis(title = 'date'.upper(), format = ("%b %Y"), tickMinStep = 2, labelAngle=0)),
        y=alt.Y('death_percent', axis = alt.Axis(title='Deaths / Confirmed Cases')),
        color='county_x',
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(mortality_rate).mark_point().encode(
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
        text=alt.condition(nearest, 'death_percent', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(mortality_rate).mark_rule(color='gray').encode(
        x='date'
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=1200,
        height=600
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20,
    ).configure_legend(
        titleFontSize=10,
        labelFontSize=15,
    ).configure_title(fontSize=24).interactive()
    st.altair_chart(chart)

def pop_density_chart():
    alt.data_transformers.disable_max_rows()
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    line = alt.Chart(pop_den, title="Case & Death Per Density, 7-Day Moving Average LA vs Alameda COVID-19").mark_line(point=True).encode(
        x = alt.X('date:T', axis = alt.Axis(title = 'date'.upper(), format = ("%b %Y"), tickMinStep = 2, labelAngle=0)),
        y=alt.Y('per_density', axis = alt.Axis(title='Per Capita / Population Density * 100')),
        color='county',
        strokeDash='Type',
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(pop_den).mark_point().encode(
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
        text=alt.condition(nearest, 'per_density', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(pop_den).mark_rule(color='gray').encode(
        x='date'
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=1200,
        height=600
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20,
    ).configure_legend(
        titleFontSize=10,
        labelFontSize=15,
    ).configure_title(fontSize=24).interactive()
    st.altair_chart(chart)

if __name__ == "__main__":
    main()
