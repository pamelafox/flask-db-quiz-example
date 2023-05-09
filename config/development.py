import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

dbuser = os.environ["DBUSER"]
dbpass = os.environ["DBPASS"]
dbhost = os.environ["DBHOST"]
dbname = os.environ["DBNAME"]
DATABASE_URI = f"postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}"

TIME_ZONE = "UTC"
