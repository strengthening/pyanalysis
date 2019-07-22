import smtplib

from email.mime.multipart import MIMEMultipart
from email.header import Header


class Mail(object):
    def __init__(self, sender, password):
        # 初始化资源
        self._sender = sender
        self._message = MIMEMultipart('alternative')
        self._message["From"] = self._sender
        self._server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)
        self._server.ehlo()
        self._server.login(self._sender, password)

    def attach(self, att):
        self._message.attach(att)

    def send(self, title, receivers, copiers=None):
        self._message["Subject"] = Header(title, "utf-8")
        self._message["To"] = ",".join(receivers)
        if copiers:
            self._message["Cc"] = ",".join(copiers)
            self._server.sendmail(self._sender, receivers + copiers, self._message.as_string())
        else:
            self._server.sendmail(self._sender, receivers, self._message.as_string())
