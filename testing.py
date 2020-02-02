from flask import Flask, render_template, request, current_app, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email
import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = 'abc786'
polyline = "ii|sDpjwuNqDAcIAgCA]?w@?wBAc@AgAAyAAiBCK?aAA_A?eAA_A?iAAwB?m@AiC?Q?_C@Y@S?eA?M@eA@"

backend_url = 'https://tester-267001.appspot.com'

request = {
    "status": 0, 
    "message": "Basic Route Created Successfully", 
    "start": "University of Florida", 
    "end": "Georgia Tech",
    "deviations": [
        {'location': {"lat" : 30.75429950000001, "lng" : -83.2732205}}, 
        {'location': {"lat" : 32.1904529, "lng" : -83.7493425}}, 
        {'location': {"lat" : 33.4328247, "lng" : -84.1849962}}
    ]
}

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    retype_password = PasswordField('retype_password', validators=[DataRequired()])
    remember_me = BooleanField('remember-me', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class SearchBar(FlaskForm):
    From = StringField('From', validators=[DataRequired()])
    To = StringField('To', validators=[DataRequired()])
    From = StringField('From',validators=[DataRequired(), Length(1,64)], render_kw={'style': 'width:500px', "placeholder": "From"})
    To = StringField('To', render_kw={'style': 'width:500px', "placeholder": "To"}, validators=[DataRequired()])

@app.route("/", methods=['GET', 'POST'])
def home():
    login = LoginForm()
    if(login.is_submitted()):
        email = login.email.data
        password =  login.password.data
        req = {
            "email" : email,
            "password" : password
        }
        r = requests.post(backend_url + '/login', json=req)
        if(r.status_code == 200):
            return redirect(url_for('search'))
        else:
            return redirect(url_for('home'))
    return render_template("index.html", form=login)

# @app.route("/registration")
# def register():
#     return render_template("register.html")

@app.route("/map")
def map():
    return render_template('map.html', start_point=start_point, polyline=polyline)
    
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
            r = requests.post(backend_url + '/register', json=req)
            if(r['status'] == 0):
                return redirect(url_for('search'))
            else:
                return redirect(url_for('register'))
    return render_template("register.html", form=form)

@app.route("/dashboard", methods=['GET', 'POST'])
def search():
    search = SearchBar()
    if search.is_submitted():
        origin = search.From.data
        dest = search.To.data
        print(origin)
        print(dest)
    return render_template('dashboard.html', start_point=request["start"], end_point=request["end"], polyline=polyline, waypoints=request["deviations"], form=search)  
# def dashboard():
#     return render_template('dashboard.html')

@app.route("/account")
def account():
    return render_template('account.html')
        
if __name__ == "__main__":
    app.run(debug=True)
    