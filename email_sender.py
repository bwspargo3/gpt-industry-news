import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(html_content):
    sender_email = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient_email = os.environ.get("RECIPIENT_EMAIL")

    msg = MIMEMultipart()
    msg['Subject'] = "Actuarial Intelligence Briefing"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("    Email sent successfully!")
    except Exception as e:
        print(f"    Failed to send email: {e}")
