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

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devtegrate.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = '...'
app.config['SECRET_KEY'] = "cairocoders-ednalan"
app.config['FLASK_DEBUG'] = True

'''cloudinary.config(
    cloud_name="...",
    api_key="...",
    api_secret="...",
)

upload("https://upload.wikimedia.org/wikipedia/commons/a/ae/Olympic_flag.jpg",
       public_id="olympic_flag")
url, options = cloudinary_url(
    "olympic_flag", width=100, height=150, crop="fill")'''

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

@app.route('/', methods=['GET', 'POST'])
def index():
    form = MessagesForm()
    if form.validate_on_submit():
        sender_email = 'folayemiebire@gmail.com'
        name = form.name.data
        recipient_emails = 'tobi@devtegrate.com'
        company_name = form.company_name.data
        company_size = form.company_size.data
        industry = form.industry.data
        other_industry = form.other_industry.data
        help_with = form.help_with.data
        other_help = form.other_help.data

        try:
            api_key = '7313cf6592999b69b87e0136ef2d0eea'
            api_secret = '06f5e0d8c5df097b9841e91e8bb51e04'

            mailjet = Client(auth=(api_key, api_secret), version='v3.1')

            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": sender_email,
                            "Name": "Devtegrate"
                        },
                        "To": [
                            {
                                "Email": recipient_emails,
                                "Name": "Devtegrate"
                            }
                        ],
                        "Subject": subject,
                        "TextPart": "",
                        "HTMLPart": f'''<h2 style="@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap'); font-family: 'poppins', sans-serif; font-size: 1.4em; font-weight: 100; color: #000000; text-align: left; padding: 0 0 15px 0;"">You just received a message<br>{message}<br><p @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap'); font-family: 'poppins', sans-serif; font-size: 0.9em; font-weight: 100; color: #000000; text-align: left; padding: 0 0 15px 0;">Contact phone number:</p>{phone}</p>''',
                        "CustomID": "AppGettingStartedTest"
                    }
                ]
            }

            result = mailjet.send.create(data=data)
            
            # Check if the request was successful (status code 2xx)
            if result.status_code == 200:
                flash("Thank you for reaching out. Your message has been successfully sent. We will promptly review your inquiry and get in touch with you at our earliest convenience.")
            else:
                print(f"Failed to send the email. MailJet API response: {result.json()}")
                flash("Failed to send the email.", 'danger')
        except Exception as e:
            print(f"Error occurred while sending the emails: {e}")
            flash("Failed to send the email.", 'danger')

    return render_template('index.html',
        form=form,
        title_tag='Devtegrate Cloud | Cloud Services | Cloud DevOps',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/cloud-integration', methods=['GET', 'POST'])
def cloud_integration():
    return render_template('pages/cloud-integration.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/cloud-automation', methods=['GET', 'POST'])
def cloud_automation():
    return render_template('pages/cloud-automation.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/cloud-computing', methods=['GET', 'POST'])
def cloud_computing():
    return render_template('pages/cloud-computing.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/inspiration', methods=['GET', 'POST'])
def inspiration():
    return render_template('pages/inspiration.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/team', methods=['GET', 'POST'])
def team():
    return render_template('pages/team.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/amazon-web-service', methods=['GET', 'POST'])
def aws():
    return render_template('pages/aws.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/microsoft-azure', methods=['GET', 'POST'])
def azure():
    return render_template('pages/azure.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/google-cloud-service', methods=['GET', 'POST'])
def gcp():
    return render_template('pages/gcp.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/cloud-infrastructure', methods=['GET', 'POST'])
def cloud_infrastructure():
    return render_template('pages/cloud-infrastructure.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/about-us', methods=['GET', 'POST'])
def about():
    return render_template('pages/about.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/cloud-services', methods=['GET', 'POST'])
def cloud_service():
    return render_template('pages/cloud-services.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/our-services', methods=['GET', 'POST'])
def service():
    return render_template('pages/service.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/cloud-devops', methods=['GET', 'POST'])
def cloud_devops():
    return render_template('pages/cloud-devops.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/security-compliance', methods=['GET', 'POST'])
def security_compliance():
    return render_template('pages/security-compliance.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/software-development', methods=['GET', 'POST'])
def software_development():
    return render_template('pages/software-development.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/cyber-security', methods=['GET', 'POST'])
def cyber_security():
    return render_template('pages/cyber-security.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/financial-services', methods=['GET', 'POST'])
def financial_services():
    return render_template('pages/financial-services.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/government', methods=['GET', 'POST'])
def government():
    return render_template('pages/government.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/health', methods=['GET', 'POST'])
def health():
    return render_template('pages/health.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

@app.route('/technology', methods=['GET', 'POST'])
def technology():
    return render_template('pages/technology.html',
        title_tag='',
        meta_description='',
        url_link='',
        revised=''
    )

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
