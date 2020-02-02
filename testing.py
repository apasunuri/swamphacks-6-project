from flask import Flask, render_template, request, current_app, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email

app = Flask(__name__)

app.config['SECRET_KEY'] = 'abc786'

polyline = "ii|sDpjwuNqDAcIAgCA]?w@?wBAc@AgAAyAAiBCK?aAA_A?eAA_A?iAAwB?m@AiC?Q?_C@Y@S?eA?M@eA@"

start_point = {
    'lat' : 29.64133,
    'lng' : -82.37241
}

end_point = {
    'lat' : 34.048927,
    'lng' : -111.093735
}

waypoints = [
    {
        'location' : 'New York, NY',
        'stopover' : False
    },
    {
        'location' : 'Atlanta, GA',
        'stopover' : False
    }
]

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

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    reenter_password = PasswordField('retype password', validators=[DataRequired()])
    remember_me = BooleanField('remember-me', validators=[DataRequired()])
    # submit = SubmitField('Sign In')

class SearchBar(FlaskForm):
    From = StringField('From',validators=[DataRequired(), Length(1,64)], render_kw={'style': 'width:500px', "placeholder": "From"})
    To = StringField('To', render_kw={'style': 'width:500px', "placeholder": "To"}, validators=[DataRequired()])

@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/registration")
# def register():
#     return render_template("register.html")

@app.route("/map")
def map():
    return render_template('map.html', start_point=start_point, polyline=polyline)
    
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    # if form.validate_on_submit():
    #     flash()
    return render_template("register.html", form=form)
    # username = request.form['email']
    # password = request.form['pass']

@app.route("/dashboard", methods=['GET', 'POST'])
def search():
    search = SearchBar()
    if search.validate_on_submit():
        origin = search.From.data
        dest = search.To.data
    return render_template('dashboard.html', start_point=request["start"], end_point=request["end"], polyline=polyline, waypoints=request["deviations"], form=search)  
# def dashboard():
# return render_template('dashboard.html')

@app.route("/account")
def account():
    return render_template('account.html')
        
if __name__ == "__main__":
    app.run(debug=True)
    