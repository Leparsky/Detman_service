from flask import Flask, render_template, request, redirect, url_for

#from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from forms import LoginForm
from detman import detman



app = Flask(__name__)
#login_manager = LoginManager()
#login_manager.init_app(app)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/')
@app.route('/index')
def index():
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
    return render_template('index.html', title='Home', user=user, posts=posts)



@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        login = request.form["username"]
        password = request.form["password"]
        remember_me = request.form["remember_me"]
        # ищем пользователя по логину и паролю
        # get_user - внутренняя функция, для запроса к БД, например
        detmgr = detman()
        detmgr.login_db()
        detmgr.login(login,password)

        if detmgr.connected:
            user = usr()
            user.name = detmgr.name
            return redirect(url_for("index"))
    return render_template("login.html", title='Login', form=form)

if __name__ == "__main__":
    app.run()