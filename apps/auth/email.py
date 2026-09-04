import os
import smtplib

from email.message import EmailMessage


def send_otp(
    recipient,
    otp,
    purpose
):

    smtp_host = os.getenv("SMTP_HOST")

    smtp_port = int(
        os.getenv(
            "SMTP_PORT",
            "587"
        )
    )

    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM")

    if purpose == "registration":

        subject = "Verify your Zoothy account"

        content = f"""
Welcome to Zoothy.

Your email verification code is:

{otp}

This code expires in 10 minutes.

If you did not create a Zoothy account, you can safely ignore this email.

Zoothy
"""

    elif purpose == "password_reset":

        subject = "Your Zoothy password reset code"

        content = f"""
Your Zoothy password reset code is:

{otp}

This code expires in 10 minutes.

If you did not request a password reset, you can safely ignore this email.

Zoothy
"""

    else:

        raise ValueError(
            "Invalid OTP purpose."
        )

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient

    message.set_content(
        content
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

        smtp.send_message(
            message
        )


def send_password_reset_otp(
    recipient,
    otp
):

    send_otp(
        recipient,
        otp,
        "password_reset"
    )