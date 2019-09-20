import ssl

from logging import StreamHandler, Formatter, DEBUG, WARNING, CRITICAL
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, SMTPHandler

__all__ = [
    "DebugHandler",
    "ReleaseRotatingFileHandler",
    "ReleaseTimedRotatingFileHandler",
    "AlarmSMTPHandler",
]

DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S%z"


# use it when you dev or debug your program.
class DebugHandler(StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)
        formatter = Formatter(
            DEFAULT_LOG_FORMAT,
            DEFAULT_DATE_FORMAT,
        )
        self.setFormatter(formatter)
        self.setLevel(DEBUG)


# choose it on your release environment
class ReleaseRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename):
        super().__init__(
            filename,
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding="UTF-8",
        )
        formatter = Formatter(
            DEFAULT_LOG_FORMAT,
            DEFAULT_DATE_FORMAT,
        )
        self.setFormatter(formatter)
        self.setLevel(WARNING)


# choose it on your release environment
class ReleaseTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename):
        super().__init__(
            filename,
            when="D",
            backupCount=10,
            encoding="UTF-8",
        )
        formatter = Formatter(
            DEFAULT_LOG_FORMAT,
            DEFAULT_DATE_FORMAT,
        )
        self.setFormatter(formatter)
        self.setLevel(WARNING)


class AlarmSMTPHandler(SMTPHandler):
    def __init__(
            self,
            host="",
            port=578,
            username="",
            password="",
            fromaddr="",
            toaddrs="",
            subject="pyanalysis notify"
    ):
        _DEFAULT_CIPHERS = (
            'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
            'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
            '!eNULL:!MD5')

        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3

        context.set_ciphers(_DEFAULT_CIPHERS)
        context.set_default_verify_paths()
        context.verify_mode = ssl.CERT_REQUIRED

        super().__init__(
            mailhost=(host, port),
            credentials=(username, password),
            secure=(None, None, context),
            subject=subject,
            fromaddr=fromaddr,
            toaddrs=toaddrs,
            timeout=20.0,
        )
        formatter = Formatter(
            DEFAULT_LOG_FORMAT,
            DEFAULT_DATE_FORMAT,
        )
        self.setFormatter(formatter)
        self.setLevel(CRITICAL)
