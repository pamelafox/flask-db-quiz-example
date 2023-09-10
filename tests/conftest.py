import os

import pytest

from flaskapp import create_app
from flaskapp import db as _db
from flaskapp.quizzes import Question, Quiz, QuizScore


@pytest.fixture(scope="session")
def app():
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

    with _app.app_context():
        engines = _db.engines
        _db.create_all()

    engine_cleanup = []
    for key, engine in engines.items():
        connection = engine.connect()
        transaction = connection.begin()
        engines[key] = connection
        engine_cleanup.append((key, engine, connection, transaction))

    yield _app

    with _app.app_context():
        _db.session.query(QuizScore).delete()
        _db.session.query(Question).delete()
        _db.session.query(Quiz).delete()

    for key, engine, connection, transaction in engine_cleanup:
        transaction.rollback()
        connection.close()
        engines[key] = engine


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def fake_quiz(app):
    Quiz.seed_data_if_empty()

    yield _db.session.query(Quiz).first()

    _db.session.query(Question).delete()
    _db.session.query(QuizScore).delete()
    _db.session.query(Quiz).delete()
