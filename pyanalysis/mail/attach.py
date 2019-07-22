from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication


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
