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
import re
import sqlite3
import networkx as nx
import scipy.sparse as sp

with st.echo(code_location='below'):
    st.header("Добро пожаловать, дорогой друг!")
    st.markdown("Этот проект поможет вам выбрать книгу согласно вашим пожеланиям и узнать больше фактов о чтении в целом.")
    st.image("https://img.championat.com/s/735x490/news/big/m/a/kakie-knigi-chitat-v-doroge_1649771640842518832.jpg")
    st.markdown("Давайте подберем для вас книгу. Выберите желаемую категорию из выпадающего списка, затем установите диапазоны количества страниц и года издания книги.")
    bs = pd.read_csv("Bookshops.csv")
    books = pd.read_csv("books_edited.csv")
    books = books.astype({"num_pages": "Int64"})
    books = books.astype({"published_year": "Int64"})
    geo = pd.read_csv("geo.csv")
    stat = pd.read_csv("stat.csv")
    stat_1 = pd.read_csv("stat.csv")
    mos = pd.read_csv("Mos (1).csv")

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
    st.markdown("Вот 10 лучших по рейтингу книг, соответсвующих вашему запросу.")
    df_demonstr[0:10]

    st.markdown("Выберите из них книгу, о которой хотите узнать подробнее.")
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
    st.markdown("Автор(ы) этой книги -  " + aut + ". Вы можете почитать об авторе/авторах, перейдя по ссылке: " + need['wiki_url'][0:1].values[0])
    url_pic = need['image_url'][0:1].values[0]
    try:
        st.image(url_pic)
    except:
        pass
    st.markdown("Ниже можно ознакомиться с описанием книги.")
    st.markdown(need['description'][0:1].values[0])
    st.markdown("Если описание не пусто, давайте узнаем насколько полным и оригинальным  оно является.")
    try:
        analyze = need['description'][0:1].values[0]
        words = re.findall("[a-zA-Z]+", analyze)
        st.write("Длина описания - " + str(len(words)) + " слов.  Из них " + str(len(set(words))) + " слов являются уникальными.")
    except:
        pass

    st.markdown("Теперь давайте узнаем примерную цену книги в рублях, выбрав предпочтительную для вас версию.")
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
    st.write("Предсказанная цена составляет " + str(round(model.coef_[0] * type_sel + model.coef_[1] * rating_sel + model.intercept_, 2)) + " рублей.")

    st.write("Также вы можете предсказать цену любой другой книги с конкретным рейтингом в желаемой версии.")
    type_s0 = st.radio("Версия", ('Электронная версия','Книга в мягкой обложке', 'Книга в твердой обложке'))
    if(type_s0 == 'Электронная версия'):
        type_sel0 = 1
    if(type_s0 == 'Книга в мягкой обложке'):
        type_sel0 = 2
    if(type_s0 == 'Книга в твердой обложке'):
        type_sel0 = 3
    opt = st.expander("", True)
    rating_sel0 = opt.slider("Рейтинг книги", min_value = 3.0, max_value = 5.0)
    st.write("Предсказанная цена составляет " + str(round(model.coef_[0] * type_sel0 + model.coef_[1] * rating_sel0 + model.intercept_, 2)) + " рублей.")

    st.header("Интересные факты о чтении")
    st.image("https://thelighthouse.team/wp-content/uploads/sites/6/2020/07/derecho-y-literatura-2020-4-1.jpg")
    st.markdown("Проживая в Москве, мы привыкли, что книгу можно купить в любом районе города, но везде ли покупка книги представляет собой настолько простой процесс? Мы будем рассматривать только крупные города разных стран мира и сравнивать такой показатель как количество книжных магазинов на 100 000 населения. Вы можете выбрать для просмотра города с наименьшей или наибольшей такой концентрацией.")
    which_bs = st.radio("", ('Наибольшая концентрация книжных магазинов','Наименьшая концентрация книжных магазинов'))
    if(which_bs == "Наибольшая концентрация книжных магазинов"):
        bs1 = bs.sort_values(by =['Figure'])[-5:]
        fig, ax = plt.subplots(figsize=(16,10), dpi= 80)
        ax.vlines(x = bs1['City'], ymin = 0, ymax= bs1['Figure'], color='mediumseagreen', alpha=0.7, linewidth=2)
        ax.scatter(x= bs1['City'], y = bs1['Figure'], s=75, color='mediumseagreen', alpha=0.7)
        st.pyplot(fig)
        st.markdown("А теперь посмотрим где располагаются города, в которых покупка книги занимает наименьшее количество затруднений, на карте мира (при нажатии на метку на вашем экране появится название города).")
        map1 = folium.Map(location=[0, 0], zoom_start = 1)
        geo1 = geo[0:5]
        lat1 = geo1['lat'] 
        lon1 = geo1['lon']
        city1 = geo1['City']
        for lat1, lon1, city1 in zip(lat1, lon1, city1): 
            folium.Marker(location=[lat1, lon1], popup = str(city1)).add_to(map1)
        st_data1 = st_folium(map1, width = 750)
    
    if(which_bs == "Наименьшая концентрация книжных магазинов"):
        bs1 = bs.sort_values(by =['Figure'])[:5]
        fig, ax = plt.subplots(figsize=(16,10), dpi= 80)
        ax.vlines(x = bs1['City'], ymin = 0, ymax= bs1['Figure'], color='mediumseagreen', alpha=0.7, linewidth=2)
        ax.scatter(x= bs1['City'], y = bs1['Figure'], s=75, color='mediumseagreen', alpha=0.7)
        st.pyplot(fig)
        st.markdown("А теперь посмотрим где располагаются города, в которых покупка книги занимает наибольшее количество затруднений, на карте мира (при нажатии на метку на вашем экране появится название города).")
        map2 = folium.Map(location=[0, 0], zoom_start = 1)
        geo2 = geo[5:10]
        lat2 = geo2['lat'] 
        lon2 = geo2['lon']
        city2 = geo2['City']
        for lat2, lon2, city2 in zip(lat2, lon2, city2): 
            folium.Marker(location = [lat2, lon2], popup = str(city2)).add_to(map2)
        st_data2 = st_folium(map2, width = 750)

    st.markdown("А сейчас самое время узнать как связаны уровень образования человека с количеством прочитанных им книг за год. Для этого будем использовать данные опроса. Представим полученные результаты наглядно с помощью двудольного графа, где зеленые вершины - уровни образования, а персиковые - диапазоны количества прочитанных книг.")
    stat = stat[['Education', 'How many books did you read during last 12months?']]
    stat = stat.rename(columns={'How many books did you read during last 12months?': 'number'})
    stat.loc[(stat.Education == "High school incomplete"), 'Education'] = 1
    stat.loc[(stat.Education == "High school graduate"), 'Education'] = 2
    stat.loc[(stat.Education == "Some college, no 4-year degree"), 'Education'] = 3
    stat.loc[(stat.Education == "College graduate"), 'Education'] = 4
    stat.loc[(stat.number <= 10), 'number'] = 1
    stat.loc[(stat.number > 10) & (stat.number <= 50), 'number'] = 2
    stat.loc[(stat.number > 50), 'number'] = 3
    Matrix = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ])
    for i in range(len(stat.index)):
        Matrix[stat['Education'][i:i+1].values[0] - 1][stat['number'][i:i+1].values[0] + 3] = 1
        Matrix[stat['number'][i:i+1].values[0] + 3][stat['Education'][i:i+1].values[0] - 1] = 1

    G = nx.Graph()
    H = nx.path_graph(Matrix.shape[0]) 
    G.add_nodes_from(H)
    for i in range(Matrix.shape[0]):
        for j in range(Matrix.shape[1]):
            if(Matrix[i][j] == 1):
                G.add_edge(i, j)
    colors = ['mediumseagreen', 'mediumseagreen', 'mediumseagreen', 'mediumseagreen', 'darksalmon', 'darksalmon', 'darksalmon']
    fig, ax = plt.subplots()
    pos = nx.bipartite_layout(G, [0, 1, 2, 3])
    nx.draw(G,pos, with_labels=True, node_color=colors)
    st.pyplot(fig)
    st.markdown("Более подробно о номерах вершин:")
    st.markdown("0 - не окончил школу,  1 - окончил школу,  2 - не окончил высшее образование,  3 - высшее образование")
    st.markdown("4 - не более 10 книг в год,  5 - от 10 до 50 книг в год,  6 - более 50 книг в год")
    st.markdown("Получаем интересный результат, что никто из людей из нашей выборки, не окончивших школу, не читал более 50 книг в год (отсутствует соответствующее ребро). А также никто из людей с высшим образованием не читал менее 10 книг в год.")
    
    shop = st.selectbox("Название", mos['Name'].unique())
    need_1 = mos[lambda x: x["Name"] == shop]
    for i in range(len(need_1.index)):
        ad = mos['Address'][i:i + 1].values[0]
        street = re.split("[,]", ad)[1]
        house = re.findall("[\d]+", ad)
        add = "Москва," + street + ", " + house[0]
        entrypoint = "https://nominatim.openstreetmap.org/search"
        params = {'q': add,
          'format': 'json'}
        r = requests.get(entrypoint, params=params)
        data = r.json()
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        st.write(lat, lon)
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
            ##st.write("https:"+  ans)

