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

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    reenter_password = PasswordField('retype password', validators=[DataRequired()])
    remember_me = BooleanField('remember-me', validators=[DataRequired()])
    # submit = SubmitField('Sign In')

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

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/account")
def account():
    return render_template('account.html')
        
if __name__ == "__main__":
    app.run(debug=True)
    