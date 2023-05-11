import os

import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

from flaskapp import create_app
from flaskapp import db as _db


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    dbuser = os.environ["DBUSER"]
    dbpass = os.environ["DBPASS"]
    dbhost = os.environ["DBHOST"]
    TEST_DATABASE_URI = f"postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/postgres"
    config_override = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ.get("TEST_DATABASE_URI", TEST_DATABASE_URI),
    }
    _app = create_app(config_override)

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return _app


@pytest.fixture(scope="session")
def db(app, request):
    """Session-wide test database."""

    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    db.session = scoped_session(session_factory=sessionmaker(bind=connection))

    def teardown():
        transaction.rollback()
        connection.close()
        db.session.remove()

    request.addfinalizer(teardown)
    return db.session


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
