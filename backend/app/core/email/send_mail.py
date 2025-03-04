import smtplib
from email.mime.text import MIMEText

import emailgen

from app.core.logging.logger import logger
from app.settings import settings
from app.users.schema import User

# For most simple use cases, this should be all you need to define.
generator = emailgen.Generator(
    product={
        "name": f"The {settings.PORTAL_NAME} Team",
        "link": settings.HOST,
        "logo": f"{settings.HOST.strip('/')}/favicon.svg",
        "copyright": f"Copyright &copy;, {settings.CORPORATION}. All rights reserved.",
        "trouble": "If you're having trouble viewing this"
        "email in your email, view it <a href=",  # ">here</a>."
    }
)


def send_mail(recipients: list[User], action: emailgen.Table, url: str, subject: str):
    for recipient in recipients:
        try:
            email = emailgen.Email(f"{recipient.first_name}")
            email.greeting = "Hi"
            email.add_intro(
                "You have a pending request in the <b>Data Product Portal</b>. "
                "Please review it at your earliest convenience."
            )
            email.add_table(action)
            email.add_action(
                "Click below to take action:",
                emailgen.Button("Go to Portal", url, color=settings.EMAIL_BUTTON_COLOR),
            )
            email.add_outros(
                "If you have questions or need assistance, "
                "feel free to reach out — we're here to help!"
            )
            email.add_outros("Made with ❤️ by Dataminded.")

            html_output = generator.html(email)

            msg = MIMEText(html_output, _subtype="html")
            msg["Subject"] = subject
            msg["From"] = settings.FROM_MAIL_ADDRESS
            msg["To"] = recipient.email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if not settings.SMTP_NO_LOGIN and settings.SMTP_HOST != "localhost":
                    server.starttls()
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(
                    settings.FROM_MAIL_ADDRESS, recipient.email, msg.as_string()
                )
                server.quit()
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
