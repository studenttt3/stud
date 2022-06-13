import pandas as pd
import numpy as np
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import json
import wikipedia
import requests
import sklearn
from sklearn.linear_model import LinearRegression
import re
import sqlite3
import networkx as nx

with st.echo(code_location='below'):
    st.header("Добро пожаловать, дорогой друг!")
    st.markdown("Пожалуйста, подождите некоторое время, подвисание может происходить из-за загрузки карт с многочисленными метками, но спустя несколько секунд всё будет работать исправно!Описание проекта по критериям вы можете найти в конце работы перед кодом.")
    st.markdown("Этот проект поможет вам выбрать книгу согласно вашим пожеланиям и узнать больше фактов о чтении в целом.")
    st.image("https://img.championat.com/s/735x490/news/big/m/a/kakie-knigi-chitat-v-doroge_1649771640842518832.jpg")
    st.markdown("Давайте подберем для вас книгу. Выберите желаемую категорию из выпадающего списка, затем установите диапазоны количества страниц и года издания книги.")
    
    ##Чтение всех нужных таблиц из csv-файлов
    bs = pd.read_csv("Bookshops.csv")
    books = pd.read_csv("books_edited.csv")
    books = books.astype({"num_pages": "Int64"})
    books = books.astype({"published_year": "Int64"})
    geo = pd.read_csv("geo.csv")
    stat = pd.read_csv("stat.csv")
    stat_1 = pd.read_csv("stat.csv")
    mos = pd.read_csv("Mos (1).csv")
    pr = pd.read_csv("predict.csv")
    good = pd.read_csv("good.csv")
    bad = pd.read_csv("bad.csv")
    
    ##Выбор пользователем категории, диапозонов количества страниц и года публикации и отбор 10 лучших книг с заданными параметрами
    cat = st.selectbox("Категория", books["categories"].value_counts().index)
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

    ##Выбор книги для получения подробной информации, вывод обложки книги, ссылки на страницу википедии об авторе, фото автора и описания книги.
    ##Обращение к таблице с добавленными ссылкой на страницу википедии об авторе и ссылкой на фото автора, созданной в отдельном файле в ipynb.
    ##Здесь использовалась библиотека wikipedia для поиска имен авторов в википедии и перехода по первому запросу на страницу со статьей об авторе.
    ##Далее использовался selenium для нахождения фотографии автора на странице и занесения в таблицу ссылки на нее.
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
    
    ##Здесь мы находим все слова в тексте описания с помощью регулярных выражений
    ##Использование регулярных выражений здесь оправдано, потому что недостаточно разделять строку пробелами, а знаки препинания (их много) могут идти сразу после букв.
    st.markdown("Если описание не пусто, давайте узнаем насколько полным и оригинальным  оно является.")
    try:
        analyze = need['description'][0:1].values[0]
        words = re.findall("[a-zA-Z]+", analyze)
        st.write("Длина описания - " + str(len(words)) + " слов.  Из них " + str(len(set(words))) + " слов являются уникальными.")
    except:
        pass

    ##Обработка таблицы, на основании которой будут выполняться предсказания цены с помощью линейной регрессии (машинное обучение).
    st.markdown("Теперь давайте узнаем примерную цену книги в рублях, выбрав предпочтительную для вас версию.")
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

    ##Выбор пользователем версии книги и предсказание цены.
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

    ##Предсказание цены с помощью линейной регрессии ля книги с любым другим рейтингом и любой версией.
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
    
    ##Выбор пользователем московской сети книжных магазинов, с помощью REST API нахождение географических координат по известному адресу.
    ##Здесь тоже есть регулярные выражения для преобразования адреса в таблице к виду, требуемому для запросов
    ##Затем рисование карты Москвы с расстановкой меток всех магазинов с подписями адресов при клике.
    st.markdown("Если предсказанная цена является приемлемой для вас, то вам пора отправиться за покупкой в книжный магазин. Выберите в выпадающем списке название магазина или сети магазинов, и вы увидите на карте все точки расположения интересующих вас магазинов. При наведении на метку, вы сможете увидеть адрес конкретного магазина")
    shop = st.selectbox("Название", mos['Name'].unique())
    need_1 = mos[lambda x: x["Name"] == shop]
    map3 = folium.Map(location=[55.7522, 37.6156], zoom_start = 10.485)
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
        folium.Marker(location = [lat, lon], popup = str(add)).add_to(map3)
    st_data3 = st_folium(map3, width = 750)

    ##Используются таблицы, полученные с помощью SQL в отдельном файле jupiter для рисования графиков, которые меняются в зависимости от выбора пользователя.
    ##Все соответствующие выбору пользователя города отмечаются на карте мира с подписями, появляющимися при клике мышкой.
    st.header("Интересные факты о чтении")
    st.image("https://thelighthouse.team/wp-content/uploads/sites/6/2020/07/derecho-y-literatura-2020-4-1.jpg")
    st.markdown("Как мы увидели, в Москве довольно много книжных магазинов в любых районах города, но везде ли покупка книги представляет собой настолько простой процесс? Мы будем рассматривать только крупные города разных стран мира и сравнивать такой показатель как количество книжных магазинов на 100 000 населения. Вы можете выбрать для просмотра города с наименьшей или наибольшей такой концентрацией. По вертикальной оси отложено количество книжных магазинов на 100 000 населения.")
    which_bs = st.radio("", ('Наибольшая концентрация книжных магазинов','Наименьшая концентрация книжных магазинов'))
    if(which_bs == "Наибольшая концентрация книжных магазинов"):
        fig, ax = plt.subplots(figsize=(16,10), dpi= 80)
        ax.vlines(x = good['City'], ymin = 0, ymax= good['Figure'], color='mediumseagreen', alpha=0.7, linewidth=2)
        ax.scatter(x= good['City'], y = good['Figure'], s=75, color='mediumseagreen', alpha=0.7)
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
        fig, ax = plt.subplots(figsize=(16,10), dpi= 80)
        ax.vlines(x = bad['City'], ymin = 0, ymax= bad['Figure'], color='mediumseagreen', alpha=0.7, linewidth=2)
        ax.scatter(x= bad['City'], y = bad['Figure'], s=75, color='mediumseagreen', alpha=0.7)
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
    
    ##Построение графа (сначала обработка данных таблицы)
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
    
    ##Построение коррелограмма с предшествующей обработкой таблицы.
    st.markdown("Люди используют для чтения разные ресурсы: печатные книги, аудиокниги, электронные книги, газеты и журналы. Давайте посмотрим как коррелирует тот факт, что человек читает какой-то один из этих видов изданий с тем фактом, что он читает также какой-то определенный друг вид изданий.")
    stat_1 = stat_1[['Read any printed books during last 12months?', 'Read any audiobooks during last 12months?', 'Read any e-books during last 12months?', 'Do you happen to read any daily news or newspapers?', 'Do you happen to read any magazines or journals?']]
    stat_1 = stat_1.rename(columns={'Read any printed books during last 12months?': 'Печатные'})
    stat_1 = stat_1.rename(columns={'Read any audiobooks during last 12months?': 'Аудиокниги'})
    stat_1 = stat_1.rename(columns={'Read any e-books during last 12months?': 'Электронные'})
    stat_1 = stat_1.rename(columns={'Do you happen to read any daily news or newspapers?': 'Газеты'})
    stat_1 = stat_1.rename(columns={'Do you happen to read any magazines or journals?': 'Журналы'})
    stat_1.loc[(stat_1['Печатные'] == 'Yes'), 'Печатные'] = '1'
    stat_1.loc[(stat_1['Печатные'] == 'No'), 'Печатные'] = '0'
    stat_1.loc[(stat_1['Аудиокниги'] == 'Yes'), 'Аудиокниги'] = '1'
    stat_1.loc[(stat_1['Аудиокниги'] == 'No'), 'Аудиокниги'] = '0'
    stat_1.loc[(stat_1['Электронные'] == 'Yes'), 'Электронные'] = '1'
    stat_1.loc[(stat_1['Электронные'] == 'No'), 'Электронные'] = '0'
    stat_1.loc[(stat_1['Газеты'] == 'Yes'), 'Газеты'] = '1'
    stat_1.loc[(stat_1['Газеты'] == 'No'), 'Газеты'] = '0'
    stat_1.loc[(stat_1['Журналы'] == 'Yes'), 'Журналы'] = '1'
    stat_1.loc[(stat_1['Журналы'] == 'No'), 'Журналы'] = '0'
    stat_1 = stat_1[((stat_1['Печатные'] == '1') | (stat_1['Печатные'] == '0')) & ((stat_1['Аудиокниги'] == '1') | (stat_1['Аудиокниги'] == '0'))& ((stat_1['Электронные'] == '1') | (stat_1['Электронные'] == '0'))& ((stat_1['Газеты'] == '1') | (stat_1['Газеты'] == '0'))& ((stat_1['Журналы'] == '1') | (stat_1['Журналы'] == '0'))]
    stat_1['Печатные'] = pd.to_numeric(stat_1['Печатные'])
    stat_1['Аудиокниги'] = pd.to_numeric(stat_1['Аудиокниги'])
    stat_1['Электронные'] = pd.to_numeric(stat_1['Электронные'])
    stat_1['Газеты'] = pd.to_numeric(stat_1['Газеты'])
    stat_1['Журналы'] = pd.to_numeric(stat_1['Журналы'])
    stat_1 = stat_1.dropna()
    fig = plt.figure(figsize = (10,8), dpi = 80)
    sns.heatmap(stat_1.corr(), xticklabels = stat_1.corr().columns, yticklabels = stat_1.corr().columns, cmap ='RdYlGn', center = 0, annot = True)
    plt.title('Коррелограмм', fontsize = 24)
    plt.xticks(fontsize = 10)
    plt.yticks(fontsize = 10)
    st.pyplot(fig)
    st.markdown("Мы можем заметить, например, что корреляции между чтением печатных книг и использованием аудиокниг очень близка к 0, как и корреляция между чтением печатных и электронных книг. Это значит, что многие люди не используют эти пары типов изданий как взаимозаменяемые, как мы могли ожидать.")
    st.header("Описание проекта по критериям:")
    st.subheader("Обработка данных с помощью pandas")
    st.markdown("Чтение из csv-файлов, сортировка по столбцу, удаление столбцов, обрезка строк, выбор строк с определенными значениями в определенных столбцах, вынимание значение из ячеек, изменение значений в ячейках при условиях, удаление строк, переиндексирование, изменение типов столбцов (в том числе to_numeric приведение к численному виду), изменение названий столбцов, удаление строк с NaN.")
    st.subheader("Веб-скреппинг")
    st.markdown("Осуществлялся в отдельно приложенном ipynb-файле, который называется webscrap.ipynb. Но для удобства я еще приложу код перед кодом основным кодом. Использовались библиотеки Wikipedia и Selenium. С помощью Wikipedia производим поиск по имени и фамилии автора в википедии и переходим по ссылке из первого запроса к нужной статье. C помощью Selenium находим на странице основное фото автора и заносим ссылку на изображение в нашу таблицу. (Если у какой-то книги было несколько авторов, операция проделывалась для всех авторов.)")
    st.subheader("Работа с REST API (XML/JSON)")
    st.markdown("Использовалось для нахождения географических координат книжных магазинов выбранной пользователем сети по заданным адресам магазинов.")
    st.subheader("Визуализация данных")
    st.markdown("2 карты, изменяющихся в зависимости от выборов пользователей с отметками и всплывающим при нажатии текстом, граф с цветными пронумерованными вершинами, гистограмма (2 штуки в зависимости от выбора пользователя), коррелограмм.")
    st.subheader("Математические возможности Python (содержательное использование numpy/scipy, SymPy и т.д. для решения математических задач)")
    st. markdown("Преобразования numpy-массива для создания матрицы смежности, по которой в дальнейшем строится двудольный граф.")
    st.subheader("Streamlit")
    st.markdown("Размещено на Streamlit.")
    st.subheader("SQL")
    st.markdown("Обработка таблицы, сортировка по значениям определенного столбца и получение двух новых из нее в отдельном приложенном ipynb-файле, который называется sql_data.ipynb. Но для удобства я еще приложу код перед кодом основным кодом.")
    st.subheader("Регулярные выражения")
    st.markdown("Использовались дважды. Первый раз для разделения описания книги на слова (это оправдано, т.к. недостаточно разделять строку используя пробел как разделитель, а перечислять всевозможные знаки препинания нецелесообразно). Второй раз для преобразования адресов книжных магазинов к нужному нам виду путем извлечения с помощью регулярных выражений нужных фрагментов строки (в этом случае обойтись без регулярных выражений реально, но регулярные выражения помогли существенно сократить код).")
    st.subheader("Работа с геоданными с помощью geopandas, shapely, folium и т.д.")
    st.markdown("Использовался folium. Первая карта – карта Москвы с отмеченными магазинами книжной сети, выбранной пользователем. При кликании на метку магазина всплывает его адрес. Метки поставлены по полученным из адреса с помощью REST API долготе и широте. Вторая карта – карта мира с отмеченными 5 городами, которые изменяются в зависимости от выбора пользователя. При кликании на метку появляется название города. Метки поставлены по взятым из таблицы широте и долготе.")
    st.subheader("Машинное обучение")
    st.markdown("Линейная регрессия для предсказания цены книги по ее рейтингу и версии (электронная версия/ мягкая обложка/ твердая обложка).")
    st.subheader("Работа с графами (библиотека networkx)")
    st.markdown("Построение двудольного графа по заданной матрице смежности, нумерация вершин и окрашивания вершин из разных долей в разные цвета.")
    st.subheader("Дополнительные технологии (библиотеки, не обсуждавшиеся в ходе курса — например, телеграм-боты, нейросети или ещё что-нибудь")
    st.markdown("Библиотека Wikipedia для поиска словосочетания в поисковой строке википедии и нахождения ссылки первого запроса в поиске.")
    st.subheader("Объём (осмысленных строк кода, не считая import)")
    st.markdown("Более 120 строк в основном файле (вместе с импортами и комментариями более 260) + около 40 строк в двух других приложенных файлах.")
    st.subheader("Целостность и общее впечатление судить не мне😊")
    st.header("Код из файла webscrap.ipynb:")
    
    st.markdown("import pandas as pd")
    st.markdown("import numpy as np")
    st.markdown("import wikipedia")
    st.markdown("import requests")
    st.markdown("books = pd.read_csv("books.csv")")
    st.markdown("from selenium import webdriver")
    st.markdown("from selenium.webdriver.common.keys import Keys")
    st.markdown("from selenium.webdriver.chrome.service import Service")
    st.markdown("from webdriver_manager.chrome import ChromeDriverManager")
    st.markdown("from selenium.webdriver.common.by import By")
    st.markdown("driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))")
    st.markdown("driver.get("https://www.google.com")")
    st.markdown("for j in range(len(books.index)):")
    st.markdown("url_img = """)
    st.markdown("url_wiki = """)
    st.markdown("search0 = books['authors'][j:(j+1)].values[0]")
    st.markdown("list = str(search0).split(";")")
    st.markdown("for i in list:")
    st.markdown("   try:")
    st.markdown("       search0 = wikipedia.search(i)[0]")
    st.markdown("       search0 = search0.replace(" ", "_")")
    st.markdown("       url = 'https://en.wikipedia.org/wiki/' + search0")
    st.markdown("       url_wiki = url_wiki + "\n" + url")
    st.markdown("       driver.get(url)")
    st.markdown("       check =  driver.find_elements_by_xpath('//td[@class="infobox-image"]')")
    st.markdown("       if(len(check) != 0):")
    st.markdown("           obj = check[0]")
    st.markdown("           try:")
    st.markdown("               picture_url = obj.find_element(By.TAG_NAME, "img").get_attribute("src")")
    st.markdown("               url_img = url_img + "\n" + picture_url")
    st.markdown("           except:")
    st.markdown("               pass")
    st.markdown("   except IndexError:")
    st.markdown("       print("not found")")
    st.markdown("books.loc[j,'wiki_url'] = url_wiki")
    st.markdown("books.loc[j,'image_url'] = url_img")
    st.markdown("print(j)")
    st.markdown("books.to_csv('books_with_urls.csv')")
    
    st.header("Код из файла sql_data.ipynb:")
    
    '''
    import sqlite3
    import pandas as pd
    import numpy as np
    conn = sqlite3.connect("database.sqlite")
    c = conn.cursor()
    df = pd.read_csv("Bookshops.csv")
    df.to_sql("bss", conn)
    bad = pd.read_sql(
    """
    SELECT City, Figure FROM bss
    ORDER BY  Figure
    LIMIT 5
    """,
    conn,
    )
    good = pd.read_sql(
    """
    SELECT City, Figure FROM bss
    ORDER BY  Figure DESC
    LIMIT 5
    """,
    conn,
    )
    bad.to_csv("bad.csv")
    good.to_csv("good.csv")
    '''

    
