from flask import Flask, render_template, request, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email

app = Flask(__name__)

app.config['SECRET_KEY'] = 'abc786'

class RegistrationForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember-me', validators=[DataRequired()])
    # submit = SubmitField('Sign In')



@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/registration")
# def register():
#     return render_template("register.html")
    
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    # if form.validate_on_submit():
    #     flash()
    return render_template("register.html", form=form)
    # username = request.form['email']
    # password = request.form['pass']
        

if __name__ == "__main__":
    app.run(debug=True)
    