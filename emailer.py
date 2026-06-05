import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config


def send_email(html):
    msg = MIMEMultipart()
    msg["Subject"] = "Actuarial Intelligence Digest"
    msg["From"] = config.GMAIL_USER
    msg["To"] = config.TO_EMAIL

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(config.GMAIL_USER, config.GMAIL_PASS)
        s.sendmail(config.GMAIL_USER, config.TO_EMAIL, msg.as_string())
