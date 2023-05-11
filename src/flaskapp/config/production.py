import os

DEBUG = False

if "WEBSITE_HOSTNAME" in os.environ:
    ALLOWED_HOSTS = [os.environ["WEBSITE_HOSTNAME"]]
else:
    ALLOWED_HOSTS = []

# Configure Postgres database; the full username for PostgreSQL flexible server is
# username (not @sever-name).
dbuser = os.environ["DBUSER"]
dbpass = os.environ["DBPASS"]
dbhost = os.environ["DBHOST"] + ".postgres.database.azure.com"
dbname = os.environ["DBNAME"]
DATABASE_URI = f"postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}"
