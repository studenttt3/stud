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
##import selenium
##from selenium import webdriver
##from selenium.webdriver.common.keys import Keys
##from selenium.webdriver.common.by import By
##from selenium.webdriver.chrome.service import Service
##from webdriver_manager.chrome import ChromeDriverManager




books = pd.read_csv("books.csv")

cat = st.selectbox(
"Category", books["categories"].value_counts().index)
df_selection = books[lambda x: x["categories"] == cat]
df_selection =  df_selection.sort_values('average_rating', ascending = False)
df_selection = df_selection[['title', 'average_rating', 'authors', 'num_pages', 'published_year']]

optionals1 = st.expander("Выберите желаемый диапазон количества страниц", True)
page_min = optionals1.slider("Минимальное количество страниц", min_value=float(books['num_pages'].min()), max_value=float(books['num_pages'].max()))
page_max = optionals1.slider("Максимальное количество страниц", min_value=float(books['num_pages'].min()), max_value=float(books['num_pages'].max()))
if page_max < page_min:
    st.error("Минимальное количество страниц должно быть меньше максимального, иначе не получится найти ничего подходящего!")
else:
    df_selection = df_selection[(df_selection['num_pages'] <= page_max) & (page_min <= df_selection['num_pages'])]
    
optionals2 = st.expander("Выберите желаемый диапазон года публикации", True)
year_min = optionals2.slider("Минимальный год", min_value=float(books['published_year'].min()), max_value=float(books['published_year'].max()))
year_max = optionals2.slider("Максимальный год", min_value=float(books['published_year'].min()), max_value=float(books['published_year'].max()))
if year_max < year_min:
    st.error("Минимальный год публикации должен быть меньше максимального, иначе не получится найти ничего подходящего!")
else:
    df_selection = df_selection[(df_selection['published_year'] <= year_max) & (year_min <= df_selection['published_year'])]
df_selection[0:10]

search0 = df_selection['authors'][0:1].values[0]
list = search0.split(";")
search0 = list[0]
search0 = wikipedia.search(search0)[0]
st.write(search0)
search0 = search0.replace(" ", "_")
url = 'https://en.wikipedia.org/wiki/' + search0
r = requests.get(url)

##driver = webdriver.Chrome('/Users/godun/Downloads/chromedriver_win32 (1)/chromedriver')
##driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
##driver.get(url)
##player = driver.find_elements_by_xpath('//td[@class="infobox-image"]')
##obj = player[0]
##picture_url = obj.find_element(By.TAG_NAME, "img").get_attribute("src")
##st.write("https:"+ picture_url)

text = BeautifulSoup(r.text, 'html.parser')
for i in text("td"):
    if(class == "infobox-image"):
        for link in text("img"):
            a = link.get('src')
            if((a is None) == False):
                ans = a
                ind = 1
            if(ind == 1):
                break
        if(ans is None):
            st.write("К сожалению, фотография автора не найдена в википедии")
        else:
            st.write("https:"+ ans)

