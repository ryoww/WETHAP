import logging

logger = logging.getLogger("uvicorn.app")

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
