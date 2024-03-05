from datetime import timedelta
from flask import Flask, redirect, url_for, render_template, request,session, flash #display message
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#secret key for the sessions
app.secret_key = "hello"
#set up configuration for our database URI unique resource indicator - where it lives
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3' #users is name of table
app.permanent_session_lifetime = timedelta(days=5) #keeps session data for a certain amount of time

#create a database
db = SQLAlchemy(app)
#store details on our users, name and email

class users(db.Model): #this is a database model
    _id = db.Column("id", db.Integer, primary_key=True) #this is the unique id for each object in our table, we'll use this to reference
    name = db.Column("name",db.String(100))
    email = db.Column("email",db.String(150))

    def __init__(self, name, email): #this is our initialisation
        self.name = name
        self.email = email

@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/view")
def view():
    return render_template("view.html",values=users.query.all())

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        session.permanent = True #links to the app.permanent_session
        user = request.form["name"]
        session["user"] = user #stores data as a dictionary the bit in square bracks is the key

        found_user = users.query.filter_by(name=user).first() #this will search our db for the name entered
        if found_user:
            session["email"] = found_user.email #this adds the users email to the db, if they're already logged in.
        else:
            usr = users(user, None) #they haven't entered email yet so left blank
            db.session.add(usr) #this adds the usr above to our db
            db.session.commit() #Every time we make a change it adds it to our db

        flash("Login Successful!","info")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in!","info")
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/user", methods=["POST","GET"])
def user():
    email = None #declare variable
    #check any data in the session
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"] #get the email from the form
            session["email"] = email #store the email in the session
            found_user = users.query.filter_by(name=user).first() #queries the user again
            found_user.email = email #this will add the updated email to the db
            db.session.commit()
            flash("Email was saved!","info")
        else:
            if "email" in session:
                email = session["email"]

        return render_template("user.html", email = email, user=user)
    else:
        flash("You are not logged in!","info")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    flash("You have been logged out", "info")
    session.pop("user",None) #this removes the data from the session
    session.pop("email",None)
    return redirect(url_for("login"))

with app.app_context():
    db.create_all()
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
