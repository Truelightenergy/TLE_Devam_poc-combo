import smtplib
from email.mime.text import MIMEText

class Email:
    """
    class to send email to the users
    """

    def __init__(self):
        
        self.sender_email = "notifications@truelightenergy.com" 
        self.app_password = "Boston4000harbor"

    def send_email(self, subject, body, receiver_email = "alliranjha807@gmail.com"):
        """
        sends the email to the user
        """

        msg = MIMEText(body, 'html')
        msg['Subject'] = subject


        # Connect to Gmail's SMTP server using SSL
        smtp_server = 'smtp.gmail.com'
        port = 465  # SSL port for Gmail

        try:
            with smtplib.SMTP_SSL(smtp_server, port) as server:
                server.login(self.sender_email, self.app_password)  
                server.sendmail(self.sender_email, receiver_email, msg.as_string())
                print(f"Email sent successfully to {receiver_email}")
        except Exception as e:
            print(f"Error: {e}")