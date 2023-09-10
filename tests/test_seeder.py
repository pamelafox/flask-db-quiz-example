from flaskapp.quizzes import Question, Quiz, QuizScore


def test_seed_data(app):
    assert Quiz.seed_data_if_empty() is True
    assert Quiz.seed_data_if_empty() is False
    QuizScore.query.delete()
    Question.query.delete()
    Quiz.query.delete()


def test_seed_command(app, runner):
    result = runner.invoke(args="seed")
    assert "Quiz seeded!" in result.output
    result = runner.invoke(args="seed")
    assert "Already seeded!" in result.output
