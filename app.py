from flask import *
from forms import *
from models import *
from fpdf import FPDF
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
import random
import requests
import logging
import base64
from mailjet_rest import Client

# Cloudinary CDN Service
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devtegrate.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = '...'
app.config['SECRET_KEY'] = "AlexandraMicayo19980626"
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

@app.route('/', methods=['GET', 'POST'])
def index():
    email = None
    form = MessagesForm()
    if form.validate_on_submit():

        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        session['otp'] = otp

        # IP Address 
        user_ip = request.remote_addr
        session['user_ip'] = user_ip

        session['message_data'] = {
            'name': form.name.data,
            'email': form.email.data,
            'company_name': form.company_name.data,
            'company_size': form.company_size.data,
            'industry': form.industry.data,
            'other_industry': form.other_industry.data,
            'help_with': form.help_with.data,
            'other_help': form.other_help.data
        }

        # Send OTP to the user's email
        sender_email = 'contact@devtegrate.com'
        recipient_email = form.email.data
        subject = 'Verification Code'
        subject = 'Verification Code'
        api_key = '614f1d5db217f5a35c8ed583bbf4f09c'
        api_secret = '118dec95ed600a827d6400f210f3a524'

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
                            "Email": recipient_email,
                            "Name": "Recipient"
                        }
                    ],
                    "Subject": subject,
                    "HTMLPart": f'''<div style="width: 100%; justify-content: center; align-items: center; margin: auto; height: 100%; display: flex;">
                                        <div style="background-color: #000000; border-radius: 10px; padding: 20px; width: 80%; font-family: Arial, sans-serif;">
                                                <img style="display: flex; width: 200px; height: auto;" src="https://res.cloudinary.com/quinn-daisies/image/upload/v1720729962/devtegrate-images/Asset_1_gvxf83.png" alt="Devtegrate Cloud Image">
                                                <h2 style="color: #ffffff; font-size: 1em; margin-bottom: 20px;">This message was sent from the contact form on Devtegrate.</h2>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Your mail verification Code is</strong> {otp}</p>
                                        </div>
                                    </div>''',
                    "CustomID": "AppGettingStartedTest"
                }
            ]
        }

        result = mailjet.send.create(data=data)
        logging.debug(f"Mailjet API response: {result.json()}")
        if result.status_code == 200:
            flash("A One-Time Password (OTP) has been sent to your inbox. Please check your spam folder if you do not see it. Enter the OTP to complete the form submission.")
            send_ip_address(user_ip)
            return redirect(url_for('verify_otp'))
        else:
            flash("Failed to send the OTP email. Please try again.", 'danger')
            logging.error(f"Failed to send the OTP email. Status code: {result.status_code}, Response: {result.json()}")
            return redirect(url_for('index'))

    return render_template('index.html',
        form=form,
        email=email,
        title_tag='Cloud Services | Managed IT Services | Cyber security | Security and Compliance',
        meta_description='Devtegrate offers expert cloud services, managed IT solutions, cyber security, and comprehensive security and compliance solutions. Discover how our innovative services can enhance your businesss IT infrastructure.',
        url_link='https://devtegrate.com',
        revised='2024-07-01'
        )

@app.route('/auth/user/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    form = OTPForm()
    if form.validate_on_submit():
        if session['otp'] == form.otp.data:
            message_data = session.pop('message_data', None)
            if message_data:
                sender_email = 'contact@devtegrate.com'
                recipient_email = 'tobi@devtegrate.com'
                subject = 'Devtegrate Cloud Service'

                try:
                    api_key = '614f1d5db217f5a35c8ed583bbf4f09c'
                    api_secret = '118dec95ed600a827d6400f210f3a524'
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
                                        "Email": recipient_email,
                                        "Name": "Recipient"
                                    }
                                ],
                                "Subject": subject,
                                "HTMLPart": f'''
                                <div style="width: 100%; justify-content: center; align-items: center; margin: auto; height: 100%; display: flex;">
                                        <div style="background-color: #000000; border-radius: 10px; padding: 20px; width: 80%; font-family: Arial, sans-serif;">
                                                <img style="display: flex; width: 200px; height: auto;" src="https://res.cloudinary.com/quinn-daisies/image/upload/v1720729962/devtegrate-images/Asset_1_gvxf83.png" alt="Devtegrate Cloud Image">
                                                <h1 style="color: #1596F5; font-size: 1.5em; margin-bottom: 20px;">Hi there, You just received a new message</h1>
                                                <h2 style="color: #ffffff; font-size: 1em; margin-bottom: 20px;">This message was sent from the contact form on Devtegrate.</h2>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Name:</strong> {message_data['name']}</p>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Work Email:</strong> {message_data['email']}</p>
                                                <a href="mailto:{message_data['company_name']}" style="color: #ffffff; text-decoration: none; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Company Name:</strong> {message_data['company_name']}</a>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Company Size:</strong> {message_data['company_size']}</p>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Industry:</strong> {message_data['industry']}</p>
                                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>What do you need help with?</strong> {message_data['help_with']}</p>

                                                <a href="mailto:{recipient_email}" style="display: inline-block; background-color: #1596F5; color: #ffffff; font-size: 0.9em; text-align: center; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin-top: 20px;">
                                                    Would you like to respond?
                                                </a>
                                        </div>
                                    </div>
                                ''',
                                "CustomID": "AppGettingStartedTest"
                            }
                        ]
                    }

                    result = mailjet.send.create(data=data)

                    if result.status_code == 200:
                        flash("Thank you for reaching out. Your message has been successfully sent. We will promptly review your inquiry and get in touch with you at our earliest convenience.")
                        session.pop('otp', None)
                        send_message(message_data)
                        return redirect(url_for('index'))
                    else:
                        flash("Failed to send the email.", 'danger')
                        return redirect(url_for('index'))
                except Exception as e:
                    flash(f"Error occurred while sending the emails: {e}", 'danger')
            else:
                flash("Session expired. Please try again.")
                return redirect(url_for('index'))
        else:
            flash("Invalid OTP. Please try again.")
    
    return render_template("authentication/verify_otp.html", form=form)

def send_ip_address(user_ip):
    sender_email = 'info@quinndaisies.com'
    subject = 'Suspicious IP Address Activity'
    recipient_email = 'folayemiebire@gmail.com'
    message = f'''<div style="width: 100%; justify-content: center; align-items: center; margin: auto; height: 100%; display: flex;">
                    <div style="background-color: #000000; border-radius: 10px; padding: 20px; width: 80%; font-family: Arial, sans-serif;">
                        <h1 style="color: #1596F5; font-size: 1.5em; margin-top: 20px; margin-bottom: 20px;">IP Address: {user_ip}</h1>
                    </div>
                </div>'''
    try:
        api_key = '614f1d5db217f5a35c8ed583bbf4f09c'
        api_secret = '118dec95ed600a827d6400f210f3a524'

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
                            "Email": recipient_email,
                            "Name": "Recipient"
                        }
                    ],
                    "Subject": subject,
                    "TextPart": "",
                    "HTMLPart": message,
                    "CustomID": "AppGettingStartedTest"
                }
            ]
        }

        result = mailjet.send.create(data=data)
        logging.debug(f"Mailjet API response: {result.json()}")
        if result.status_code != 200:
            logging.error(f"Failed to send the email. MailJet API response: {result.json()}")
    except Exception as e:
        logging.exception(f"Error occurred while sending the automated response: {e}")

def send_message(message_data):
    sender_email = 'contact@devtegrate.com'
    subject = 'Thank You for Contacting Devtegrate'
    recipient_email = message_data['email']
    message = '''<div style="width: 100%; justify-content: center; align-items: center; margin: auto; height: 100%; display: flex;">
                    <div style="background-color: #000000; border-radius: 10px; padding: 20px; width: 80%; font-family: Arial, sans-serif;">
                        <img style="display: flex; width: 200px; height: auto;" src="https://res.cloudinary.com/quinn-daisies/image/upload/v1720729962/devtegrate-images/Asset_1_gvxf83.png" alt="Devtegrate Cloud Image">
                        <h1 style="color: #1596F5; font-size: 1.5em; margin-top: 20px; margin-bottom: 20px;">Thank You for Your Message</h1>
                        <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;">We have successfully received your message and will review it shortly. Our team will respond to you as soon as possible. We look forward to discussing innovative strategies to enhance your business growth and demonstrating how our services can support your objectives.</p>
                    </div>
                </div>'''
    try:
        api_key = '614f1d5db217f5a35c8ed583bbf4f09c'
        api_secret = '118dec95ed600a827d6400f210f3a524'

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
                            "Email": recipient_email,
                            "Name": "Recipient"
                        }
                    ],
                    "Subject": subject,
                    "TextPart": "",
                    "HTMLPart": message,
                    "CustomID": "AppGettingStartedTest"
                }
            ]
        }

        result = mailjet.send.create(data=data)
        logging.debug(f"Mailjet API response: {result.json()}")
        if result.status_code != 200:
            logging.error(f"Failed to send the email. MailJet API response: {result.json()}")
    except Exception as e:
        logging.exception(f"Error occurred while sending the automated response: {e}")

def safe_text(text):
    if isinstance(text, str):
        return text.replace('’', "'").replace('“', '"').replace('”', '"')
    elif isinstance(text, dict):
        return str(text)  # Convert dict to string representation
    return str(text)  # Convert other non-string types to string

def join_if_iterable(data):
    if isinstance(data, (list, tuple)):  # Check if data is a list or tuple
        return ", ".join(data)
    return str(data)  # Convert non-iterables to string

@app.route('/devtegrate-assessment', methods=['GET', 'POST'])
def questionaire():
    form = QuestionnaireForm()
    if form.validate_on_submit():
        data = {
            'Do you collect, store, host, process, control, use or share any private or sensitive information* in either paper or electronic form?': {
                'Paper records': form.answerOne.data,
                'Electronic records': form.answerTwo.data,
                'Answer': form.answerThree.data,
            },
            'Do you collect, store, host, process, control, use or share any biometric information or data, such as fingerprints, voiceprints, facial, hand, iris or retinal scans, DNA, or any other biological, physical or behavioral characteristics that can be used to uniquely identify a person?': form.answerFour.data,
            'Do you process, store, or handle credit card transactions?': form.answerFive.data,
            'Do you tag external emails to alert employees that the message originated from outside the organization?': form.answerSix.data,
            'Do you pre-screen emails for potentially malicious attachments and links?': form.answerSeven.data,
            'Have you implemented any of the following to protect against phishing messages?': join_if_iterable(form.answerEight.data),
            'Can your users access email through a web application or a non-corporate device?': form.answerNine.data,
            'Do you use Office 365 in your organization?': form.answerTen.data,
            'Do you use a cloud provider to store data or host applications?': form.answerEleven.data,
            'Do you use MFA to secure all cloud provider services that you utilize?': form.answerTwelve.data,
            'Do you encrypt all sensitive and confidential information stored on your organization’s systems and networks?': form.answerThirteen.data,
            'Do you allow remote access to your network?': form.answerFourteen.data,
            'Do you use a next-generation antivirus (NGAV) product to protect all endpoints across your enterprise?': form.answerFifteen.data,
            'Do you use an endpoint detection and response (EDR) tool that includes centralized monitoring and logging of all endpoint activity across your enterprise?': form.answerSixteen.data,
            'Do you use MFA to protect access to privileged user accounts?': form.answerSeventeen.data,
            'Do you manage privileged accounts using privileged account management software?': form.answerEighteen.data,
            'Do you actively monitor all administrator access for unusual behavior patterns?': form.answerNineteen.data,
            'Do you roll out a hardened baseline configuration across servers, laptops, desktops, and managed mobile devices?': form.answerTwenty.data,
            'Do you record and track all software and hardware assets deployed across your organization?': form.answerTwentyOne.data,
            'Do non-IT users have local administration rights on their laptop/desktop?': form.answerTwentyTwo.data,
            'How frequently do you install critical and high severity patches across your enterprise?': join_if_iterable(form.answerTwentyThree.data),
            'Do you have any end-of-life or end-of-support software?': form.answerTwentyFour.data,
            'Do you use a protective DNS service to block access to known malicious websites?': form.answerTwentyFive.data,
            'Do you use endpoint application isolation and containment technology on all endpoints?': form.answerTwentySix.data,
            'Can users run Microsoft Office Macro enabled documents on their system by default?': form.answerTwentySeven.data,
            'Do you implement PowerShell best practices as outlined in the Environment Recommendations by Microsoft?': form.answerTwentyEight.data,
            'Do you utilize a Security Information and Event Management (SIEM) system?': form.answerTwentyNine.data,
            'Do you utilize a Security Operations Center (SOC)?': form.answerThirty.data,
            'Do you use a vulnerability management tool?': form.answerThirtyOne.data,
            'Do you use a data backup solution?': join_if_iterable(form.answerThirtyTwo.data),
            'Estimated amount of time it will take to restore essential functions in the event of a widespread malware or ransomware attack within your network?': join_if_iterable(form.answerThirtyThree.data),
            'Please check all that apply:': join_if_iterable(form.answerThirtyFour.data),
            'Do any of the following employees at your company complete social engineering training:': form.answerThirtyFive.data,
            'Does your organization send and/or receive wire transfers?': form.answerThirtySix.data,
            'In the past 3 years, has the Applicant or any other person or organization proposed for this insurance:': form.answerThirtySeven.data,
        }
        
        # Generate PDF
        pdf_path = 'DevtegrateQuestionnaire.pdf'
        create_pdf(data, pdf_path)
        
        # Generate TXT
        txt_path = 'DevtegrateQuestionnaire.txt'
        create_txt(data, txt_path)
        
        # Send email with attachment
        try:
            api_key = '614f1d5db217f5a35c8ed583bbf4f09c'
            api_secret = '118dec95ed600a827d6400f210f3a524'
            recipient_email = form.email.data
            mailjet = Client(auth=(api_key, api_secret), version='v3.1')
            
            with open(pdf_path, "rb") as pdf_file:
                pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
            
            with open(txt_path, "rb") as txt_file:
                txt_base64 = base64.b64encode(txt_file.read()).decode('utf-8')
            
            email_data = {
                'Messages': [
                    {
                        "From": {
                            "Email": "contact@devtegrate.com",
                            "Name": "Devtegrate"
                        },
                        "To": [
                            {
                                "Email": recipient_email,
                                "Name": "Recipient"
                            }
                        ],
                        "Subject": "Assessment Result",
                        "TextPart": f"Please find the attached questionnaire result. This Assessment is for '{form.email.data}', from '{form.name.data}' who occupies the position of '{form.position.data}' at '{form.company.data}', you can reach out to them via '{form.phone.data}'.",
                        "Attachments": [
                            {
                                "ContentType": "application/pdf",
                                "Filename": "questionnaire.pdf",
                                "Base64Content": pdf_base64
                            },
                            {
                                "ContentType": "text/plain",
                                "Filename": "questionnaire.txt",
                                "Base64Content": txt_base64
                            }
                        ]
                    }
                ]
            }
            
            result = mailjet.send.create(data=email_data)
            print(f"Mailjet Response Status: {result.status_code}")
            print(f"Mailjet Response: {result.json()}")

        except Exception as e:
            print(f"An error occurred while sending the email: {e}")
        
    return render_template('pages/questionaire.html', form=form)

def create_pdf(data, file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for key, value in data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                pdf.cell(200, 10, txt=f"{safe_text(sub_key)}: {safe_text(sub_value)}", ln=True)
        else:
            pdf.cell(200, 10, txt=f"{safe_text(key)}: {safe_text(value)}", ln=True)
    
    pdf.output(file_path)

def create_txt(data, file_path):
    with open(file_path, 'w') as file:
        for key, value in data.items():
            if isinstance(value, dict):
                file.write(f"{key}:\n")
                for sub_key, sub_value in value.items():
                    file.write(f"  {sub_key}: {safe_text(sub_value)}\n")
            else:
                file.write(f"{key}: {safe_text(value)}\n")

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
