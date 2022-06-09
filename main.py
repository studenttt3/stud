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

cat = st.selectbox(
"Category", books["categories"].value_counts().index)
df_selection = books[lambda x: x["Category"] == cat]
df_selection
