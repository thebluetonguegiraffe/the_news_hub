import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

# Gmail account credentials
load_dotenv()  # Load environment variables from .env file if needed

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_USER = "thebluetonguegiraffe@gmail.com"
GMAIL_APP_PASSWORD = os.getenv('GMAIL_PWD')

def send_email(to_email, subject, body, cc=None, bcc=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        if cc:
            msg["Cc"] = ", ".join(cc if isinstance(cc, list) else [cc])

        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)

        recipients = [to_email]
        if cc:
            recipients += cc if isinstance(cc, list) else [cc]
        if bcc:
            recipients += bcc if isinstance(bcc, list) else [bcc]

        # Send email
        server.sendmail(GMAIL_USER, recipients, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        raise

# Example usage
if __name__ == "__main__":
    send_email(
        to_email="thebluetonguegiraffe@gmail.com",
        subject="Test Email from Python",
        body="<h2>Hello!</h2><p>This is a test email sent using <b>Gmail SMTP</b>.</p>",
        # cc=["ccperson@example.com"],
        # bcc=["hidden@example.com"]
    )
