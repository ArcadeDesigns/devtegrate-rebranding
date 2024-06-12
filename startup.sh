#!/bin/bash

# To run file "./startup.sh"

# Create folders
mkdir templates static

# Create files
touch app.py models.py forms.py create_database.py database.py .gitignore

# Create subfolders in the templates folder
mkdir templates/components templates/authentication templates/forms templates/dashboard

# Create files in the templates folder
touch templates/index.html templates/base.html

# Create files in subfolders in the templates folder
touch templates/components/navbar.html templates/components/footer.html templates/components/notification.html

# Create files in subfolders in the templates folder
touch templates/authentication/login.html templates/authentication/registration.html

# Create subfolders in the static folder
mkdir static/js static/css 

# Create files subfolders in the static folder
touch static/js/app.js static/js/main.js static/js/index.js

# Create files subfolders in the static folder
touch static/css/app.css static/css/main.css static/css/index.css 

cat <<EOF > app.py
from flask import *
from forms import *
from models import *
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from flask_ckeditor import upload_success, upload_fail
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
import urllib.request
from database import db
import uuid as uuid
import os
import requests
import logging
from mailjet_rest import Client

# Cloudinary CDN Service
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

app = Flask(__name__)
ckeditor = CKEditor(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///....db'
#app.config['SQLALCHEMY_DATABASE_URI'] = '...'
app.config['SECRET_KEY'] = "cairocoders-ednalan"
app.config['FLASK_DEBUG'] = True

cloudinary.config(
    cloud_name="...",
    api_key="...",
    api_secret="...",
)

upload("https://upload.wikimedia.org/wikipedia/commons/a/ae/Olympic_flag.jpg",
       public_id="olympic_flag")
url, options = cloudinary_url(
    "olympic_flag", width=100, height=150, crop="fill")

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSIONS'] = [
    'jpg', 'jpeg', 'png', 'JPG', 'gif', 'PNG', 'JPEG']
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CLIENT_ID = '...'
CLIENT_SECRET = '...'
REDIRECT_URI = '...'

# Google Authentication
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

# Paystack configuration
PAYSTACK_SECRET_KEY = '...'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

app.config['MAX_CONTENT_LENGTH'] = 16 * 900 * 900
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'JPG', 'gif', 'PNG', 'JPEG'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


####################################################################################################################################################################################
####################################################################################################################################################################################
####################################################################################################################################################################################
####################################################################################################################################################################################

@app.route('/renaissance/auth/google-callback')
def google_callback():
    code = request.args.get('code')
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    access_token = response.json().get('access_token')
    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            user = Users.query.filter_by(email=profile_data['email']).first()
            if user:
                login_user(user)
                flash("Login Successful!", 'success')
                return redirect(url_for('dashboard'))
                
            else:
                hashed_pw = generate_password_hash('your_random_password', "sha256")
                user = Users(name=profile_data['name'], username=profile_data['email'], email=profile_data['email'], password_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("User Created and logged In Successfully", "success")
                return redirect(url_for('properties'))
    return redirect(url_for('google_login'))

@app.route('/continue/with/google')
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid email profile',
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{'&'.join(f'{key}={value}' for key, value in params.items())}"
    return redirect(auth_url)


####################################################################################################################################################################################
####################################################################################################################################################################################
####################################################################################################################################################################################
####################################################################################################################################################################################

@app.route('/files/<path:filename>')
def uploaded_files(filename):
    app = current_app._get_current_object()
    path = (app.config['UPLOAD_FOLDER'])
    return send_from_directory(path, filename)

@app.route('/upload', methods=['POST'])
def upload():
    app = current_app._get_current_object()
    f = request.files.get('upload')

    # Add more validations here
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    saver.save(os.path.join((app.config['UPLOAD_FOLDER']), f.filename))
    url = url_for('main.uploaded_files', filename=f.filename)
    return upload_success(url, filename=f.filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("components/404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("components/500.html"), 500

if __name__ == '__main__':
    app.run(debug=True)
EOF

cat <<EOF > models.py
from database import db
from datetime import date, datetime
from flask_login import UserMixin

class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Boolean, default='User')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def formatted_date(self):
        return self.date_posted.strftime("%B %Y")

    def formatted_date_with_day(self):
        return self.date_posted.strftime("%d %B %Y")

    def formatted_time(self):
        return self.date_posted.strftime("%I:%M %p").lstrip('0')

    def time_since_posted(self):
        time_diff = datetime.now() - self.date_posted
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if time_diff.days > 0:
            return f"{time_diff.days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "just now"

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=True)
    last_name = db.Column(db.String(), nullable=True)
    middle_name = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)
    password_hash = db.Column(db.String())

    # Foreignkey Integration
    roles = db.relationship('Roles', backref='poster', lazy=True, cascade='all, delete-orphan')

    def formatted_date(self):
        return self.date_added.strftime("%B %Y")

    def formatted_date_with_day(self):
        return self.date_added.strftime("%d %B %Y")

    def formatted_time(self):
        return self.date_added.strftime("%I:%M %p").lstrip('0')

    def time_since_posted(self):
        time_diff = datetime.now() - self.date_added
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if time_diff.days > 0:
            return f"{time_diff.days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "just now"
    
    @property
    def password(self):
        raise AttributeError(' Password Not A Readable Attribute !!! ')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create string
    def __repr__(self):
        return '<Name %r>' % self.name
EOF

cat <<EOF > create_database.py
from app import app, db
with app.app_context():
    db.create_all()
EOF

cat <<EOF > database.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
EOF

cat <<EOF > .gitignore
.gitignore
/environment
EOF

cat <<EOF > base.html
<!DOCTYPE html>
<html lang="en-US">

<head>
  <meta charset="UTF-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta property="og:type" content="homepage" />
  <meta property="type" content="homepage" />
  <meta name="google-site-verification" content="------------" />

  <title>{{ title_tag }}</title>

  <!-- Links -->
  <link rel="canonical" href="{{ url_link }}" />
  <link rel="og:canonical" href="{{ url_link }}" />
  <link rel="image_src" src="..................." />
  <link rel="shortcut icon" type="image/png" src="..................." />
  <meta name="apple-touch-fullscreen" content="yes" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta property="og:image" src="..................." />

  <link rel="icon" type="image/png" href="..................." />

  <meta property="twitter:image" src="..................." />
  <meta property="twitter:card" content="summary_large_image" />
  <link rel="icon" href="..................." />
  <meta name="og:description" content="{{ meta_description }}" />
  <meta name="description" content="{{ meta_description }}" />
  <meta name="og:keywords" content="{{ keyword }}" />
  <meta name="keywords" content="{{ keyword }}" />
  <meta name="rating" content="General" />
  <meta content="all" name="Googlebot-Image" />
  <meta content="all" name="Slurp" />
  <meta content="all" name="Scooter" />
  <meta content="ALL" name="WEBCRAWLERS" />
  <meta name="revisit-ALL" content="1 days" />
  <meta name="robots" content="ALL, index, follow" />
  <meta name="author" content="Ebire Folayemi Michael" />
  <meta name="revised" content="{{ revised }}" />
  <meta name="viewport" content="width=device-width, initial-scale=1." />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
    integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous" />

  <!-------------------------------------------------------------------
    ---------------------------------------------------------------------
    -------------------------------------------------------------------->

  <!-- Website CSS -->
  <link href="{{ url_for('static', filename='css/app.css') }}" rel="stylesheet" />

  <link href="{{ url_for('static', filename='css/main.css') }}" rel="stylesheet" />

  <link href="{{ url_for('static', filename='css/index.css') }}" rel="stylesheet" />

  <!-------------------------------------------------------------------
    ---------------------------------------------------------------------
    -------------------------------------------------------------------->

  <link href="https://unpkg.com/boxicons@2.1.2/css/boxicons.min.css" rel="stylesheet" />

  <link rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&display=swap"
    rel="stylesheet">

  <script src="https://unpkg.com/scrollreveal"></script>
</head>

<body>
  {% block content %}

  {% endblock %}

  <script src="{{ url_for('static', filename='js/app.js') }}"></script>

  <script src="{{ url_for('static', filename='js/main.js') }}"></script>

  <script src="{{ url_for('static', filename='js/index.js') }}"></script>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
    integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
    crossorigin="anonymous"></script>
  <script>
    ScrollReveal({
      reset: true,
      distance: "200px",
      duration: 1500,
      delay: 600,
    });

    ScrollReveal().reveal(".reveal__left", { delay: 200, origin: "left" });
    ScrollReveal().reveal(".reveal__right", {
      delay: 200,
      origin: "right",
    });

    ScrollReveal().reveal(".reveal__top", { delay: 200, origin: "top" });
    ScrollReveal().reveal(".reveal__bottom", {
      delay: 200,
      origin: "bottom",
    });

    // Text Animation Section //

    ScrollReveal().reveal(".reveal__top", { 
      delay: 500, 
      origin: "top" 
    });

    ScrollReveal().reveal(".reveal__bottom", {
      delay: 500,
      origin: "bottom",
    });

    ScrollReveal().reveal(".reveal__left", { 
      delay: 500, 
      origin: "left" 
    });

    ScrollReveal().reveal(".reveal__right", {
      delay: 500,
      origin: "right",
    });

    ScrollReveal().reveal(".reveal__interval__top", {
      delay: 400,
      origin: "top",
      interval: 200,
    });

    ScrollReveal().reveal(".reveal__interval__left", {
      delay: 400,
      origin: "left",
      interval: 200,
    });

    ScrollReveal().reveal(".reveal__interval__right", {
      delay: 400,
      origin: "right",
      interval: 200,
    });

    ScrollReveal().reveal(".reveal__interval__bottom", {
      delay: 400,
      origin: "bottom",
      interval: 200,
    });

    ScrollReveal().reveal(".reveal__text", {
      delay: 1000,
      origin: "left",
    });
    
  </script>
</body>

</html>
EOF


cat <<EOF > index.html
{% extends 'base.html' %}
    {% block content %}
        {% include 'components/navbar.html' %}
        {% include 'components/notification.html' %}

        {% include 'components/footer.html' %}
    {% endblock %}
EOF


cat <<EOF > app.css
@import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

.poppins-thin {
  font-family: "Poppins", sans-serif;
  font-weight: 100;
  font-style: normal;
}

.poppins-extralight {
  font-family: "Poppins", sans-serif;
  font-weight: 200;
  font-style: normal;
}

.poppins-light {
  font-family: "Poppins", sans-serif;
  font-weight: 300;
  font-style: normal;
}

.poppins-regular {
  font-family: "Poppins", sans-serif;
  font-weight: 400;
  font-style: normal;
}

.poppins-medium {
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  font-style: normal;
}

.poppins-semibold {
  font-family: "Poppins", sans-serif;
  font-weight: 600;
  font-style: normal;
}

.poppins-bold {
  font-family: "Poppins", sans-serif;
  font-weight: 700;
  font-style: normal;
}

.poppins-extrabold {
  font-family: "Poppins", sans-serif;
  font-weight: 800;
  font-style: normal;
}

.poppins-black {
  font-family: "Poppins", sans-serif;
  font-weight: 900;
  font-style: normal;
}

.poppins-thin-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 100;
  font-style: italic;
}

.poppins-extralight-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 200;
  font-style: italic;
}

.poppins-light-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 300;
  font-style: italic;
}

.poppins-regular-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 400;
  font-style: italic;
}

.poppins-medium-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 500;
  font-style: italic;
}

.poppins-semibold-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 600;
  font-style: italic;
}

.poppins-bold-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 700;
  font-style: italic;
}

.poppins-extrabold-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 800;
  font-style: italic;
}

.poppins-black-italic {
  font-family: "Poppins", sans-serif;
  font-weight: 900;
  font-style: italic;
}

* {
  font-optical-sizing: auto;
    margin: 0;
    padding: 0;
    scroll-behavior: smooth;
    scroll-padding-top: 2rem;
    -webkit-box-sizing: border-box;
            box-sizing: border-box;
}

/*variables*/
:root {
  /*variables Colors*/
  --primary-color: #FFFFFF;
  --secondary-color: #000000;
  --tertiary-color: ------;
  --background-color: ------;
  --text-color: #888888;
  --reserved-color: ------;

  /*variables Text*/
  --mega-header: 5em;
  --mini-header: 4em;
  --header-text: 3em;
  --medium-text: 2em;
  --small-text: 1.5em;
  --p-text: 1.1em;
  --span-text: 0.9em;
  --link-span-text: 0.8em;
}

body, html{
  overflow-x: hidden;
}
EOF
