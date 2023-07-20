import pytest

from flaskapp import db
from flaskapp.quizzes import Quiz, QuizScore


@pytest.fixture()
def client(app):
    return app.test_client()


def test_index(client, fake_quiz):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Python Quiz" in response.data


def test_quiz(client, fake_quiz):
    response = client.get(f"/quizzes/{fake_quiz.id}")
    assert response.status_code == 200
    assert b"Python Quiz" in response.data
    assert b"Who invented Python?" in response.data
    assert b"Guido van Rossum" in response.data
    assert b"Ada Lovelace" in response.data
    assert b"Rob Pike" in response.data
    assert b"Kathleen Booth" in response.data


def test_scores_100(client, fake_quiz):
    questions = Quiz.questions_for_quiz(fake_quiz.id)
    question_data = {question.form_name: question.answer for question in questions}
    question_data["player"] = "pamela"
    response = client.post(f"/quizzes/{fake_quiz.id}/scores", data=question_data)
    assert response.status_code == 200
    assert b"You got it all right!" in response.data
    quiz_score = db.session.execute(db.select(QuizScore).where(QuizScore.player == "pamela")).scalars().first()
    assert quiz_score.score == 100
    assert quiz_score.player == "pamela"
    # Now GET scores
    response = client.get(f"/quizzes/{fake_quiz.id}/scores")
    assert response.status_code == 200
    assert b"pamela: 100" in response.data


def test_scores_0(client, fake_quiz):
    questions = Quiz.questions_for_quiz(fake_quiz.id)
    question_data = {question.form_name: "wrong answer" for question in questions}
    question_data["player"] = "pammyla"
    response = client.post(f"/quizzes/{fake_quiz.id}/scores", data=question_data)
    assert response.status_code == 200
    assert b"You scored 0%" in response.data
    quiz_score = db.session.execute(db.select(QuizScore).where(QuizScore.player == "pammyla")).scalars().first()
    assert quiz_score.score == 0
    assert quiz_score.player == "pammyla"
    # Now GET scores
    response = client.get(f"/quizzes/{fake_quiz.id}/scores")
    assert response.status_code == 200
    assert b"pammyla: 0" in response.data


def test_scores_50(client, fake_quiz):
    questions = Quiz.questions_for_quiz(fake_quiz.id)
    question_data = {question.form_name: question.answer for question in questions}
    question_data[questions[0].form_name] = "wrong answer"
    question_data[questions[1].form_name] = "wrong answer"
    question_data["player"] = "susan"
    response = client.post(f"/quizzes/{fake_quiz.id}/scores", data=question_data)
    assert response.status_code == 200
    assert b"You scored 50%" in response.data
    quiz_score = db.session.execute(db.select(QuizScore).where(QuizScore.player == "susan")).scalars().first()
    assert quiz_score.score == 50
    assert quiz_score.player == "susan"
    # Now GET scores
    response = client.get(f"/quizzes/{fake_quiz.id}/scores")
    assert response.status_code == 200
    assert b"susan: 50" in response.data
