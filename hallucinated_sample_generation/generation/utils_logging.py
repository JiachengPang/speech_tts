import logging
import os
import sys
from datetime import datetime

def setup_logger(script_name: str, log_dir: str = 'logs') -> str:
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(log_dir, f"{script_name}_{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    class PrintRedirect:
        def write(self, message):
            if message.strip():
                logger.info(message.strip())
        def flush(self): pass

    sys.stdout = PrintRedirect()
    sys.stderr = PrintRedirect()

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    print(f"[LOGGING] Output is being saved to: {log_path}")
    return log_path
