import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import List


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.mail.ru")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USERNAME","kolm-danil@mail.ru")
        self.password = os.getenv("SMTP_PASSWORD","RTX1ZSLvgTs1wCigtzl3")

    async def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Error sending email: {e}")