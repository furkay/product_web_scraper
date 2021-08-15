import os
from dotenv import load_dotenv

load_dotenv()

data_hostname = os.getenv('DATA_HOSTNAME')
data_username = os.getenv('DATA_USERNAME')
data_pass = os.getenv('DATA_PASSWORD')
data_db_name = os.getenv('DATA_DATABASE')
