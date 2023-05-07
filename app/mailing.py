# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail,From
import os


def send_mail(sender_name,recipient_email,subject,template):
    print('Mailing target reached')
    mail=From(name=sender_name,email=os.getenv('sendgrid_sender_email'))
    message = Mail(
    from_email=mail,
    to_emails=recipient_email,
    subject=subject,
    html_content=template
    )
    print(message)
    try:
        sg = SendGridAPIClient(os.getenv('sendgrid_api_key'))
        response=sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

