import mailtrap as mt


class EmailClient:
    def __init__(self, token, receiver, sender, subject, html_body):
        self.client = mt.MailtrapClient(token=token)
        self.receiver = receiver
        self.sender = sender
        self.subject = subject
        self.html_body = html_body

    def send(self):
        mail = mt.Mail(
            sender=mt.Address(email=self.sender, name="SCANPAY"),
            to=[mt.Address(email=self.receiver)],
            subject=self.subject,
            html=self.html_body,
        )

        try:
            self.client.send(mail)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
