import smtplib
from email.mime.text import MIMEText

from app.core.logging.logger import logger
from app.settings import settings


def send_mail(from_mail: str, to_mail: list[str], message: str, subject: str):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = from_mail
    msg["To"] = ", ".join(to_mail)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_HOST != "localhost":
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(from_mail, to_mail, msg.as_string())
            server.quit()
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
