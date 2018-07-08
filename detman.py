import sqlite3
import datetime
import time
import requests

import urllib.request  # библиотека HTTP
from lxml import html  # библиотека для обработки разметки xml и html, импортируем только для работы с html
import re  # осуществляет работу с регулярными выражениями
from bs4 import BeautifulSoup  # осуществляет синтаксический разбор документов HTML


BASE_URL = 'http://www.detkityumen.ru'
client = requests.session()
headers = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': BASE_URL
}

user_agent = {'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}





class detman:
    # осуществляет работу с HTTP-запросами сайта http://www.detkityumen.ru/
    conn = sqlite3.connect("detservice.db")
    name=""
    pw=""
    user_id = 0
    connected = False
    csrftoken = ""
    def login(self,name):
        #Выполняет логин на сайт
        print("начинаем коннект к сайту")
        self.name=name
        #self.conn1 = sqlite3.connect("detservice.db")  # или :memory: чтобы сохранить в RAM
        # Retrieve the CSRF token first
        client.get(BASE_URL)  # sets cookie

        if 'csrftoken' in client.cookies:
            # Django 1.6 and up
            self.csrftoken = client.cookies['csrftoken']
        else:
            # older versions
            self.csrftoken = client.cookies['csrf']
        print(self.csrftoken)
        self.get_user_pw(name)
        self.get_user_id(name)
        login_data = dict(csrfmiddlewaretoken=self.csrftoken, this_is_the_login_form=1, next='/profile/', username=self.name,
                          password=self.pw)
        headers['Referer'] = BASE_URL
        r = client.post(BASE_URL + "/login/", data=login_data, headers=headers)
        n = r.text.find(r'<a href="/logout/?next=/">')
        if n != -1:
            self.connected = True
        print(self.connected)
    def login_db(self):
        self.conn = sqlite3.connect("detservice.db")  # или :memory: чтобы сохранить в RAM
#Получить список тем
    def get_topics(self):
            print("Начинаем поиск тем")
            r = client.get(BASE_URL+r"/sp/?order_by=all&oz="+self.name+"&keyword=&keyword_area=all&pub_date=0&submit=Найти&stop_date=0")  # sets cookie
            str = html.fromstring(r.content)
            #преобразование документа к типу lxml.html.HtmlElement
            soup = BeautifulSoup(r.content, "lxml")
            for topic in soup.find_all("div", "b-actions__item_style_info_link"):
                tname = topic.find('a').contents[0];
                tref = topic.find('a').get('href')
                tid = tref.split("/")[3]
                self.add_topic(tid, tref, tname)
                #tref.split("/")[]
                print("№ {} Тема :{} ссылка: {}".format(tid,tname,tref))

            #result = str.xpath("//tr[@class='odd']/td[1]/text()")
    def add_order(self,tref):
        #добавляем заказ в закупку
        print("Получаем список товаров")
        r = client.get(BASE_URL +tref)
        soup = BeautifulSoup(r.content, "lxml")
        for good in soup.find_all("div", "b-sp-photo_item"):
            a = good.find('a', "popup-photo")
            form_url = a.get('form-url')
            print(form_url)
            tref = a.get('href')
            print(tref)

            if tref!=None and len(tref.split("/")) > 4:
                #сли ссылка на страницу с товаром а не на скрипт
                card_id=tref.split("/")[3]
                photo_id=tref.split("/")[5]
                b = good.find('div', "b-sp-photo_descr__title2 b-sp-photo_descr__title").find("b").contents[0]
                main_field_496445 = b.strip()
                b = good.find_all('div', "b-sp-photo_descr__title")[1].contents[0]
                main_field_496446 = b.strip().split(":")[1].strip()
                break

        login_data = dict(csrfmiddlewaretoken = self.csrftoken, main_field_496445 = main_field_496445,
                          main_field_496446 = main_field_496446, additional_field_496447 = 1,
                          additional_field_496448 = "", delivery_place = 3, photo_id = photo_id)
        headers["Referer"] = BASE_URL + tref
        r = client.get(BASE_URL + form_url, headers=headers)
        time.sleep(2)
        headers["Referer"] = BASE_URL + form_url
        r = client.post(BASE_URL + form_url, data
        =login_data,headers=headers)
        #n = r.text.find(r'<a href="/logout/?next=/">')

    def clear_topiс_bucket_arc(self, tref):
        #переносит отмененные заказы в архив
        print("Получаем список заказов")
        r = client.get(BASE_URL + tref)
        soup = BeautifulSoup(r.content, "lxml")
        headers["Referer"] = BASE_URL + tref
        for good in soup.find_all("div", "b-contain-delete"):
            a = good.find('a').get('url')
            client.get(BASE_URL + a, headers=headers)
            print(a)

    def clear_topiс_bucket(self, tref):
        print("Получаем список заказов")
        r = client.get(BASE_URL + tref)
        soup = BeautifulSoup(r.content, "lxml")
        headers["Referer"] = BASE_URL + tref
        for good in soup.find_all("tr", "b-contain-item"):
            #td=good.find('td')
            div=good.find_all('div','main-info')
            a=div[1].find('a','popup-html')
            if not a==None:
                ref=a.get('href')
                print(ref)

                headers["Referer"] = BASE_URL + tref
                r = client.get(BASE_URL + ref, headers=headers)
                time.sleep(1)
                form_data = dict(csrfmiddlewaretoken=self.csrftoken, state_comment="")
                r = client.post(BASE_URL + ref, data=form_data, headers=headers)
                form_data = dict(csrfmiddlewaretoken=self.csrftoken, state_comment="Ах какая жалость!!! :(")
                r = client.post(BASE_URL + ref, data=form_data, headers=headers)

    def reject_last_order(self, tref):
        #удаляем последний заказ в закупке
        print("Получаем список заказов")
        r = client.get(BASE_URL + tref)
        soup = BeautifulSoup(r.content, "lxml")
        headers["Referer"] = BASE_URL + tref
        for good in soup.find_all("tr", "b-contain-item"):
            # td=good.find('td')
            div = good.find_all('div', 'main-info')
            a = div[1].find('a', 'popup-html')
            if not a == None:
                ref = a.get('href')
                print(ref)

                headers["Referer"] = BASE_URL + tref
                r = client.get(BASE_URL + ref, headers=headers)
                time.sleep(1)
                form_data = dict(csrfmiddlewaretoken=self.csrftoken, state_comment="")
                r = client.post(BASE_URL + ref, data=form_data, headers=headers)
                form_data = dict(csrfmiddlewaretoken=self.csrftoken, state_comment="Ах какая жалость!!! :(")
                r = client.post(BASE_URL + ref, data=form_data, headers=headers)
                break


    def get_user_id(self,name):
        #получение id пользователя из базы
        cursor = self.conn.cursor()
        b="select id from users where upper(name)='{}'".format(name.upper())
        #b="select id from users where upper(name)='LENCHA'"
        #b="select * from sqlite_master where type = 'table'"
        cursor.execute(b)
        n=cursor.fetchone()[0]
        cursor.close()
        #print("найден пользователь в БД : {}".format(n))
        self.user_id = n
        return n


    def get_user_pw(self,name):
        #получение пароля пользователя из базы
        cursor = self.conn.cursor()
        b="select pw from users where upper(name)='{}'".format(name.upper())
        #b="select id from users where upper(name)='LENCHA'"
        #b="select * from sqlite_master where type = 'table'"
        cursor.execute(b)
        pw = cursor.fetchone()[0]
        cursor.close()
        #print("найден пользователь в БД : {}".format(pw))
        self.pw = pw
        return pw

    def add_topic(self, tid, tref, tname):
        #добавляет в таблицу тему
        cursor = self.conn.cursor()
        b = "select count(id) from topics where id={}".format(tid)
        r=cursor.execute(b)
        d=cursor.fetchone()
        if d[0] == 0:
            b = "insert into topics(id, name, ref, user_id) values({},'{}','{}','{}')".format(tid, tname, tref, self.user_id)
            cursor.execute(b)
            self.conn.commit()
        cursor.close()

    def set_topic_page(self,tid, page):
        #добавляет в таблицу тему
        cursor = self.conn.cursor()
        b = "update topics set page={} where id= {}".format(page, tid)
        #print(b+";")
        cursor.execute(b)
        self.conn.commit()
        cursor.close()

    def raise_topics(self):
        #conn1 = sqlite3.connect("detservice.db")  # или :memory: чтобы сохранить в RAM
        #проверяет необходимость поднятия тем и поднимает
        print("{} Запущено поднятие тем".format(datetime.datetime.now()))
        cursor = self.conn.cursor()
        cursor2 = self.conn.cursor()
        #select t.id,t.name from topics t where (strftime('%s','now')-t.last_up_time)/60>t.interval_minutes
        #select datetime(t.last_up_time, 'unixepoch', 'localtime') from topics t
        #select t.id,t.name, (strftime('%s','now')-t.last_up_time)/60 d  from topics t where t.active=1
        #select t.id,t.name,t.user_id from topics t where (strftime('%s','now')-t.last_up_time)/60>t.interval_minutes and t.active=1 and t.page>t.maxpage order by user_id
        b = """ select t.id,t.name,t.user_id, u.name 
                from topics t, users u  
                where u.id=t.user_id 
                and (strftime('%s','now')-t.last_up_time)/60>t.interval_minutes 
                and t.active=1 
                
                order by user_id"""
        #выбираем просроченные задания
        cursor.execute(b)
        for row in cursor.fetchall():
            if row[3].upper() != self.name.upper():
                self.login(row[3])
            self.add_order("/sp/igr/{}/photos/".format(row[0]))
            self.reject_last_order("/sp/bucket/{}/orders/".format(row[0]))
            self.clear_topiс_bucket_arc("/sp/bucket/{}/orders/".format(row[0]))
            b="update topics set last_up_time=strftime('%s','now') where id={}".format(row[0])
            print("{} UP {}".format(datetime.datetime.now(),row[1]))
            cursor2.execute(b)
            self.conn.commit()
        cursor.close()
        cursor2.close()

    def check_topics_position(self):
        cnn = sqlite3.connect("detservice.db")
        #проверяет место темы в выдаче
        print("Запущена проверка места темы в выдаче")
        pages=["http://www.detkityumen.ru/sp/list/1/"]
        headers["Referer"] = BASE_URL
        r = client.get(pages[0], headers=headers)
        soup = BeautifulSoup(r.content, "lxml")
        pager=soup.find('div', 'divPager')
        i=1
        for a in pager.find_all('a'):
            pages.append(BASE_URL+"/sp/list/1/"+a.get('href'))
            i+=1
            if i>3 : break;
            # нам нужны только первые пять страниц
        #список страниц для проверки позиции если закупки там нет то считаем что она на 99 странице
        cur = self.conn.cursor()
        b = "update topics set page=99"
        #поставили всем 99 страницу
        cur.execute(b)
        #cur.сlose()
        self.conn.commit()
        i=1
        for url in pages:
            r = client.get(url,headers=headers)
            #print("#Получаем список заказов {}".format(url))
            soup = BeautifulSoup(r.content, "lxml")
            for topic in soup.find_all('div', 'b-actions__item_style_info_link'):
                a = topic.find('a')
                if not a == None:
                    ref = a.get('href')
                    tid = ref.split("/")[3]
                    #print("#стр {} тема {}".format(tid,i))
                    self.set_topic_page(tid, i)
            i += 1







