import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)


logger = logging.getLogger('PhysicsLearningPlatform')

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def log_debug(message):
    logger.debug(message)