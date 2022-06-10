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




books = pd.read_csv("books_edited.csv")
books = books.astype({"num_pages": "Int64"})
books = books.astype({"published_year": "Int64"})

cat = st.selectbox(
"Категория", books["categories"].value_counts().index)
df_selection = books[lambda x: x["categories"] == cat]
df_selection =  df_selection.sort_values('average_rating', ascending = False)

optionals1 = st.expander("Выберите желаемый диапазон количества страниц", True)
page_min = optionals1.slider("Минимальное количество страниц", min_value = int(books['num_pages'].min()), max_value = int(books['num_pages'].max()))
page_max = optionals1.slider("Максимальное количество страниц", min_value = int(books['num_pages'].min()), max_value = int(books['num_pages'].max()), value = int(books['num_pages'].max()))
if page_max < page_min:
    st.error("Минимальное количество страниц должно быть меньше максимального, иначе не получится найти ничего подходящего!")
else:
    df_selection = df_selection[(df_selection['num_pages'] <= page_max) & (page_min <= df_selection['num_pages'])]
    
year = st.columns(2)
year_min = year[0].number_input("Минимальный год", value = books['published_year'].min())
year_max = year[1].number_input("Максимальный год", value = books['published_year'].max())
if year_max < year_min:
    st.error("Минимальный год публикации должен быть меньше максимального, иначе не получится найти ничего подходящего!")
else:
    df_selection = df_selection[(df_selection['published_year'] <= year_max) & (year_min <= df_selection['published_year'])]
df_demonstr = df_selection[['title', 'authors', 'average_rating',  'num_pages', 'published_year']]
df_demonstr[0:10]

name_book = st.selectbox("Название книги", df_selection[0:10]['title'].unique())
need = df_selection[lambda x: x["title"] == name_book]
st.write(need)


search0 = need['authors'][0:1].values[0]
list = search0.split(";")
aut = ""
ln = len(list)
for i in range(ln):
    if(i != ln):
        aut = aut + list[i] + " and"
    else:
        aut = aut + list[i]
st.markdown("This book was written by" + aut)

##driver = webdriver.Chrome('/Users/godun/Downloads/chromedriver_win32 (1)/chromedriver')
##driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
##driver.get(url)
##player = driver.find_elements_by_xpath('//td[@class="infobox-image"]')
##obj = player[0]
##picture_url = obj.find_element(By.TAG_NAME, "img").get_attribute("src")
##st.write("https:"+ picture_url)

##text = BeautifulSoup(r.text, 'html.parser')
##for i in text("td"):
    ##if(class == "infobox-image"):
        ##for link in text("img"):
            ##a = link.get('src')
            ##if((a is None) == False):
                ##ans = a
                ##ind = 1
            ##if(ind == 1):
                ##break
        ##if(ans is None):
            ##st.write("К сожалению, фотография автора не найдена в википедии")
        ##else:
            ##st.write("https:"+ ans)

