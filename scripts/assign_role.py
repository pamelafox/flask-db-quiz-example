import logging
import os

import psycopg2
from azure.identity import DefaultAzureCredential

logger = logging.getLogger("scripts")


def assign_role_for_webapp(postgres_host, postgres_username, app_identity_name):
    if not postgres_host.endswith(".database.azure.com"):
        logger.info("This script is intended to be used with Azure Database for PostgreSQL.")
        logger.info("Please set the environment variable DBHOST to the Azure Database for PostgreSQL server hostname.")
        return

    logger.info("Authenticating to Azure Database for PostgreSQL using Azure Identity...")
    azure_credential = DefaultAzureCredential()
    token = azure_credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
    conn = psycopg2.connect(
        database="postgres",  # You must connect to postgres database when assigning roles
        user=postgres_username,
        password=token.token,
        host=postgres_host,
        sslmode="require",
    )

    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"select * from pgaadauth_list_principals(false) WHERE rolname = '{app_identity_name}'")

    # count number of rows in cur
    if len(cur.fetchall()) == 1:
        logger.info(f"Found an existing PostgreSQL role for identity {app_identity_name}")
    else:
        logger.info(f"Creating a PostgreSQL role for identity {app_identity_name}")
        cur.execute(f"SELECT * FROM pgaadauth_create_principal('{app_identity_name}', false, false)")
    logger.info(f"Granting permissions to {app_identity_name}")
    cur.execute(f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{app_identity_name}"')
    cur.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f'GRANT SELECT, UPDATE, INSERT, DELETE ON TABLES TO "{app_identity_name}"'
    )
    cur.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.INFO)

    POSTGRES_HOST = os.getenv("POSTGRES_DOMAIN_NAME")
    POSTGRES_USERNAME = os.getenv("POSTGRES_ADMIN_USERNAME")
    APP_IDENTITY_NAME = os.getenv("WEB_APP_NAME")
    if not POSTGRES_HOST or not POSTGRES_USERNAME or not APP_IDENTITY_NAME:
        logger.error(
            "Can't find POSTGRES_DOMAIN_NAME, POSTGRES_ADMIN_USERNAME, and WEB_APP_NAME environment variables. "
            "Make sure you run azd up first."
        )
    else:
        assign_role_for_webapp(POSTGRES_HOST, POSTGRES_USERNAME, APP_IDENTITY_NAME)
