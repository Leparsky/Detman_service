import sqlite3
import datetime
import time
import requests

import urllib.request  # библиотека HTTP
from lxml import html  # библиотека для обработки разметки xml и html, импортируем только для работы с html
import re  # осуществляет работу с регулярными выражениями
from bs4 import BeautifulSoup  # осуществляет синтаксический разбор документов HTML

def get_user(login, password):
    return 222823


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
    def login(self,name,password=""):
        #Выполняет логин на сайт
        print("начинаем коннект к сайту {}".format(name))

        #self.conn1 = sqlite3.connect("detservice.db")  # или :memory: чтобы сохранить в RAM
        # Retrieve the CSRF token first
        client.get(BASE_URL+"/logout")  # sets cookie

        if 'csrftoken' in client.cookies:
            # Django 1.6 and up
            self.csrftoken = client.cookies['csrftoken']
        else:
            # older versions
            self.csrftoken = client.cookies['csrf']
        print(self.csrftoken)

        self.get_user_id(name)
        self.pw = self.get_user_pw(name)
        if password and  self.pw != password:
                self.connected = False
                return
        login_data = dict(csrfmiddlewaretoken=self.csrftoken, this_is_the_login_form=1, next='/profile/', username=name,
                          password=self.pw)
        headers['Referer'] = BASE_URL
        r = client.post(BASE_URL + "/login/", data=login_data, headers=headers)
        n = r.text.find(r'<a href="/logout/?next=/">')
        if n != -1:
            self.connected = True
            self.name=name
        else:
            self.name="Not connected"
            self.user_id = 0
            self.connected = False
            print("{} подключено {}".format(self.name,self.connected))
    def login_db(self):
        self.conn = sqlite3.connect("detservice.db")  # или :memory: чтобы сохранить в RAM
#Получить список тем
    def get_topics(self):
            print("{} Начинаем поиск тем".format(self.name))
            r = client.get(BASE_URL+r"/sp/?order_by=all&oz="+self.name+"&keyword=&keyword_area=all&pub_date=0&submit=Найти&stop_date=0")  # sets cookie
            time.sleep(3)
            str = html.fromstring(r.content)
            #преобразование документа к типу lxml.html.HtmlElement
            soup = BeautifulSoup(r.content, "lxml")
            for topic in soup.find_all("div", "b-actions__item_style_info_link"):
                tname = topic.find('a').contents[0];
                tref = topic.find('a').get('href')
                tid = tref.split("/")[3]
                self.add_topic(tid, tref, tname)
                #tref.split("/")[]
                print("{} № {} Тема :{} ссылка: {}".format(self.name,tid,tname,tref))
            #result = str.xpath("//tr[@class='odd']/td[1]/text()")
    def add_order(self,tref):
        cursor3 = self.conn.cursor()
        #добавляем заказ в закупку
        sp_id=tref.split("/")[3]
        print("{} добавляем заказ в закупку : {}".format(self.name, BASE_URL + tref))
        r = client.get(BASE_URL +tref)
        soup = BeautifulSoup(r.content, "lxml")
        for good in soup.find_all("div", "b-sp-photo_item"):
            a = good.find('a', "popup-photo")
            if a == None:
                continue
            form_url = a.get('form-url')
            #print(form_url)
            tref = a.get('href')
            #print(tref)

        if tref != None and len(tref.split("/")) > 4:
            card_id = tref.split("/")[3]
            photo_id = tref.split("/")[5]
            self.set_topic_good_id(card_id, photo_id)
            headers["Referer"] = BASE_URL + tref
            r = client.get(BASE_URL + form_url, headers=headers)
            time.sleep(3)

            form_data = dict()
            form_data['csrfmiddlewaretoken'] = self.csrftoken


            soup = BeautifulSoup(r.content, "lxml")
            # подготавливаем форму ля передачи, вытягиваем список полей из кода страницы
            for field in soup.find_all('input', {'name': re.compile(r'_field_')}):
                form_data[field.get('name')] = field.get('value')
            for field in soup.find_all('textarea', {'name': re.compile(r'_field_')}):
                form_data[field.get('name')] = ""

            for select in soup.find_all('select', {'name': re.compile(r'_field_')}):
                val=select.find('option',{'value': re.compile('.')}).get('value')
                #получаем первую опцию в списке выбора значений
                form_data[select.get('name')] = val

            form_data['delivery_place'] = 3
            form_data['photo_id'] = photo_id

            headers["Referer"] = BASE_URL + form_url
            r = client.post(BASE_URL + form_url, data=form_data, headers=headers)
            b = "update topics set last_up_time=strftime('%s','now') where id={}".format(sp_id)
            cursor3.execute(b)
            cursor3.close()
        else:
            print("{} ошибка asddorder {}".format(self.name,tref))

    def clear_topiс_bucket_arc(self, tref):
        #переносит отмененные заказы в архив
        print("{} Переносим отмененные заказы в архив : {}".format(self.name, BASE_URL + tref))
        time.sleep(3)
        r = client.get(BASE_URL + tref)
        soup = BeautifulSoup(r.content, "lxml")
        headers["Referer"] = BASE_URL + tref
        for good in soup.find_all("div", "b-contain-delete"):
            a = good.find('a').get('url')
            client.get(BASE_URL + a, headers=headers)
            time.sleep(3)
            print(a)

    def clear_topiс_bucket(self, tref):
        print("{} очищаем корзину заказов : {}".format(self.name, BASE_URL + tref))
        r = client.get(BASE_URL + tref)
        time.sleep(3)
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
                time.sleep(2)
                form_data = dict(csrfmiddlewaretoken=self.csrftoken, state_comment="")
                r = client.post(BASE_URL + ref, data=form_data, headers=headers)
                form_data = dict(csrfmiddlewaretoken=self.csrftoken, state_comment="Ах какая жалость!!! :(")
                r = client.post(BASE_URL + ref, data=form_data, headers=headers)
    def clear_topiс_bucket_by_good(self, tref):
        id=tref.split("/")[3].strip()
        cursor = self.conn.cursor()
        b = "select good_id from topics where id='{}'".format(id)
        cursor.execute(b)
        good_id = cursor.fetchone()[0]
        #получаем ID товара из базы
        print("{} очищаем корзину заказов : {}".format(self.name, BASE_URL + tref))
        r = client.get(BASE_URL + tref)
        time.sleep(2)
        soup = BeautifulSoup(r.content, "lxml")
        headers["Referer"] = BASE_URL + tref

        for good in soup.find_all("tr", "b-contain-item"):
            delete = False
            for reff in good.find_all('a'):
                if reff.get('href').find(str(good_id)) > 0: delete = True
            if not delete: continue
            div=good.find_all('div','main-info')
            a=div[1].find('a','popup-html')
            if not a==None:
                ref=a.get('href')
                print(ref)

                headers["Referer"] = BASE_URL + tref
                r = client.get(BASE_URL + ref, headers=headers)
                time.sleep(2)
                form_data = dict(csrfmiddlewaretoken=self.csrftoken, state_comment="")
                r = client.post(BASE_URL + ref, data=form_data, headers=headers)
                form_data = dict(csrfmiddlewaretoken=self.csrftoken, state_comment="Ах какая жалость!!! :(")
                r = client.post(BASE_URL + ref, data=form_data, headers=headers)

    def clear_org_rejected_orders(self, tref):
        #удаляет заказы со статусом отказ пользователя
        print("{} очищаем отказы пользователей у орга : {}".format(self.name, BASE_URL + tref))
        r = client.get(BASE_URL + tref)
        time.sleep(1)
        soup = BeautifulSoup(r.content, "lxml")
        headers["Referer"] = BASE_URL + tref

        headers["Referer"] = BASE_URL + tref
        form_data = dict()
        form_data['csrfmiddlewaretoken'] = self.csrftoken
        form_data['action'] = "delete"
        form_data['sp_card'] = ""
        form_data['comment'] = ""

        for order in soup.find_all("tr", "b-contain-item"):
            delete = False
            if "Отказ пользователя" in order.text:
                order_id=order.find("div",class_="commentSelf").get('order-id')
                form_data['orders'] = order_id
                r = client.post(BASE_URL + "/sp/order_list/{}/change_state/".format(tref.split("/")[3].strip()), data=form_data, headers=headers)
                time.sleep(1)
#"/sp/order_list/{}/?cancelled=1"
        r = client.get(BASE_URL + "/sp/order_list/{}/?cancelled=0".format(tref.split("/")[3].strip()))


    def reject_last_order(self, tref):
        #удаляем последний заказ в закупке
        print("{} удаляем последний заказ в закупке : {}".format(self.name, BASE_URL + tref))
        r = client.get(BASE_URL + tref)
        time.sleep(3)
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
                time.sleep(2)
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
    def set_topic_unactual(self):
        #добавляет в таблицу тему
        cursor = self.conn.cursor()
        b = "update topics set actual=0 where user_id={}".format(self.user_id)
        r=cursor.execute(b)
        self.conn.commit()
        cursor.close()
    def set_topic_good_id(self,topic_id,good_id):
        #добавляет в таблицу тему
        cursor = self.conn.cursor()
        b = "update topics set good_id={} where id={}".format(good_id , topic_id)
        r=cursor.execute(b)
        self.conn.commit()
        cursor.close()

    def add_topic(self, tid, tref, tname):
        #добавляет в таблицу тему
        cursor = self.conn.cursor()
        b = "select count(id) from topics where id={}".format(tid)
        r=cursor.execute(b)
        d=cursor.fetchone()
        if d[0] == 0:
            b = "insert into topics(id, name, ref, user_id) values({},'{}','{}','{}')".format(tid, tname, tref, self.user_id)
        else:
            b = "update topics set actual=1 where id={}".format(tid)
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

    def check_topics_position(self):
        cnn = sqlite3.connect("detservice.db")
        #проверяет место темы в выдаче
        pages = ["http://www.detkityumen.ru/sp/list/1/"]
        print("Запущена проверка места темы в выдаче : "+pages[0])
        headers["Referer"] = BASE_URL
        r = client.get(pages[0], headers=headers)
        time.sleep(3)
        soup = BeautifulSoup(r.content, "lxml")
        pager=soup.find('div', 'divPager')
        i=1
        for a in pager.find_all('a'):
            pages.append(BASE_URL+"/sp/list/1/"+a.get('href'))
            i+=1
            if i>4 : break;
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
            time.sleep(3)
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


    def raise_topics(self):
        cursor = self.conn.cursor()
        cursor2 = self.conn.cursor()
        b = "select u.name from users u"
        cursor.execute(b)
        # ТЕСТ
        for row in cursor.fetchall():
            self.login(row[0])
            self.set_topic_unactual()
            self.get_topics()
        self.check_topics_position()

        # conn1 = sqlite3.connect("detservice.db")  # или :memory: чтобы сохранить в RAM
        # проверяет необходимость поднятия тем и поднимает
        print("{} Запущено поднятие тем : {}".format(self.name, datetime.datetime.now()))
        # select t.id,t.name from topics t where (strftime('%s','now')-t.last_up_time)/60>t.interval_minutes
        # select datetime(t.last_up_time, 'unixepoch', 'localtime') from topics t
        # select t.id,t.name, (strftime('%s','now')-t.last_up_time)/60 d  from topics t where t.active=1
        # select t.id,t.name,t.user_id from topics t where (strftime('%s','now')-t.last_up_time)/60>t.interval_minutes and t.active=1 and t.page>t.maxpage order by user_id
        b = """ select t.id,t.name,t.user_id, u.name 
                from topics t, users u  
                where u.id=t.user_id 
                and (strftime('%s','now')-t.last_up_time)/60>t.interval_minutes 
                and t.active=1 
                and t.page>t.maxpage
                and t.actual=1
                and t.user_id=222823
                order by user_id"""
        # maha нахуй
        # ТЕСТ
        """b =  select t.id,t.name,t.user_id, u.name
        from topics t, users u  
        where u.id=t.user_id 
        and t.active=1 
        and t.page>t.maxpage
        and t.actual=1
        and t.user_id=222823
        and t.id = 87873
        order by user_id"""
        # выбираем просроченные задания
        cursor.execute(b)
        for row in cursor.fetchall():
            if row[3].upper() != self.name.upper():
                self.login(row[3])
            while row[3].upper() != self.name.upper():
                # важно чтобы залогинилась иначе пусть зациклится
                time.sleep(60)
                self.login(row[3])

            # ТЕСТ
            #self.clear_org_rejected_orders("/sp/order_list/{}/".format("86873"))
            self.clear_org_rejected_orders("/sp/order_list/{}/?cancelled=1".format(row[0]))
            self.add_order("/sp/igr/{}/photos/".format(row[0]))
            self.reject_last_order("/sp/bucket/{}/orders/".format(row[0]))
            self.clear_topiс_bucket_by_good("/sp/bucket/{}/orders/".format(row[0]))
            time.sleep(3)
            self.clear_topiс_bucket_arc("/sp/bucket/{}/orders/".format(row[0]))

            print("{} UP {}".format(datetime.datetime.now(), row[1]))

            self.conn.commit()

        cursor.close()
        cursor2.close()