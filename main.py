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

books = pd.read_csv("books.csv")
books = books.astype({'num_pages': np.int})

cat = st.selectbox(
"Category", books["categories"].value_counts().index)
df_selection = books[lambda x: x["categories"] == cat]
df_selection =  df_selection.sort_values('average_rating', ascending = False)
df_selection = df_selection[['title', 'average_rating', 'num_pages', 'published_year']]
df_selection[0:10]
