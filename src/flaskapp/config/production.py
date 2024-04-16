import os

from azure.identity import DefaultAzureCredential

DEBUG = False

if "WEBSITE_HOSTNAME" in os.environ:
    ALLOWED_HOSTS = [os.environ["WEBSITE_HOSTNAME"]]
else:
    ALLOWED_HOSTS = []

dbuser = os.environ["DBUSER"]
azure_credential = DefaultAzureCredential()
dbpass = azure_credential.get_token("https://ossrdbms-aad.database.windows.net/.default").token
dbhost = os.environ["DBHOST"] + ".postgres.database.azure.com"
dbname = os.environ["DBNAME"]

DATABASE_URI = f"postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}"

# TODO: SSL not needed?
