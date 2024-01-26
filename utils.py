import logging
import os

datafolder = os.path.join(os.getenv("appdata"), "the_ark")
database_path = os.path.join(datafolder, "data")
messages_path = os.path.join(datafolder, "messages")

try:
    os.makedirs(datafolder, exist_ok=True)
except FileExistsError:
    pass

log_file = os.path.join(datafolder, "log.log")
logging.basicConfig(filename=log_file, filemode='a',
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    level=logging.INFO)
