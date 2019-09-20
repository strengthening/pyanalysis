import unittest

from pyanalysis.mail import Mail


class TestMail(unittest.TestCase):
    # def test_tls_mail(self):
    #     m = Mail("the email username", "the email password", mail_port=587, protocol="TLS")
    #     # html = """
    #     # <html>
    #     # <body>
    #     #     <h1>title</h1>
    #     # </body>
    #     # </html>
    #     # """
    #     # m.attach(HtmlContent(html))
    #     m.send("基金引流获客渠道周报", ["ducg@foxmail.com"])

    def test_ssl_mail(self):
        m = Mail("the email username", "the email password", mail_port=465, protocol="ssl")
        m.send("基金引流获客渠道周报", ["ducg@foxmail.com"])
