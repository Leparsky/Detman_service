from flask import Flask, render_template, request, redirect, url_for, flash
from flask_table import Table as ftTable, Col, LinkCol
from apscheduler.schedulers.background import BackgroundScheduler

#from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from forms import LoginForm, EditForm
from detman import detman
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table


engine = create_engine('sqlite:///detservice.db', convert_unicode=True)
metadata = MetaData(bind=engine)

users = Table('users', metadata, autoload=True)
topics = Table('users', metadata, autoload=True)

app = Flask(__name__)
#login_manager = LoginManager()
#login_manager.init_app(app)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

def sensor():
    smgr=detman()
    smgr.login_db()
    #smgr.login("Lencha")
    #smgr.set_topic_unactual()
    #smgr.get_topics()
    #smgr.check_topics_position()
    #smgr.clear_topiс_bucket("/sp/bucket/82621/orders/")
    smgr.raise_topics()


sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'interval',minutes=5)
sched.start()

class usr:
    # осуществляет работу с HTTP-запросами сайта http://www.detkityumen.ru/
    name=""
user = None


class Results(ftTable):
    id = Col('Id')
    name = Col('Название закупки')
    page = Col('текушая странца')
    maxpage = Col('Max странца')
    interval_minutes = Col('Время проверки в минутах')
    active = Col('Активно')
    up_time = Col('Время последнего поднятия')
    edit = LinkCol('Изменить параметры', 'edit', url_kwargs=dict(id='id'))


@app.route('/item/<int:id>', methods=['GET', 'POST'])
def edit(id):
    tpcs = engine.execute("""select t.id,
                                           t.name,
                                           t.page,
                                           t.maxpage max_page,
                                           t.interval_minutes,
                                           t.active, 
                                           datetime(last_up_time, 'unixepoch', 'localtime') up_time 
                                   from topics t 
                                   where actual=1 """+" and id={}".format(id)).first()
    form=EditForm(formdata=request.form, obj=tpcs)
    if request.method == 'POST': # and form.validate():
        #id1 = request.form["id"]
        name = request.form["name"]
        page = request.form["page"]
        max_page = request.form["max_page"]
        interval_minutes = request.form["interval_minutes"]
        active = request.form["active"]
        up_time = request.form["up_time"]

        conn = engine.connect()
        trans = conn.begin()
        conn.execute("update topics set maxpage = :maxpage,interval_minutes = :interval_minutes, active=:active where id=:id",  maxpage=max_page, interval_minutes = interval_minutes, active=active, id=id)
        trans.commit()
        conn.close()
        # save edits
        #save_changes(album, form)
        flash('Параметры сервиса поднятия  закупки "{}" изменены успешно'.format(id))
        return redirect('/')
    return render_template('edit_topic.html', form=form)

@app.route('/', methods=["GET"])
@app.route('/index', methods=["GET"])
def index():
    if user is None : return redirect('/login')
    tpcs = engine.execute("""select t.id,
                                       t.name,
                                       t.page,
                                       t.maxpage,
                                       t.interval_minutes,
                                       t.active, 
                                       datetime(last_up_time, 'unixepoch', 'localtime') up_time 
                               from topics t , users u
                               where t.actual=1 and t.user_id=u.id
                               and upper(u.name)='{}' order by t.active desc, t.name""".format(user.name.upper()))
    table = Results(tpcs)
    table.border = True
    return render_template('index2.html', table=table, username=user.name)


@app.route('/2a', methods=["GET"])
def index2():
    tpcs=engine.execute("""select t.id,
                                   t.name,
                                   t.page,
                                   t.maxpage,
                                   t.interval_minutes,
                                   t.active, 
                                   datetime(last_up_time, 'unixepoch', 'localtime') up_time 
                           from topics t 
                           where actual=1""")
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', tpcs=tpcs, user=user)



@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        login = request.form["username"]
        password = request.form["password"]
        #remember_me = request.form["remember_me"]
        # ищем пользователя по логину и паролю
        # get_user - внутренняя функция, для запроса к БД, например
        detmgr = detman()
        detmgr.login_db()
        detmgr.login(login,password)

        if detmgr.connected:
            global user
            user = usr()
            user.name = detmgr.name
            return redirect(url_for("index"))
    return render_template("login.html", title='Login', form=form)

if __name__ == "__main__":
    #app.run(host='10.0.0.2')
    app.run()