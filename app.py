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
        email = form.email.data
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
                        "Subject": 'Devtegrate Cloud Service',
                        "TextPart": "",
                        "HTMLPart": f'''<div style="width: 100%; justify-content: center; align-items: center; margin: auto; height: 100%; display: flex;">
                                            <div style="background-color: #000000; border-radius: 10px; padding: 20px; width: 80%; font-family: Arial, sans-serif;">

                                                <img style="display: flex; width: 100%; height: auto;" src="https://res.cloudinary.com/quinn-daisies/image/upload/v1719936097/devtegrate-brand/Artboard_4-removebg-preview_awjz1u.png" alt="Devtegrate Cloud Image">

                                                <h1 style="color: #1596F5; font-size: 1.5em; margin-bottom: 20px;">Hi there, You just received a new message</h1>
                                                <h2 style="color: #ffffff; font-size: 1em; margin-bottom: 20px;">This message was sent from the contact form on Devtegrate.</h2>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Name:</strong> {name}</p>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Work Email:</strong> {email}</p>
                                                <a href="mailto:{company_name}" style="color: #ffffff; text-decoration: none; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Company Name:</strong>{company_name}</a>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Company Size:</strong> {company_size}</p>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Industry:</strong> {industry}</p>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>What do you need help with?</strong> {help_with}</p>

                                                <a href="mailto:{recipient_emails}" style="display: inline-block; background-color: #1596F5; color: #ffffff; font-size: 0.9em; text-align: center; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                                                    Would you like to respond?
                                                </a>
                                            </div>
                                        </div>''',
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
        meta_description='Welcome to Devtegrate, your premier partner for comprehensive cloud services and expert cloud DevOps solutions. Enhance your business agility and efficiency with our state-of-the-art cloud solutions.',
        url_link='https://devtegrate.com/',
        revised='2024-07-01'
    )

@app.route('/cloud-integration', methods=['GET', 'POST'])
def cloud_integration():
    return render_template('pages/cloud-integration.html',
        title_tag='Cloud Integration Services | Seamlessly Connect Your Systems',
        meta_description='Discover top-notch cloud integration services to seamlessly connect your systems and streamline your operations. Enhance your business agility with our expert solutions.',
        url_link='https://devtegrate.com/cloud-integration',
        revised='2024-07-01'
    )

@app.route('/cloud-automation', methods=['GET', 'POST'])
def cloud_automation():
    return render_template('pages/cloud-automation.html',
        title_tag='Cloud Automation Solutions | Optimize and Automate Workflows',
        meta_description='Explore advanced cloud automation solutions to optimize and automate your workflows. Increase efficiency and reduce operational costs with our state-of-the-art automation services.',
        url_link='https://devtegrate.com/cloud-automation',
        revised='2024-07-01'
    )

@app.route('/cloud-computing', methods=['GET', 'POST'])
def cloud_computing():
    return render_template('pages/cloud-computing.html',
        title_tag='Cloud Computing Services | Scalable and Secure Solutions',
        meta_description='Get the best cloud computing services with scalable and secure solutions tailored to your business needs. Leverage our expertise to drive your digital transformation.',
        url_link='https://devtegrate.com/cloud-computing',
        revised='2024-07-01'
    )

@app.route('/inspiration', methods=['GET', 'POST'])
def inspiration():
    return render_template('pages/inspiration.html',
        title_tag='Inspiration and Ideas | Innovative Solutions for Your Business',
        meta_description='Find inspiration and innovative ideas to take your business to the next level. Discover trends, tips, and success stories that can help you grow and thrive.',
        url_link='https://devtegrate.com/inspiration',
        revised='2024-07-01'
    )

@app.route('/team', methods=['GET', 'POST'])
def team():
    return render_template('pages/team.html',
        title_tag='Meet Our Team | Experts in Cloud Solutions and Services',
        meta_description='Meet our team of experts dedicated to providing top-notch cloud solutions and services. Learn more about the professionals driving your success.',
        url_link='https://devtegrate.com/team',
        revised='2024-07-01'
    )

@app.route('/amazon-web-service', methods=['GET', 'POST'])
def aws():
    return render_template('pages/aws.html',
        title_tag='Amazon Web Services (AWS) | Reliable and Scalable Cloud Solutions',
        meta_description='Leverage Amazon Web Services (AWS) for reliable and scalable cloud solutions. Our expert team provides comprehensive AWS services tailored to your needs.',
        url_link='https://devtegrate.com/amazon-web-service',
        revised='2024-07-01'
    )

@app.route('/microsoft-azure', methods=['GET', 'POST'])
def azure():
    return render_template('pages/azure.html',
        title_tag='Microsoft Azure Services | Secure and Flexible Cloud Solutions',
        meta_description='Explore Microsoft Azure services for secure and flexible cloud solutions. Our experienced team helps you harness the power of Azure to achieve your business goals.',
        url_link='https://devtegrate.com/microsoft-azure',
        revised='2024-07-01'
    )

@app.route('/google-cloud-service', methods=['GET', 'POST'])
def gcp():
    return render_template('pages/gcp.html',
        title_tag='Google Cloud Services (GCP) | Powerful and Innovative Cloud Solutions',
        meta_description='Discover Google Cloud Services (GCP) for powerful and innovative cloud solutions. Our experts provide tailored GCP services to support your business transformation.',
        url_link='https://devtegrate.com/google-cloud-service',
        revised='2024-07-01'
    )

@app.route('/cloud-infrastructure', methods=['GET', 'POST'])
def cloud_infrastructure():
    return render_template('pages/cloud-infrastructure.html',
        title_tag='Cloud Infrastructure Solutions | Scalable and Robust | Devtegrate',
        meta_description='Enhance your business operations with our scalable and robust cloud infrastructure solutions. Trust Devtegrate for reliable cloud infrastructure services.',
        url_link='https://devtegrate.com/cloud-infrastructure',
        revised='2024-07-01'
    )

@app.route('/about-us', methods=['GET', 'POST'])
def about():
    return render_template('pages/about.html',
        title_tag='About Devtegrate | Leading Cloud Solutions Provider',
        meta_description='Learn more about Devtegrate, a leading provider of innovative cloud solutions. Discover our mission, vision, and the team behind our success.',
        url_link='https://devtegrate.com/about-us',
        revised='2024-07-01'
    )

@app.route('/cloud-services', methods=['GET', 'POST'])
def cloud_service():
    return render_template('pages/cloud-services.html',
        title_tag='Comprehensive Cloud Services | Tailored to Your Needs | Devtegrate',
        meta_description='Explore Devtegrate’s comprehensive cloud services, tailored to meet your business needs. From integration to automation, we offer end-to-end cloud solutions.',
        url_link='https://devtegrate.com/cloud-services',
        revised='2024-07-01'
    )

@app.route('/our-services', methods=['GET', 'POST'])
def service():
    return render_template('pages/service.html',
        title_tag='Our Services | Expert Cloud Solutions and Consulting | Devtegrate',
        meta_description='Discover the wide range of cloud solutions and consulting services offered by Devtegrate. Our expert team is dedicated to helping your business thrive.',
        url_link='https://devtegrate.com/our-services',
        revised='2024-07-01'
    )

@app.route('/cloud-devops', methods=['GET', 'POST'])
def cloud_devops():
    return render_template('pages/cloud-devops.html',
        title_tag='Cloud DevOps Services | Streamline Development and Operations | Devtegrate',
        meta_description='Optimize your development and operations with Devtegrate’s cloud DevOps services. Streamline workflows and enhance efficiency with our expert solutions.',
        url_link='https://devtegrate.com/cloud-devops',
        revised='2024-07-01'
    )

@app.route('/security-compliance', methods=['GET', 'POST'])
def security_compliance():
    return render_template('pages/security-compliance.html',
        title_tag='Cloud Security and Compliance | Protect Your Data | Devtegrate',
        meta_description='Ensure the security and compliance of your cloud infrastructure with Devtegrate. Protect your data and meet regulatory requirements with our expert services.',
        url_link='https://devtegrate.com/security-compliance',
        revised='2024-07-01'
    )

@app.route('/software-development', methods=['GET', 'POST'])
def software_development():
    return render_template('pages/software-development.html',
        title_tag='Custom Software Development Services | Innovative Solutions | Devtegrate',
        meta_description='Transform your business with custom software development services from Devtegrate. Our innovative solutions are designed to meet your unique needs.',
        url_link='https://devtegrate.com/software-development',
        revised='2024-07-01'
    )

@app.route('/cyber-security', methods=['GET', 'POST'])
def cyber_security():
    return render_template('pages/cyber-security.html',
        title_tag='Cyber Security Services | Protect Your Business | Devtegrate',
        meta_description='Safeguard your business with Devtegrate’s comprehensive cyber security services. Protect your data and systems from threats with our expert solutions.',
        url_link='https://devtegrate.com/cyber-security',
        revised='2024-07-01'
    )

@app.route('/financial-services', methods=['GET', 'POST'])
def financial_services():
    return render_template('pages/financial-services.html',
        title_tag='Financial Services Solutions | Enhance Your Financial Operations | Devtegrate',
        meta_description='Optimize your financial operations with Devtegrate’s tailored financial services solutions. Improve efficiency and compliance with our expert services.',
        url_link='https://devtegrate.com/financial-services',
        revised='2024-07-01'
    )

@app.route('/government', methods=['GET', 'POST'])
def government():
    return render_template('pages/government.html',
        title_tag='Government Cloud Solutions | Secure and Compliant | Devtegrate',
        meta_description='Empower your government agency with secure and compliant cloud solutions from Devtegrate. Leverage our expertise to improve public services and efficiency.',
        url_link='https://devtegrate.com/government',
        revised='2024-07-01'
    )

@app.route('/health', methods=['GET', 'POST'])
def health():
    return render_template('pages/health.html',
        title_tag='Healthcare Cloud Solutions | Enhance Patient Care | Devtegrate',
        meta_description='Enhance patient care with Devtegrate’s healthcare cloud solutions. Improve efficiency, security, and compliance in your healthcare operations.',
        url_link='https://devtegrate.com/health',
        revised='2024-07-01'
    )

@app.route('/technology', methods=['GET', 'POST'])
def technology():
    return render_template('pages/technology.html',
        title_tag='Technology Solutions | Innovative and Scalable | Devtegrate',
        meta_description='Stay ahead with Devtegrate’s innovative and scalable technology solutions. From cloud computing to cyber security, we provide comprehensive tech services.',
        url_link='https://devtegrate.com/technology',
        revised='2024-07-01'
    )

@app.route('/privacy-policy', methods=['GET', 'POST'])
def privacy_policy():
    return render_template('pages/privacy-policy.html',
        title_tag='Privacy Policy | Devtegrate',
        meta_description='Read Devtegrates privacy policy to understand how we collect, use, and protect your personal information. Your privacy is important to us.',
        url_link='https://devtegrate.com/privacy-policy',
        revised='2024-07-01'
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
