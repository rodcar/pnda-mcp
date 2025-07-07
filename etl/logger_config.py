import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl/logs/etl.log'),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    return logging.getLogger(name)