import email.message
import email, smtplib, ssl
from random import choices
from os import environ

sender = environ['EMAIL_USER']
password = environ['EMAIL_PASS']


# from email import encoders
# from email.mime.base import MIMEBase
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


def generateOTP():
    digits = "0123456789"
    return ''.join(choices(digits,k=4))


# receiver = 'rahul@vmmeducation.com'
def send_Mail(receiver):
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(sender, password)
            otp = generateOTP()
            body = "Your email is been registered to E-Shop. Use the following OTP to complete registration with us.\n" \
                   f"Your registration otp is: {otp}.\n\n" \
                   # "If it is not you who requested the registration then ignore this mail."
            subject = "Subject:Please Do Not share the OTP \n\n "
            msg = subject + body
            smtp.sendmail(sender, receiver, msg)
            print('Sent')

        return otp

    except smtplib.SMTPException:
        print("Not Sent")


def send_Receipt(receiver, body):
    try:
        sender = environ['EMAIL_USER']
        password = environ['EMAIL_PASS']

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            # with smtplib.SMTP('localhost',1025) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(sender, password)

            msg = email.message.Message()
            msg['Subject'] = 'Order Placed Successfully'

            msg['From'] = sender
            msg['To'] = receiver
            msg.add_header('Content-Type', 'text/html')
            msg.set_payload(body)
            smtp.sendmail(sender, receiver, msg.as_string())
            print('Sent')


    except smtplib.SMTPException:
        print("Not Sent")


# def checkthis():
#     receiver = 'rkb9874@gmail.com'
#     username = 'Rahul'
#     mobile = '6280995201'
#     print(mobile)
#     sender = 'tania.vmmteachers23@gmail.com'
#     password = 'Teachers@123'
#
#     smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
#     smtpserver.ehlo()
#     smtpserver.starttls()
#     smtpserver.login(sender, password)
#     body = f"""
#                 <html>
#                 <head>
#                 <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
#                 </head>
#                 <body>
#
#                 </table>
#             </body>
#                 """
#     msg = email.message.Message()
#     msg['Subject'] = 'Signup in Zomato'
#
#     msg['From'] = sender
#     msg['To'] = receiver
#     password = password
#     msg.add_header('Content-Type', 'text/html')
#     msg.set_payload(body)
#     smtpserver.sendmail(sender, receiver, msg.as_string())
#     print('Sent')
#     smtpserver.close()
#
#
# def mailwithAttachemnt(reciver, id, filelocation):
#     subject = "QR Code"
#     # body = "This is an email with attachment sent from Python"
#
#     body = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Title</title>
#     </head>
#     <body>
#         <p>dear member,<br>
#         your id number is {}. download this file</p>
#     </body>
#     </html>
#     """.format(id)
#
#     sender_email = "tania.vmmteachers23@gmail.com"
#     receiver_email = reciver
#     password = "Teachers@1234"
#
#     # Create a multipart message and set headers
#     message = MIMEMultipart()
#     message["From"] = sender_email
#     message["To"] = receiver_email
#     message["Subject"] = subject
#     message["Bcc"] = receiver_email  # Recommended for mass emails
#
#     # Add body to email
#     # message.attach(MIMEText(body, "plain"))
#     message.attach(MIMEText(body, "html"))
#
#     # filename = "../static/pdf/8SigneRichardson.pdf"  # In same directory as script
#     filename = filelocation  # In same directory as script
#
#     # Open PDF file in binary mode
#     with open(filename, "rb") as attachment:
#         # Add file as application/octet-stream
#         # Email client can usually download this automatically as attachment
#         part = MIMEBase("application", "octet-stream")
#         part.set_payload(attachment.read())
#
#     # Encode file in ASCII characters to send by email
#     encoders.encode_base64(part)
#
#     # Add header as key/value pair to attachment part
#     part.add_header(
#         "Content-Disposition",
#         f"attachment; filename= {filename}",
#     )
#
#     # Add attachment to message and convert message to string
#     message.attach(part)
#     text = message.as_string()
#
#     # Log in to server using secure context and send email
#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#         server.login(sender_email, password)
#         server.sendmail(sender_email, receiver_email, text)
#

if __name__ == '__main__':
    send_Mail('madhavchopra99@gmail.com')
