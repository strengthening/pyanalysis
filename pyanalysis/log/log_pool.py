

# logger pool
__loggerDict = {}


def add(logger):
    logger_name = logger.get_name()
    __loggerDict[logger_name] = logger


def get(logger_name):
    return __loggerDict[logger_name]