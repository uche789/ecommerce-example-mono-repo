import logging

def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log") # Log to file
        ]
    )
    return logging.getLogger('inventory.logger')