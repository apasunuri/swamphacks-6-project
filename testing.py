from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, current_app, url_for, redirect, flash
from flask_login import login_user, current_user, logout_user, UserMixin, LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
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
    Dist = StringField('Distance', validators=[DataRequired()])

class SelectPorts(FlaskForm):
    From = StringField('From', validators=[DataRequired()])
    To = SelectField('To', validators=[DataRequired()])
    Dist = StringField('Distance', validators=[DataRequired()])


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
def search(query_id=None):
    if current_user.auth_token == None:
        return render_template('home')
    first_name = current_user.name.split()[0]
    last_name = current_user.name.split()[1] if len(current_user.name.split()) > 1 else ''
    search = SearchBar()
    #defaults
    origin = {'lat': 0, 'lng': 0}
    dest = {'lat': 0, 'lng': 0}
    way = [{'lat': 0, 'lng': 0}]
    tim = "00:00"
    dist = "0.0"
    query_request = {'auth_token' : current_user.auth_token, 'query_id' : current_user.user_id}
    query_response = requests.post(backend_url + '/map/query/get', json=query_request) 
    if(query_response.status_code != 200):
        print("Error, No Response {}".format(query_response.status_code))
    else:
        query_response = query_response.json()
    if search.is_submitted():
        origin = search.From.data
        dest = search.To.data
        #confirm succesful query
        tempd = {'auth_token': current_user.auth_token, 'entry_o': origin, 'entry_d': dest, 'distance': search.Dist.data}
        response = requests.post(backend_url+'/map/query/new', json=tempd)
        if response.status_code != 200 :
            print("Error, no response")
        else:
            jobj = response.json()
            print(jobj)
            if jobj['status'] != 0:
                print(jobj)
                flash(jobj['message'], 'danger')
                return redirect(url_for('home'))
        #create points
    query_id = request.args.get('query_id')
    print(query_id)
    if query_id is None:
        wayjson = {'auth_token': current_user.auth_token}
    else:
        wayjson = {'auth_token': current_user.auth_token, 'query_id': query_id}
    way_response = requests.post(backend_url+'/map/query/result', json=wayjson)
    if way_response.status_code != 200:
        print("Error, no response {}".format(way_response.status_code))
    else:
        jobj = way_response.json()
        if jobj['status'] != 0:
            print(jobj)
            flash(jobj['message'], 'danger')
            return redirect(url_for('home'))
        way = jobj.get('deviations', [])
        tim = jobj.get('time', '00:00')
        dist = jobj.get('distance', '0.00')
    return render_template('dashboard.html', start_point=jobj.get('start', 0), end_point=jobj.get('end', 0), waypoints=[{"location": x} for x in way], form=search, first_name=first_name, last_name=last_name, queries=query_response['queries'], time=tim, distance=dist)

@app.route("/seaports", methods=['GET', 'POST'])
def account():
    first_name = current_user.name.split()[0]
    last_name = current_user.name.split()[1] if len(current_user.name.split()) > 1 else ''
    selectports = SelectPorts()
    cruise_response = requests.get(backend_url + '/map/ports/get').json()
    selectports.To.choices = [(x, x) for x in cruise_response['ports']]
    if selectports.is_submitted():
        origin = selectports.From.data
        dest = selectports.To.data
        #confirm succesful query
        tempd = {'auth_token': current_user.auth_token, 'entry_o': origin, 'entry_d': dest, 'distance': selectports.Dist.data}
        response = requests.post(backend_url+'/map/query/new', json=tempd)
        if response.status_code != 200 :
            print("Error, no response")
        else:
            jobj = response.json()
            print(jobj)
            if jobj['status'] != 0:
                print(jobj)
                flash(jobj['message'], 'danger')
                return redirect(url_for('home'))
        #create points
    query_request = {'auth_token' : current_user.auth_token, 'query_id' : current_user.user_id}
    query_response = requests.post(backend_url + '/map/query/get', json=query_request) 
    if(query_response.status_code != 200):
        print("Error, No Response {}".format(query_response.status_code))
    else:
        query_response = query_response.json()
    query_id = request.args.get('query_id')
    print(query_id)
    if query_id is None:
        wayjson = {'auth_token': current_user.auth_token}
    else:
        wayjson = {'auth_token': current_user.auth_token, 'query_id': query_id}
    way_response = requests.post(backend_url+'/map/query/result', json=wayjson)
    if way_response.status_code != 200:
        print("Error, no response {}".format(way_response.status_code))
    else:
        jobj = way_response.json()
        if jobj['status'] != 0:
            print(jobj)
            flash(jobj['message'], 'danger')
            return redirect(url_for('home'))
        way = jobj.get('deviations', [])
        tim = jobj.get('time', '00:00')
        dist = jobj.get('distance', '0.00')
    return render_template('seaports.html', start_point=jobj.get('start', 0), end_point=jobj.get('end', 0), waypoints=[{"location": x} for x in way], form=selectports, first_name=first_name, last_name=last_name, queries=query_response['queries'], time=tim, distance=dist)
    # return render_template('seaports.html', cruise_response=cruise_response, first_name=first_name, last_name=last_name, form=selectports)
        
if __name__ == "__main__":
    app.run(debug=True)
    
