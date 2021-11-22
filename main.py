from random import sample
from datetime import date, datetime
from flask import Flask, render_template, redirect, abort, session, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import requests
import os
from functools import wraps
from forms import AddNewForm, UpdateForm
from notifications_manager import Notifications
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)
oauth = OAuth(app)

# CONNECT TO DB
DB = os.environ.get("DB")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL1", DB)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# GOOGLE Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

email_accounts = os.environ.get("EMAIL_ACCOUNTS")
email_acc_list = email_accounts.split(",")


year = date.today().strftime("%Y")
now = datetime.now()


class ImageGallery(db.Model):
    __tablename__ = "gallery"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    size = db.Column(db.String(15), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500), nullable=False, unique=True)


db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        try:
            if user["email"] not in email_acc_list:
                return abort(403, description="Only eMAGN admins have access to this section.")
        except TypeError:
            return abort(403, description="You have to be an admin and login to access this site.")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=["POST", "GET"])
def home():
    trip_images = []
    square_images = []
    all_images = ImageGallery.query.all()
    for image in all_images:
        if image.size == "Square":
            square_images.append(image)
        elif image.size == "Trip":
            trip_images.append(image)
    random_trip = sample(trip_images, 2)
    random_square = sample(square_images, 2)
    if request.method == "POST":
        notifications = Notifications()
        contact_name = request.form["name"]
        contact_email = request.form["email"]
        notifications.send_message(name=contact_name, email=contact_email)
    return render_template("index.html", year=year, trip_pics=random_trip, square_pics=random_square)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            oauth.register(
                name="google",
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                server_metadata_url=GOOGLE_DISCOVERY_URL,
                client_kwargs={
                    "scope": "openid email profile"
                }
            )
            # Redirect to google_auth function
            redirect_uri = url_for("callback", _external=True)
            return oauth.google.authorize_redirect(redirect_uri)
        except ConnectionError:
            return abort(503, description="Ha habido un problema al conectar con Google, intentalo mas tarde.")

    return render_template("login.html")


@app.route("/callback")
def callback():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    if user:
        session["user"] = user

    return redirect(url_for('gallery'))


@app.route("/image_gallery")
@admin_only
def gallery():
    all_images = ImageGallery.query.all()
    return render_template("gallery.html", images=all_images)


@app.route("/add_image", methods=["GET", "POST"])
@admin_only
def add():
    form = AddNewForm()
    if form.validate_on_submit():
        image_title = form.title.data
        image_size = form.size.data
        image_description = form.description.data
        image_url = form.url.data
        if image_description:
            new_image = ImageGallery(title=image_title, size=image_size, description=image_description, url=image_url)
        else:
            new_image = ImageGallery(title=image_title, size=image_size, url=image_url)
        db.session.add(new_image)
        db.session.commit()
        return redirect(url_for("gallery"))
    return render_template("add.html", form=form)


@app.route("/delete/<image_id>", methods=["POST", "GET"])
@admin_only
def delete(image_id):
    image_to_delete = ImageGallery.query.get(image_id)
    db.session.delete(image_to_delete)
    db.session.commit()
    return redirect(url_for("gallery"))


@app.route("/edit", methods=["POST", "GET"])
@admin_only
def edit():
    image_id = request.args.get("image_id")
    image_to_update = ImageGallery.query.get(image_id)
    form = UpdateForm(
        title=image_to_update.title,
        description=image_to_update.description
    )
    if form.validate_on_submit():
        image_to_update.title = form.title.data
        image_to_update.description = form.description.data
        db.session.commit()
        return redirect(url_for("gallery"))
    return render_template("edit.html", image=image_to_update, form=form)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
