def mail_otp(user, otp):
    subject = f"Greetings {user} !!!"
    template = f'''<!DOCTYPE html> 
<html>
  <head>
    <meta charset="UTF-8">
    <title>Your OTP</title>
  </head>
  <body>
    <p>Hello,</p>
    <p>Your OTP is: <strong>{otp}</strong></p>
    <p>This OTP is valid for 10 minutes. Please do not share this OTP with anyone.</p>
    <p>Thanks,<br>The Bankare Team</p>
  </body>
</html>'''
    return {'subject': subject, 'html_content': template}


def mail_agent_assigned(user, agent):
    subject = f"Greetings {user} !"
    template = f'''<html>
  <body>
    <p>Hello there!</p>
    <p>Thank you for contacting us. </p>
    <p>I appreciate you taking the time to reach out. </p>
    <strong>Agent named {agent} alloted to your query.{agent} will be responding you soon within 24 hrs.</strong>
    <p>Looking forward to your response.</p>
    <p>Best regards,</p>
    <p>The Bankare Team</p>
  </body>
</html>'''
    return {'subject': subject, 'html_content': template}


def mail_agent_reply(user):
    subject = f"Greetings {user} !"
    template = f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Customer Support - Response Received</title>
  </head>
  <body>
    <h1>Dear { user },</h1>
    <p>We are writing to let you know that one of our support agents has responded to your query.</p>
    
    <p>If you have any further questions or concerns, please don't hesitate to contact us again.</p>
    <p>Thank you for choosing Bankare.</p>
  </body>
</html>
'''
    return {'subject': subject, 'html_content': template}


def mail_complaint(user, bank_name):
    subject = f"Greetings {user}!"
    template = f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Apology to Customer</title>
  </head>
  <body>
    <h1>Apology to Customer</h1>
    <p>Dear {user},</p>
    <p>We apologize for any inconvenience caused by the issue you experienced. We take customer complaints very seriously and would like to express our sincerest apologies for falling short of your expectations.</p>
    <p>Your Banking provider is actively working on resolving the issue. In the meantime, please do not hesitate to contact us with any further questions or concerns.</p>
    <p>Thank you for bringing this to our attention and giving us the opportunity to make things right. We value your business and hope to regain your trust and confidence.</p>
    <p>Sincerely,</p>
    <p>{bank_name}@Bankare<br>
    Regards,<br>
    The Bankare Team</p>
  </body>
</html>
'''
    return {'subject': subject, 'html_content': template}
