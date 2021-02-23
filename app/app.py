from datetime import date
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import data
url = "http://ftp.berlinonline.de/lageso/corona/csv/bezirkstabelle.csv"
df = pd.read_csv(url,sep=';',encoding='latin-1')
df = df.rename(columns={"Bezirk":"District","Fallzahl":"Number of cases","Differenz":"Difference","Inzidenz":"Incidence","Genesen":"Recovery"})

# Create a table
st.markdown("<h2 style='text-align: center; color: black;'>COVID-19 Cases in Berlin</h2>", unsafe_allow_html=True)
st.dataframe(data=df, width=1000, height=500)
st.write("Last Updated:",date.today().strftime('%Y-%m-%d'),", 12pm")
st.text("Number of cases: Total number of cases.\nDifference: Today's cases minus(-) previous day's cases.\nIncidence: Cases per 100,000 people since the beginning of the pandemic.\nRecovery: Estimated number of recovered lab-confirmed cases, according to Robert Koch Institute definition.\n")

# Create select box
st.markdown("<h2 style='text-align: center; color: black;'>Cases by District</h2>", unsafe_allow_html=True)
District_list = list(df['District'])
x_axis = st.selectbox('Select District',District_list,index=District_list.index('Berlin'))

# Import data
url2 = "http://ftp.berlinonline.de/lageso/corona/csv/meldedatum_bezirk.csv"
df2 = pd.read_csv(url2,sep=';')
df2 = df2.rename(columns={'Datum': 'Date'})
df2 = df2.rename({'Neukoelln': 'Neukölln', 'Tempelhof-Schoeneberg': 'Tempelhof-Schöneberg', 'Treptow-Koepenick':'Treptow-Köpenick'}, axis=1)
df2['Berlin'] = df2.sum(axis=1)

# Create a bor chart
fig = px.bar(x=df2['Date'], y=df2[x_axis],labels=dict(x=x_axis, y="Cases"))
fig.update_layout(width=1000, height=500)
fig.update_layout(template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# Creat pie charts
st.markdown("<h2 style='text-align: center; color: black;'>Cases by Age Group</h2>", unsafe_allow_html=True)
url1 = "http://ftp.berlinonline.de/lageso/corona/csv/alterstabelle.csv"
df1 = pd.read_csv(url1,sep=';',encoding='latin-1')
df1 = df1.rename(columns={'Altersgruppe': 'Age group',"Fallzahl":"Number of cases","Differenz":"Difference"})
df1 = df1.drop([13,14])
df1['Age group'] = df1['Age group']+' years'
age_list = list(df1['Age group'])
fig1 = make_subplots(rows=1, cols=2,specs=[[{'type':'domain'}, {'type':'domain'}]],subplot_titles=['Total cases', "Today's cases"])
fig1.add_trace(go.Pie(labels=age_list, values=df1['Number of cases']),1, 1)
fig1.add_trace(go.Pie(labels=age_list, values=df1['Difference']),1, 2)
fig1.update_traces(textposition='inside', textinfo='label',hoverinfo="value+percent")
fig1.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
fig1.update_layout(showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

# Create a dataframe for map
map_data = pd.DataFrame([["Charlottenburg-Wilmersdorf",52.5053,13.2600],
["Friedrichshain-Kreuzberg",52.4996,13.4314],
["Lichtenberg",52.5336, 13.4999],["Marzahn-Hellersdorf",52.5229,13.5766],
["Mitte",52.531677, 13.381777],["Neukölln",52.4408,13.4445],
["Pankow",52.5929,13.4317],["Spandau",52.5352,13.2003],["Steglitz-Zehlendorf",52.4309,13.1927],
["Tempelhof-Schöneberg",52.4722,13.3703],["Treptow-Köpenick",52.4204,13.6200],
["Reinickendorf",52.5790,13.2805]],columns=['District','lat', 'lon'])
df_map = df[['District','Difference']]
df_map1 = pd.merge(map_data, df_map, on='District')

# Creata map
st.markdown("<h2 style='text-align: center; color: black;'>Current Hot Spots</h2>", unsafe_allow_html=True)
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v10',
    initial_view_state=pdk.ViewState(
        latitude=52.5,
        longitude=13.38,
        zoom=9.3,
        pitch=20,
    ),
    layers=[
        pdk.Layer(
            'HeatmapLayer',
            data=df_map1,
            get_position=['lon','lat'],
            get_weight="Difference",
            opacity=0.5,
            cell_size_pixels=15,
            elevation_scale=10,
            elevation_range=[-50, 300]
        )
    ],
))
st.text("Colors represent the difference between today's cases and previous day's cases.")
