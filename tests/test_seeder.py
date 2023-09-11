from flaskapp import db as _db
from flaskapp.quizzes import Quiz


def test_seed_data(app):
    assert Quiz.seed_data_if_empty() is True
    assert Quiz.seed_data_if_empty() is False

    _db.session.delete(_db.session.execute(_db.select(Quiz)).scalar())
    _db.session.commit()


def test_seed_command(app, runner):
    result = runner.invoke(args="seed")
    assert "Quiz seeded!" in result.output
    result = runner.invoke(args="seed")
    assert "Already seeded!" in result.output
