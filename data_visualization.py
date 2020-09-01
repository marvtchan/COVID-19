# data_visualization.py

import pandas as pd
import numpy as np
from numpy import median, average
import seaborn as sns
import matplotlib.pyplot as plt

import streamlit as st

from data_clean import result

import sqlite3  
from sqlalchemy import create_engine, select, MetaData, Table, Integer, String, inspect, Column, ForeignKey
import os

pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 300)
pd.set_option('display.width', 1000)
import altair as alt
alt.renderers.enable('altair_viewer')


def comparison_chart(df, x_value, y_value, color_value, stroke_value, title_value):
    alt.data_transformers.disable_max_rows()
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')


    line = alt.Chart(df, title=title_value).mark_line(point=True).encode(
        x = alt.X(x_value, axis = alt.Axis(title = 'date'.upper(), format = ("%b %Y"), tickMinStep = 2, labelAngle=90)),
        y=alt.Y(y_value, axis = alt.Axis(title='Per 100,000 Population')),
        color=color_value,
        strokeDash=stroke_value
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(df).mark_point().encode(
        x=x_value,
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
        text=alt.condition(nearest, y_value, alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x=x_value
    ).transform_filter(
        nearest
    )



    # Put the five layers into a chart and bind the data
    chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=1200,
        height=600,
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20,
    ).configure_legend(
        titleFontSize=10,
        labelFontSize=15,
    ).configure_title(fontSize=24).interactive()
    st.altair_chart(chart)



def comparison_chart_all(df, x_value, y_value, color_value, stroke_value, title_value):
    alt.data_transformers.disable_max_rows()
    # # Create a selection that chooses the nearest point & selects based on x-value
    # nearest = alt.selection(type='single', nearest=True, on='mouseover',
    #                         fields=['date'], empty='none')


    # line = alt.Chart(df, title=title_value).mark_line(point=True).encode(
    #     x = alt.X(x_value, axis = alt.Axis(title = 'date'.upper(), format = ("%b %Y"), tickMinStep = 2, labelAngle=0)),
    #     y=alt.Y(y_value, axis = alt.Axis(title='Per 100,000 Population')),
    #     color=color_value,
    #     strokeDash=stroke_value
    # )


    # # Transparent selectors across the chart. This is what tells us
    # # the x-value of the cursor
    # selectors = alt.Chart(df).mark_point().encode(
    #     x=x_value,
    #     opacity=alt.value(0),
    # ).add_selection(
    #     nearest
    # )

    # # Draw points on the line, and highlight based on selection
    # points = line.mark_point().encode(
    #     opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    # )

    # # Draw text labels near the points, and highlight based on selection
    # text = line.mark_text(align='left', dx=5, dy=-5).encode(
    #     text=alt.condition(nearest, y_value, alt.value(' '))
    # )

    # # Draw a rule at the location of the selection
    # rules = alt.Chart(df).mark_rule(color='gray').encode(
    #     x=x_value
    # ).transform_filter(
    #     nearest
    # )

    highlight = alt.selection(type='single', on='mouseover', 
        fields=['county'], nearest=True)
    
    base = alt.Chart(df, title=title_value).encode(
        x=alt.X(x_value, axis=alt.Axis(title="Date", labelAngle=90)),
        y=alt.Y(y_value, axis=alt.Axis(title="Per Capita * 100,000")),
        color=color_value,
        strokeDash=stroke_value,
        tooltip=color_value
    )

    points = base.mark_circle().encode(
       opacity=alt.value(0)
    ).add_selection(
        highlight
    )

    lines = base.mark_line().encode(
        size=alt.condition(~highlight, alt.value(1), alt.value(3))
    )


    # Bottom panel is a bar chart of weather type
    bars = alt.Chart(df).mark_bar().encode(
       x='population',
       y=y_value,
       color=color_value,
    )

    # Put the five layers into a chart and bind the data
    chart = alt.layer(
        points, lines
    ).properties(
        width=1200,
        height=600,
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20,
    ).configure_legend(
        titleFontSize=10,
        labelFontSize=15,
    ).configure_title(fontSize=24).interactive()
    st.altair_chart(chart)


def mortality_chart(df, x_value, y_value, color_value):
    alt.data_transformers.disable_max_rows()
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    line = alt.Chart(df, title="Mortality Rate, 7-Day Moving Average LA vs Alameda COVID-19").mark_line(point=True).encode(
        x = alt.X(x_value, axis = alt.Axis(title = 'date'.upper(), format = ("%b %Y"), tickMinStep = 2, labelAngle=0)),
        y=alt.Y(y_value, axis = alt.Axis(title='Deaths / Confirmed Cases')),
        color=color_value,
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(df).mark_point().encode(
        x=x_value,
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
        text=alt.condition(nearest, y_value, alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x=x_value
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

def pop_density_chart(df, x_value, y_value, color_value, stroke_value):
    alt.data_transformers.disable_max_rows()
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['date'], empty='none')

    line = alt.Chart(df, title="Case & Death Per Density, 7-Day Moving Average LA vs Alameda COVID-19").mark_line(point=True).encode(
        x = alt.X(x_value, axis = alt.Axis(title = 'date'.upper(), format = ("%b %Y"), tickMinStep = 2, labelAngle=90)),
        y=alt.Y(y_value, axis = alt.Axis(title='Per Capita / Population Density * 100')),
        color=color_value,
        strokeDash=stroke_value,
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(df).mark_point().encode(
        x=x_value,
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
        text=alt.condition(nearest, y_value, alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(df).mark_rule(color='gray').encode(
        x=x_value
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


