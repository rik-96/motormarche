from flask import Flask, render_template, flash, request, url_for, redirect, session
#from content_management import Content
from dbconnect import connection
from passlib.hash import sha256_crypt
from wtforms import Form, BooleanField, TextField, PasswordField, validators
import pymysql
pymysql.install_as_MySQLdb()
from MySQLdb import escape_string as thwart
from functools import wraps
import gc

#TOPIC_DICT = Content()

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

@app.route('/')
def homepage():
        return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
        return render_template("404.html")

@app.errorhandler(405)
def method_not_found(e):
        return render_template("405.html")


def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
                if 'logged_in' in session:
                        return f(*args, **kwargs)
                else:
                        flash("You need to login first")
                        return redirect(url_for('login_page'))
        return wrap

@app.route("/logout/")
@login_required
def logout():
        session.clear()
        flash("You have been logged out!")
        gc.collect()
        return redirect(url_for('homepage'))


@app.route('/login/', methods=["GET", "POST"])
def login_page():
        error = ''
        try:
                c, conn = connection()
                if request.method == "POST":
                        data = c.execute("SELECT * FROM users WHERE username = (%s)",
                                         thwart(request.form['username']))
                        data = c.fetchone()[2]
                        if sha256_crypt.verify(request.form['password'], data):
                                session['logged_in'] = True
                                session['username'] = request.form['username']
                                flash("You are now logged in")
                                return redirect(url_for("homepage"))
                        else:
                                error = "Invalid credentials, try again"
                gc.collect()

                return render_template("login.html", error=error)
        except Exception as e:
                #flash(e)
                error = "Invalid Credentials, try again."
                return render_template("login.html", error=error)

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password',[validators.Required(),
                validators.EqualTo('confirm',message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])

@app.route('/register/', methods=["GET","POST"])
def register_page():
        try:
                form = RegistrationForm(request.form)

                if request.method == "POST" and form.validate():
                        username = form.username.data
                        email = form.email.data
                        password = sha256_crypt.encrypt((str(form.password.data)))
                        c, conn = connection()

                        x = c.execute("SELECT * FROM users WHERE username = (%s)", (thwart(username)))

                        if int(x) > 0:
                                flash("That username is already taken, please choose another username")
                                return render_template('register.html', form = form)

                        else:
                                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                                          (thwart(username), thwart(password), thwart(email), thwart("/introduction-to-python-programming/")))

                                conn.commit()
                                flash("Thanks for registering!")
                                c.close()
                                conn.close()
                                gc.collect()

                                session['logged_in'] = True
                                session['username'] = username
                                return redirect(url_for('homepage'))

                return render_template("register.html", form=form)
        except Exception as e:
                return(str(e))
                        

if __name__ == "__main__":
        app.run()
