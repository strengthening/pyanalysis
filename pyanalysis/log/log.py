import logging

FATAL = logging.FATAL
ERROR = logging.ERROR
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG


class ILog(object):
    def __init__(self):
        self._logger = logging.getLogger()
        self._name = None

    def get_name(self):
        return self._name

    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        self._logger.info(msg)

    def warn(self, msg):
        # 当msg为错误类型时，打印traceback
        self._logger.warning(msg, exc_info=issubclass(type(msg), BaseException) or isinstance(msg, BaseException))

    def error(self, msg):
        # 当msg为错误类型时，打印traceback
        self._logger.error(msg, exc_info=issubclass(type(msg), BaseException) or isinstance(msg, BaseException))


class ConsoleLog(ILog):
    def __init__(self, name, level):
        super().__init__()
        formatter = logging.Formatter("%(asctime)-15s [%(levelname)s] %(message)s", "%Y/%m/%d %H:%M:%S")
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(console)
        self._logger = logger
        self._name = name
        self._level = level


class FileLog(ILog):
    def __init__(self, name, level, file_path):
        super().__init__()
        formatter = logging.Formatter("%(asctime)-15s [%(levelname)s] %(message)s", "%Y/%m/%d %H:%M:%S")
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(file_handler)
        self._logger = logger
        self._name = name
        self._level = level
