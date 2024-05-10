import logging

logger = logging.getLogger()

formatter = logging.Formatter("%(levelname)s;\t%(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger.setLevel(logging.INFO)
logger.addHandler(handler)


logger.info("create logger")
