import smtplib
from email.message import EmailMessage

from ..settings import settings


def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = settings.smtp_username
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(msg)


def get_email_body(row, raw_password):
    return f"""
            Poštovani/a {row["Ime"]},

            Vaš nalog za potrebe predmeta PIGKUT je aktiviran.

            Kredencijali za pristup platformi:
            Email: {row["Email"]}
            Lozinka: {raw_password}

            Prijavljivanje na platformu možete odraditi na sledećoj adresi: https://d2atyi04ej7qi4.cloudfront.net/login.

            Srećan rad!
            """
