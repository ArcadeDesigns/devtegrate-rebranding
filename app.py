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
app.config['SECRET_KEY'] = "GoodDeedsAlexandraMicayo19980626"
app.config['FLASK_DEBUG'] = True


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
        secret_response = request.form['g-recaptcha-response']
        verify_response = requests.post(
            url=f'https://www.google.com/recaptcha/api/siteverify?secret=6Lfe1CwqAAAAAJxa-YGYQ01JvqSKyc78h22rIFbC&response={secret_response}'
        ).json()
        print(verify_response)
        
        if not verify_response.get('success') or verify_response.get('score', 0) < 0.5:
            flash("reCAPTCHA verification failed. Please try again.", 'danger')
            return redirect(url_for('index'))

        message_data = {
            'name': form.name.data,
            'email': form.email.data,
            'company_name': form.company_name.data,
            'company_size': form.company_size.data,
            'industry': form.industry.data,
            'other_industry': form.other_industry.data,
            'help_with': form.help_with.data,
            'other_help': form.other_help.data
        }

        sender_email = 'contact@devtegrate.com'
        recipient_email = 'tobi@devtegrate.com'
        subject = 'Devtegrate Cloud Service'

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
                                <p style="color: #ffffff; font-size: 0.9em; line-height: 1.6; margin-bottom: 20px;"><strong>Company Name:</strong> {message_data['company_name']}</p>
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
                send_message(message_data)
                return redirect(url_for('index'))
            else:
                flash("Failed to send the email.", 'danger')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error occurred while sending the email: {e}", 'danger')
            return redirect(url_for('index'))

    return render_template('index.html',
        form=form,
        email=email,
        title_tag='Cloud Services | Managed IT Services | Cyber security | Security and Compliance',
        meta_description='Devtegrate offers expert cloud services, managed IT solutions, cyber security, and comprehensive security and compliance solutions. Discover how our innovative services can enhance your business IT infrastructure.',
        url_link='https://devtegrate.com',
        revised='2024-07-01'
    )

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
    if isinstance(data, (list, tuple)): # Check if data is a list or tuple
        return ", ".join(data)
    return str(data)  # Convert non-iterables to string

@app.route('/devtegrate-assessment', methods=['GET', 'POST'])
def questionaire():
    form = QuestionnaireForm()
    if form.validate_on_submit():
        secret_response = request.form['g-recaptcha-response']
        verify_response = requests.post(
            url=f'https://www.google.com/recaptcha/api/siteverify?secret=6Lf2FhMqAAAAAAAlFMtdt0d6OO8aIINVETpyWFx8&response={secret_response}'
        ).json()
        print(verify_response)
        
        if not verify_response.get('success') or verify_response.get('score', 0) < 0.5:
            flash("reCAPTCHA verification failed. Please try again.", 'danger')
            return redirect(url_for('index'))

        data = {
            'Client Information': {
                'Full Name': form.name.data, '| Email Address': form.email.data, '| Contact Number': form.phone.data, '| Company Name': form.company.data, '| Position Held': form.position.data,
            },

            '1.  Do you collect, store, host, process, control, use or share any private or sensitive information* in either paper or electronic form?': {
                'a.  Paper records': form.answerOne.data,
                'b.  Electronic records': form.answerTwo.data,
                'c.  Answer': form.answerThree.data,
                'i.  If “Yes”, please provide the approximate number of unique records': form.inputOne.data,
            },
            
            '2.  Do you collect, store, host, process, control, use or share any biometric information or data, such as fingerprints, voiceprints, facial, hand, iris or retinal scans, DNA, or any other biological, physical or behavioral characteristics that can be used to uniquely identify a person?': form.answerFour.data,
            'i.  If “Yes”, have you reviewed your policies relating to the collection, storage, and destruction of such information or data with a qualified attorney and confirmed compliance with applicable federal, state, local, and foreign laws?': form.inputTwo.data,

            '3.  Do you process, store, or handle credit card transactions?': form.answerFive.data,
            'i.  If “Yes”, are you PCI-DSS Compliant?': form.inputThree.data,

            '4.  Do you tag external emails to alert employees that the message originated from outside the organization?': form.answerSix.data,
            'i.  If “Yes”, have you reviewed your policies relating to the collection, storage, and destruction of such information or data with a qualified attorney and confirmed compliance with applicable federal, state, local, and foreign laws?': form.inputFour.data,

            '5.  Do you pre-screen emails for potentially malicious attachments and links?': form.answerSeven.data,
            'i.  If “Yes”, do you have the capability to automatically detonate and evaluate attachments in a sandbox to determine if they are malicious prior to delivery to the end-user?': form.inputFive.data,

            '6.  Have you implemented any of the following to protect against phishing messages?': join_if_iterable(form.answerEight.data),

            '7.  Can your users access email through a web application or a non-corporate device?': form.answerNine.data,
            'i.  If “Yes”, do you enforce Multi-Factor Authentication (MFA)?': form.inputSix.data,

            '8.  Do you use Office 365 in your organization?': form.answerTen.data,
            'i.  If “Yes”, do you use the Office 365 Advanced Threat Protection add-on?': form.inputSeven.data,

            '9.  Do you use a cloud provider to store data or host applications?': form.answerEleven.data,
            'i.  If “Yes”, please provide the name of the cloud provider:': form.inputEight.data,
            'ii.  If you use more than one cloud provider to store data, please specify the cloud provider storing the largest quantity of sensitive customer and/or employee records.': form.inputNine.data,

            '10   Do you use MFA to secure all cloud provider services that you utilize?': form.answerTwelve.data,

            '11.  Do you encrypt all sensitive and confidential information stored on your organization’s systems and networks?': form.answerThirteen.data,

            '12.  Do you allow remote access to your network?': form.answerFourteen.data,
            'i.  If MFA is used, please select your MFA provider:': form.inputTen.data,

            '13.  Do you use a next-generation antivirus (NGAV) product to protect all endpoints across your enterprise?': form.answerFifteen.data,
            'i.  If “Yes”, please select your NGAV provider:': form.inputEleven.data,

            '14.  Do you use an endpoint detection and response (EDR) tool that includes centralized monitoring and logging of all endpoint activity across your enterprise?': form.answerSixteen.data,
            'i.  If “Yes”, please select your EDR provider:': form.inputTwelve.data,

            '15.  Do you use MFA to protect access to privileged user accounts?': form.answerSeventeen.data,

            '16.  Do you manage privileged accounts using privileged account management software?': form.answerEighteen.data,
            'i.  If “Yes”, please provide the name of your provider:' : form.inputThirteen.data,

            '17.  Do you actively monitor all administrator access for unusual behavior patterns?': form.answerNineteen.data,
            'i.  If “Yes”, please provide the name of your monitoring tool:' : form.inputFourteen.data,
            
            '18.  Do you roll out a hardened baseline configuration across servers, laptops, desktops, and managed mobile devices?': form.answerTwenty.data,

            '19.  Do you record and track all software and hardware assets deployed across your organization?': form.answerTwentyOne.data,
            'i.  If “Yes”, please provide the name of the tool used for this purpose (if any):': form.inputFifteen.data,

            '20.  Do non-IT users have local administration rights on their laptop/desktop?': form.answerTwentyTwo.data,
            '21.  How frequently do you install critical and high severity patches across your enterprise?': join_if_iterable(form.answerTwentyThree.data),

            '22.  Do you have any end-of-life or end-of-support software?': form.answerTwentyFour.data,
            'i.  If “Yes”, is it segregated from the rest of your network?': form.inputSixteen.data,

            '23.  Do you use a protective DNS service to block access to known malicious websites?': form.inputSeventeen.data,
            'i.  If “Yes”, please provide the name of your DNS provider:': form.inputSeventeen.data,

            '24.  Do you use endpoint application isolation and containment technology on all endpoints?': form.answerTwentySix.data,
            'i.  If “Yes”, please select your provider:': form.inputEighteen.data,

            '25.  Can users run Microsoft Office Macro enabled documents on their system by default?': form.answerTwentySeven.data,
            
            '26.  Do you implement PowerShell best practices as outlined in the Environment Recommendations by Microsoft?': form.answerTwentyEight.data,
            
            '27.  Do you utilize a Security Information and Event Management (SIEM) system?': form.answerTwentyNine.data,
            
            '28.  Do you utilize a Security Operations Center (SOC)?': form.answerThirty.data,
            'i.  If “Yes”, is it monitored 24 hours a day, 7 days a week?': form.inputNineteen.data,

            '29.  Do you use a vulnerability management tool?': form.answerThirtyOne.data,
            'i.  If “Yes”, please select your provider:': form.inputTwenty.data,

            '30.  Do you use a data backup solution?': join_if_iterable(form.answerThirtyTwo.data),

            '31.  Estimated amount of time it will take to restore essential functions in the event of a widespread malware or ransomware attack within your network?': join_if_iterable(form.answerThirtyThree.data),

            '32.  Please check all that apply:': join_if_iterable(form.answerThirtyFour.data),

            '33.  Do any of the following employees at your company complete social engineering training:': form.answerThirtyFive.data,
            'i.  If “Yes” to question 9.a.(1) or 9.a.(2) above, does your social engineering training include phishing simulation?': form.inputTwentyOne.data,

            '34.  Does your organization send and/or receive wire transfers?': form.answerThirtySix.data,

            '35.  In the past 3 years, has the Applicant or any other person or organization proposed for this insurance:': form.answerThirtySeven.data,
        }
        
        # Generate PDF
        pdf_path = 'DevtegrateQuestionnaire.pdf'
        create_pdf(data, pdf_path)
        
        # Generate TXT
        txt_path = 'DevtegrateQuestionnaire.txt'
        create_txt(data, txt_path)
        
        # Send email with attachment
        try:
            api_key = '7313cf6592999b69b87e0136ef2d0eea'
            api_secret = '06f5e0d8c5df097b9841e91e8bb51e04'
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
                                "Email": 'tobi@devtegrate.com',
                                "Name": "Recipient"
                            }
                        ],
                        "Subject": "Assessment Result",
                        "TextPart": f"Please find the attached questionnaire result. This Assessment is for {form.company.data} from {form.name.data} who occupies the position of {form.position.data} at {form.company.data}, you can reach out to them via telephone at; {form.phone.data}, and email via {form.email.data}.",
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
            flash("Thank you for completing our complimentary assessment. Your insights are invaluable and will enable us to better understand your specific vulnerabilities, allowing us to offer customized solutions. To further enhance our evaluation, please provide the following details. We assure you that all information shared will remain confidential and be used exclusively for this assessment. A member of our team or your dedicated account manager will be in touch shortly. Thank you once again for your participation.")

        except Exception as e:
            print(f"An error occurred while sending the email: {e}")
            flash('Seems like there was an error! Please reach out to us via mail: contact@devtegrate.com')
        
    return render_template('pages/questionaire.html', form=form)

def create_pdf(data, file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    def wrap_text(text, width):
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(width, 10, txt=safe_text(text))

    for key, value in data.items():
        if isinstance(value, dict):
            wrap_text(key, 190)  # Adjust width as needed
            for sub_key, sub_value in value.items():
                wrap_text(f"  {sub_key}: {safe_text(sub_value)}", 190)  # Adjust width as needed
            pdf.ln()  # Add a line break
        else:
            wrap_text(f"{key}: {safe_text(value)}", 190)  # Adjust width as needed
        pdf.ln()  # Add a line break
    
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

@app.route('/microsoft-form', methods=['GET', 'POST'])
def microsoft_form():
    form = MicrosoftForm()
    if form.validate_on_submit():
        secret_response = request.form['g-recaptcha-response']
        verify_response = requests.post(
            url=f'https://www.google.com/recaptcha/api/siteverify?secret=6LdgeDcqAAAAAIaV_KdbIEIEZFlHEDyvVha6aWwt&response={secret_response}'
        ).json()
        print(verify_response)
        
        if not verify_response.get('success') or verify_response.get('score', 0) < 0.5:
            flash("reCAPTCHA verification failed. Please try again.", 'danger')
            return redirect(url_for('index'))

        microsft_message_data = {
            '1. First and Last Name': form.name.data,
            '2. Email Address': form.email.data,
            '3. Phone Number': form.contact.data,
            '4. What services are you interested in? (Select all that apply)': form.serviceOthers.data,
            '5. What is the size of your business?': form.companySize.data,
            '6. What is your biggest technology challenge?': form.techChallenge.data,
            '7. What industry does your company belong to?': form.companyIndustry.data,
            '8. When are you looking to implement these solutions?': form.solutions.data,
            '9. Preferred method of contact': form.contactMethod.data,
        }

        sender_email = 'contact@devtegrate.com'
        recipient_email = 'tobi@devtegrate.com'
        subject = 'Devtegrate Prospective Client'

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
                                "Email": recipient_email,
                                "Name": "Recipient"
                            }
                        ],
                        "Subject": subject,
                        "HTMLPart": f'''
                            <div style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
                            <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                                <div style="background-color: #000000; padding: 20px; text-align: left;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 1.2em;">Devtegrate</h1>
                                </div>
                                <div style="padding: 20px;">
                                    <h2 style="color: #333333; margin-top: 0; font-size: 1em;">Dear Tobi Ogebule</h2>
                                    <p style="color: #666666; font-size: .8em;">We have received new information from a prospective client through the form you distributed. Please review the details at your earliest convenience to take the necessary actions.</p>
                                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                        <h3 style="color: #333333; margin-top: 0; font-size: 1em;">Prospective Client Answers:</h3>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>1. First and Last Name:</strong> {microsft_message_data['1. First and Last Name']}
                                        </p>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>2. Email Address:</strong> {microsft_message_data['2. Email Address']}
                                        </p>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>3. Phone Number:</strong> {microsft_message_data['3. Phone Number']}
                                        </p>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>4. What services are you interested in? (Select all that apply):</strong> {microsft_message_data['4. What services are you interested in? (Select all that apply)']}
                                        </p>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>5. What is the size of your business?</strong> {microsft_message_data['5. What is the size of your business?']}
                                        </p>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>6. What is your biggest technology challenge?</strong> {microsft_message_data['6. What is your biggest technology challenge?']}
                                        </p>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>7. What industry does your company belong to?</strong> {microsft_message_data['7. What industry does your company belong to?']}
                                        </p>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>8. When are you looking to implement these solutions?</strong> {microsft_message_data['8. When are you looking to implement these solutions?']}
                                        </p>
                                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                                            <strong>9. Preferred method of contact:</strong> {microsft_message_data['9. Preferred method of contact']}
                                        </p>
                                    </div>

                                    <div style="text-align: left; margin-top: 20px;">
                                        <a href="mailto:{microsft_message_data['2. Email Address']}" style="display: inline-block; font-size: .8em; padding: 10px 20px; background-color: #000000; color: #ffffff; text-decoration: none; border-radius: 5px;">Get in touch with Client</a>
                                    </div>
                                </div>
                                <div style="background-color: #000000; padding: 15px; text-align: center;">
                                    <p style="color: #ffffff; margin: 0; font-size: .8em;">&copy; 2024 Devtegrate. All rights reserved.</p>
                                </div>
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
                send_microsoft_message(microsft_message_data)
                return redirect(url_for('index'))
            else:
                flash("Failed to send the email.", 'danger')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error occurred while sending the email: {e}", 'danger')
            return redirect(url_for('index'))

    return render_template('forms/form.html',
        form=form,
        title_tag='',
        meta_description=' ',
        url_link=' ',
        revised='2024-07-01'
    )

def send_microsoft_message(microsft_message_data):
    sender_email = 'contact@devtegrate.com'
    subject = 'Thank You for Contacting Devtegrate'
    recipient_email = microsft_message_data['2. Email Address']
    message = f'''<div style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <!-- Header Section -->
                <div style="background-color: #000000; padding: 20px; text-align: left;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 1.2em;">Devtegrate</h1>
                </div>
                <!-- Body Section -->
                <div style="padding: 20px;">
                    <h2 style="color: #333333; margin-top: 0; font-size: 1em;">Dear {microsft_message_data['1. First and Last Name']}</h2>
                    <p style="color: #666666; font-size: .8em;">Thank you for contacting Devtegrate. We have received your information and will get back to you shortly.</p>
                    <p style="color: #666666; font-size: .8em;">Here are the details you provided:</p>
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>First and Last Name:</strong> {microsft_message_data['1. First and Last Name']}
                        </p>
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>Email Address:</strong> {microsft_message_data['2. Email Address']}
                        </p>
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>Phone Number:</strong> {microsft_message_data['3. Phone Number']}
                        </p>
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>Services of Interest:</strong> {microsft_message_data['4. What services are you interested in? (Select all that apply)']}
                        </p>
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>Company Size:</strong> {microsft_message_data['5. What is the size of your business?']}
                        </p>
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>Biggest Technology Challenge:</strong> {microsft_message_data['6. What is your biggest technology challenge?']}
                        </p>
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>Company Industry:</strong> {microsft_message_data['7. What industry does your company belong to?']}
                        </p>
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>Implementation Timeline:</strong> {microsft_message_data['8. When are you looking to implement these solutions?']}
                        </p>
                        <p style="color: #666666; margin: 0; font-size: 0.9em;">
                            <strong>Preferred Contact Method:</strong> {microsft_message_data['9. Preferred method of contact']}
                        </p>
                    </div>
                    
                    <p style="color: #666666; font-size: .8em;">We look forward to assisting you.</p>
                    
                    <!-- Call to Action Button -->
                    <div style="text-align: left; margin-top: 20px;">
                        <a href="https://wwww.devtegrate.com" style="display: inline-block; font-size: .8em; padding: 10px 20px; background-color: #000000; color: #ffffff; text-decoration: none; border-radius: 5px;">Get Started</a>
                    </div>

                    <div style="text-align: left; margin-top: 20px;">
                        <!-- Facebook Share -->
                        <a href="https://www.facebook.com/sharer/sharer.php?u=https://devtegrate.com" target="_blank" style="display: inline-block; font-size: 1.2em; padding: 5px 10px; background-color: #000000; color: #ffffff; text-decoration: none; border-radius: 5px;">
                            <i class="bx bxl-facebook"></i>
                        </a>

                        <!-- Twitter Share -->
                        <a href="https://twitter.com/intent/tweet?url=https://devtegrate.com&text=Check%20this%20out!" target="_blank" style="display: inline-block; font-size: 1.2em; padding: 5px 10px; background-color: #000000; color: #ffffff; text-decoration: none; border-radius: 5px;">
                            <i class="bx bxl-twitter"></i>
                        </a>

                        <!-- LinkedIn Share -->
                        <a href="https://www.linkedin.com/shareArticle?mini=true&url=https://devtegrate.com&title=Title%20Here&summary=Summary%20Here" target="_blank" style="display: inline-block; font-size: 1.2em; padding: 5px 10px; background-color: #000000; color: #ffffff; text-decoration: none; border-radius: 5px;">
                            <i class="bx bxl-linkedin"></i>
                        </a>

                        <!-- Instagram (Note: Instagram does not have direct share links) -->
                        <a href="https://www.instagram.com/" target="_blank" style="display: inline-block; font-size: 1.2em; padding: 5px 10px; background-color: #000000; color: #ffffff; text-decoration: none; border-radius: 5px;">
                            <i class="bx bxl-instagram"></i>
                        </a>
                    </div>
                </div>

                <!-- Footer Section -->
                <div style="background-color: #000000; padding: 15px; text-align: center;">
                    <p style="color: #ffffff; margin: 0; font-size: .8em;">&copy; 2024 Devtegrate. All rights reserved.</p>
                </div>
            </div>
        </div>
    '''
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
                            "Email": recipient_email,
                            "Name": microsft_message_data['1. First and Last Name']
                        }
                    ],
                    "Subject": subject,
                    "HTMLPart": message,
                    "CustomID": "AppGettingStartedTest"
                }
            ]
        }

        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print("Confirmation email sent successfully.")
        else:
            print(f"Failed to send confirmation email: {result.status_code} - {result.text}")
    except Exception as e:
        print(f"Error sending confirmation email: {e}")

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
