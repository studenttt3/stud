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
import sklearn
from sklearn.linear_model import LinearRegression

bs = pd.read_csv("Bookshops.csv")
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

search0 = need['authors'][0:1].values[0]
list = search0.split(";")
aut = ""
ln = len(list)
for i in range(ln):
    if(i != ln - 1):
        aut = aut + list[i] + " and "
    else:
        aut = aut + list[i]
try:
    st.image(need['thumbnail'][0:1].values[0])
except:
    pass
st.markdown("This book was written by " + aut + ". You can learn more about him/her or them at this link" + need['wiki_url'][0:1].values[0])
url_pic = need['image_url'][0:1].values[0]
st.image(url_pic)
st.markdown("Also you can read description of this book below.")
st.markdown(need['description'][0:1].values[0])

pr = pd.read_csv("predict.csv")
pr.loc[(pr.type == "Kindle Edition"), 'type'] = 1
pr.loc[(pr.type == "Paperback"), 'type'] = 2
pr.loc[(pr.type == "Hardcover"), 'type'] = 3
pr.drop(labels = [11],axis = 0, inplace = True)
pr.drop(labels = [40],axis = 0, inplace = True)
pr.drop(labels = [33],axis = 0, inplace = True)
pr = pr.reset_index()
pr = pr[['type', 'rating', 'price']]
for i in range(len(pr.index)):
    pr.loc[i,'rating'] = pr['rating'][i:i+1].values[0][0:3]
pr['rating'] = pd.to_numeric(pr['rating'])
pr['price'] = pd.to_numeric(pr['price'])
pr = pr.astype({"type": "Int64"})

type_s = st.radio("", ('Электронная версия','Книга в мягкой обложке', 'Книга в твердой обложке'))
if(type_s == 'Электронная версия'):
    type_sel = 1
if(type_s == 'Книга в мягкой обложке'):
    type_sel = 2
if(type_s == 'Книга в твердой обложке'):
    type_sel = 3
opt = st.expander("", True)
rating_sel = need['average_rating'][0:1].values[0]
model = LinearRegression()
model.fit(pr.drop(columns=["price"]), pr["price"])
st.write(model.coef_[0] * type_sel + model.coef_[1] * rating_sel + model.intercept_)

st.write("Или можно узнать цену для любой другой книги с известным вам рейтингом")
type_s0 = st.radio("", ('Электронная версия','Книга в мягкой обложке', 'Книга в твердой обложке'))
if(type_s0 == 'Электронная версия'):
    type_sel0 = 1
if(type_s0 == 'Книга в мягкой обложке'):
    type_sel0 = 2
if(type_s0 == 'Книга в твердой обложке'):
    type_sel0 = 3
opt = st.expander("", True)
rating_sel0 = opt.slider("Рейтинг книги", min_value = 3.0, max_value = 5.0)
st.write(model.coef_[0] * type_sel0 + model.coef_[1] * rating_sel0 + model.intercept_)

which_bs = st.radio("", ('Наибольшая концентрация книжных магазинов','Наименьшая концентрация книжных магазинов'))
if(which_bs == "Наибольшая концентрация книжных магазинов"):
    bs1 = bs.sort_values(by =['Figure'])[-5:]
    fig, ax = plt.subplots(figsize=(16,10), dpi= 80)
    ax.vlines(x = bs1['City'], ymin = 0, ymax= bs1['Figure'], color='blue', alpha=0.7, linewidth=2)
    ax.scatter(x= bs1['City'], y = bs1['Figure'], s=75, color='blue', alpha=0.7)
    st.pyplot(fig)
if(which_bs == "Наименьшая концентрация книжных магазинов"):
    bs1 = bs.sort_values(by =['Figure'])[:5]
    fig, ax = plt.subplots(figsize=(16,10), dpi= 80)
    ax.vlines(x = bs1['City'], ymin = 0, ymax= bs1['Figure'], color='blue', alpha=0.7, linewidth=2)
    ax.scatter(x= bs1['City'], y = bs1['Figure'], s=75, color='blue', alpha=0.7)
    st.pyplot(fig)
    
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

