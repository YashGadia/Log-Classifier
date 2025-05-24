import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_workflow_error_email_batch(df, recipient_email):
    if not EMAIL_USER or not EMAIL_PASSWORD:
        raise ValueError("Email credentials not set in .env file")

    subject = "⚠️ Workflow Error Logs Alert"
    body = "The following Workflow Error logs were detected:\n\n"

    for _, row in df.iterrows():
        body += f"- Source: {row['source']}\n  Message: {row['log_message']}\n\n"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)