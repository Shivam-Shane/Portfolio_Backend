
import os
import logging
import logging_loki 
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger("PortfolioChatBotBackend")
logger.setLevel(logging.DEBUG)  

# Console handler (to log to console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter(
    '%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(console_format)

# Loki handler (For Remote logging to grafana loki logs)
LOKI_URL = os.getenv("LOKI_URL")
LOKI_USER = os.getenv("LOKI_USER")
LOKI_API_KEY = os.getenv("LOKI_API_KEY")  

loki_handler = logging_loki.LokiHandler(
    url=LOKI_URL,
    auth=(LOKI_USER, LOKI_API_KEY),
    version="1",
    tags={"application": "PortfolioChatBotBackend"},
)
loki_handler.setLevel(logging.INFO)


loki_format = logging.Formatter(
    '%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s'
)
loki_handler.setFormatter(loki_format)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(loki_handler)