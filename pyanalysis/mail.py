import ssl
import smtplib

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

__all__ = ["Mail", "HtmlContent", "ExcelAttach", "ImageAttach"]


# 图片附件，这里不是指镶嵌在html中的图片
class ImageAttach(MIMEImage):
    def __init__(self, filepath, filename):
        with open(filepath, "rb") as fp:
            super().__init__(fp.read(), _subtype="octet-stream")
            self.add_header("Content-Disposition", "attachment", filename=("gb2312", "", filename))


class ExcelAttach(MIMEApplication):
    def __init__(self, filepath, filename):
        with open(filepath, "rb") as fp:
            super().__init__(fp.read())
            self.add_header("Content-Disposition", "attachment", filename=("gb2312", "", filename))


# html正文
class HtmlContent(MIMEText):
    def __init__(self, content):
        super().__init__(content, "html", "utf-8")


class Mail(object):
    def __init__(self, username, password, mail_port=465, time_out=20.0, host="smtp.qq.com", protocol="SSL"):
        # 初始化资源
        self._username = username
        self._password = password
        self._mail_port = mail_port
        self._time_out = time_out
        self._protocol = protocol
        self._host = host
        self._secure = None
        self._attachments = []

    def _get_smtp_server(self):
        if self._protocol.upper() == "SSL":
            smtp = smtplib.SMTP_SSL(self._host, self._mail_port, timeout=self._time_out)
        elif self._protocol.upper() == "TLS":
            _DEFAULT_CIPHERS = (
                "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:"
                "DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:"
                "!eNULL:!MD5"
            )
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.set_ciphers(_DEFAULT_CIPHERS)
            context.set_default_verify_paths()
            context.verify_mode = ssl.CERT_REQUIRED
            self._secure = (None, None, context)
            smtp = smtplib.SMTP(self._host, self._mail_port, timeout=self._time_out)
        else:
            raise RuntimeError("Can not use the protocol {}. The protocol must in ssl or tls".format(self._protocol))

        if self._username:
            if self._secure is not None:
                smtp.ehlo()
                smtp.starttls(*self._secure)
                smtp.ehlo()
            smtp.login(self._username, self._password)
        return smtp

    def attach(self, context):
        self._attachments.append(context)

    def send(self, title, receivers, copiers=None):
        msg = MIMEMultipart('alternative')
        msg["From"] = self._username
        msg["To"] = ",".join(receivers)
        msg["Subject"] = title
        all_receiver = receivers
        if copiers:
            msg["Cc"] = ",".join(copiers)
            all_receiver += copiers
        for attach in self._attachments:
            msg.attach(attach)

        smtp = self._get_smtp_server()
        smtp.sendmail(self._username, all_receiver, msg.as_string())
        smtp.quit()
