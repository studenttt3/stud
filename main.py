import pandas as pd
import numpy as np
import seaborn as sns
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from pywaffle import Waffle
import folium
from streamlit_folium import st_folium
import json
from geopandas.tools import geocode
import wikipedia
from bs4 import BeautifulSoup
import requests

books = pd.read_csv("books.csv")

cat = st.selectbox(
"Category", books["categories"].value_counts().index)
df_selection = books[lambda x: x["categories"] == cat]
df_selection =  df_selection.sort_values('average_rating', ascending = False)
df_selection = df_selection[['title', 'average_rating', 'authors', 'num_pages', 'published_year']]

page = st.columns(2)
page_min = page[0].number_input("Minimum number of pages", value = books['num_pages'].min())
page_max = page[1].number_input("Maximum number of pages", value = books['num_pages'].max())
if page_max < page_min:
    st.error("The maximum number of page can't be smaller than the minimum number of pages!")
else:
    df_selection = df_selection[(df_selection['num_pages'] <= page_max) & (page_min <= df_selection['num_pages'])]
    
year = st.columns(2)
year_min = year[0].number_input("Minimum year", value = books['published_year'].min())
year_max = year[1].number_input("Maximum year", value = books['published_year'].max())
if year_max < year_min:
    st.error("The maximum year can't be smaller than the minimum year!")
else:
    df_selection = df_selection[(df_selection['published_year'] <= year_max) & (year_min <= df_selection['published_year'])]
df_selection[0:10]


st.write(df_selection['authors'][0])
