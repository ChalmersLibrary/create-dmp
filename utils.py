from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = os.getenv("SMTP_PORT")
smtp_user = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMPT_PASSWORD")
email_sender = os.getenv("EMAIL_SENDER")    

def test_smtp_connection():
    try:
        with smtplib.SMTP(smtp_server, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            print(f"SMTP server connected successfully.")
            return True
    except Exception as e:
        print(f"Failed to connect to SMTP server: {e}")
        return False

def load_template(mail_template_path):
    with open(mail_template_path, 'r', encoding='utf-8') as f:
        return f.read()

def send_html_email(recipient, recipent_name, subject, template_path, projectid, dmptitle, dmpurl, crisurl):
    html_template = load_template(template_path)
    html_content = html_template.format(recipent_name=recipent_name, projectid=projectid, dmptitle=dmptitle, dmpurl=dmpurl, crisurl=crisurl)
    msg = MIMEMultipart('alternative')
    msg['From'] = email_sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(email_sender, recipient, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
    
def pdb_stop_session(session_token):
    pdbstop_payload = {
        "function": "session_stop",
        "params": [],
        "session": session_token
    }
    pdb_url=os.getenv("PDB_API_URL")
    pdb_headers = {
    "Content-Type": "application/json"
    }
    pdbstop_response = requests.post(pdb_url, headers=pdb_headers, data=json.dumps(pdbstop_payload))
    if pdbstop_response.status_code == 200:
        try:
            pdbstop_result = pdbstop_response.json()
            print("PDB session terminated successfully")
        except ValueError:
            print(pdbstop_response.text)
            exit()
    else:
        print(f"PDB session terminate request failed with status code {pdbstop_response.status_code}")
        exit()

