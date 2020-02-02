from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, current_app, url_for, redirect, flash
from flask_login import login_user, current_user, logout_user, UserMixin, LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email
import requests
import json

#frontend session database
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

#application settings
app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc786'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)

#backend
backend_url = 'https://tester-267001.appspot.com'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(127))
    email = db.Column(db.String(127))
    auth_token = db.Column(db.String(127))

    def __init__(self, id, name, email, auth_token):
        self.user_id = id
        self.name = name
        self.email = email
        self.auth_token = auth_token

#login classes
class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('remember-me', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    retype_password = PasswordField('retype_password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class SearchBar(FlaskForm):
    From = StringField('From', validators=[DataRequired()])
    To = StringField('To', validators=[DataRequired()])

@app.route("/", methods=['GET', 'POST'])
def home():
    db.create_all()
    login = LoginForm()
    if(login.is_submitted()):
        email = login.email.data
        password =  login.password.data
        
        req = {
            "email" : email,
            "password" : password
        }
        response = requests.post(backend_url + '/login', json=req)
        if(response.status_code == 200):
            job = response.json()
            if job['status'] != 0:
                print(job)
                flash(job['message'], 'danger')
                return redirect(url_for('home'))
            print(job) 
            jobj = job['user']
            user = User(jobj['id'], jobj['name'], jobj['email'], jobj['auth_token'])
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=login.remember.data)
            return redirect(url_for('search'))
        else:
            flash("ERROR")
            return redirect(url_for('home'))
    return render_template("index.html", form=login)

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if(form.is_submitted()):
        name = form.name.data
        email = form.email.data
        password = form.password.data
        retype_password = form.retype_password.data
        if(password == retype_password):
            req = {
                "name" : name,
                "email" : email,
                "password" : password
            }
            rresponse = requests.post(backend_url + '/register', json=req) 
            if(rresponse.status_code == 200):
                jobj = rresponse.json()
                print(jobj)
                print(req)
                return redirect(url_for('home'))
            else:
                return redirect(url_for('register'))
    return render_template("register.html", form=form)

@app.route("/dashboard", methods=['GET', 'POST'])
def search(): 
    search = SearchBar()
    origin = {'lat': 0, 'lng': 0}
    dest = {'lat': 0, 'lng': 0}
    way = [{'lat': 0, 'lng': 0}]
    if search.is_submitted():
        origin = search.From.data
        dest = search.To.data
        #confirm succesful query
        tempd = {'auth_token': current_user.auth_token, 'entry_o': origin, 'entry_d': dest}
        response = requests.post(backend_url+'/map/query/new', json=tempd)
        if response.status_code != 200:
            print("Error, no response")
        else:
            jobj = response.json()
            print(jobj)
        #create points
        wayjson = {'auth_token': current_user.auth_token}
        way_response = requests.post(backend_url+'/map/query/result', json=tempd)
        if way_response.status_code != 200:
            print("Error, no response {}".format(way_response.status_code))
        else:
            jobj = way_response.json()
            print(jobj)
            way = jobj['deviations']
            print(way)
    return render_template('dashboard.html', start_point=origin, end_point=dest, waypoints=way, form=search)

@app.route("/account")
def account():
    return render_template('account.html')
        
if __name__ == "__main__":
    app.run(debug=True)
    
