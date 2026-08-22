import os
import smtplib

from email.message import EmailMessage


def send_password_reset_otp(
    recipient,
    otp
):

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(
        os.getenv("SMTP_PORT", "587")
    )
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM")

    message = EmailMessage()

    message["Subject"] = "Your Zoothy password reset code"
    message["From"] = sender
    message["To"] = recipient

    message.set_content(
        f"""
Your Zoothy password reset code is:

{otp}

This code expires in 10 minutes.

If you did not request a password reset, you can safely ignore this email.

Zoothy
"""
    )

    with smtplib.SMTP(
        smtp_host,
        smtp_port
    ) as smtp:

        smtp.starttls()

        smtp.login(
            smtp_username,
            smtp_password
        )

        smtp.send_message(message)