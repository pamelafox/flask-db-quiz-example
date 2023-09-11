from typing import List

from flask import Blueprint, render_template, request
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db

bp = Blueprint("quizzes", __name__)


class QuizScore(db.Model):
    __tablename__ = "quiz_scores"
    id: Mapped[int] = mapped_column(db.Integer, init=False, primary_key=True, autoincrement=True)
    player: Mapped[str] = mapped_column(db.String(255), nullable=False)
    score: Mapped[int] = mapped_column(db.Integer, nullable=False)
    # 1 to 1 relationship between QuizScore and Quiz
    quiz_id: Mapped[int] = mapped_column(db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    quiz: Mapped["Quiz"] = relationship(init=False, back_populates="scores")


class Quiz(db.Model):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(db.Integer, init=False, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    scores: Mapped[List[QuizScore]] = relationship(
        "QuizScore",
        back_populates="quiz",
        default_factory=list,
        cascade="all, delete",
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="quiz",
        default_factory=list,
        cascade="all, delete",
    )

    @staticmethod
    def questions_for_quiz(quiz_id) -> List["Question"]:
        return db.session.execute(db.select(Question).where(Question.quiz_id == quiz_id)).scalars().all()

    @staticmethod
    def seed_data_if_empty():
        if len(db.session.execute(db.select(Question)).scalars().all()) > 0:
            return False
        # if there are no quizzes, create a quiz and add questions
        quiz: Quiz = Quiz(title="Python Quiz")
        db.session.add(quiz)
        db.session.commit()
        questions = [
            Question(
                question="Who invented Python?",
                answer="Guido van Rossum",
                choices=["Guido van Rossum", "Ada Lovelace", "Rob Pike", "Kathleen Booth"],
                quiz_id=quiz.id,
            ),
            Question(
                question="What is the name of the Python package installer?",
                answer="pip",
                choices=["pip", "py", "package", "install"],
                quiz_id=quiz.id,
            ),
            Question(
                question="What was Python named after?",
                answer="Monty Python, the comedy group",
                choices=[
                    "Python, the type of snake",
                    "Monty Python, the comedy group",
                    "Python of Aenus, the philosopher",
                    "Ford Python, a race car",
                ],
                quiz_id=quiz.id,
            ),
            Question(
                question="When was the first version of Python released?",
                answer="1991",
                choices=["1971", "1981", "1991", "2001", "2011"],
                quiz_id=quiz.id,
            ),
        ]
        db.session.add_all(questions)
        db.session.commit()
        return True


class Question(db.Model):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(db.Integer, init=False, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(db.String(255), nullable=False)
    answer: Mapped[str] = mapped_column(db.String(255), nullable=False)
    choices: Mapped[List[str]] = mapped_column("data", db.ARRAY(db.String))
    quiz_id: Mapped[int] = mapped_column(db.ForeignKey("quizzes.id"), nullable=False)
    quiz: Mapped[Quiz] = relationship(init=False, back_populates="questions")

    @property
    def form_name(self):
        return f"question{self.id}"


# Set up the routes
@bp.route("/")
def index():
    quizzes = db.session.execute(db.select(Quiz)).scalars().all()
    return render_template("index.html", quizzes=quizzes)


@bp.route("/quizzes/<quiz_id>")
def quiz(quiz_id):
    quiz = db.get_or_404(Quiz, quiz_id)
    questions = Quiz.questions_for_quiz(quiz_id)
    return render_template("quiz.html", quiz=quiz, questions=questions)


@bp.route("/quizzes/<quiz_id>/scores", methods=["GET", "POST"])
def app_add(quiz_id):
    if request.method == "POST":
        questions = Quiz.questions_for_quiz(quiz_id)
        # iterate over questions and check answers
        num_correct = 0
        for question in questions:
            if request.form.get(question.form_name) == question.answer:
                num_correct += 1
        percent_correct = (num_correct / len(questions)) * 100
        quiz_score = QuizScore(player=request.form["player"] or "Anonymous", score=percent_correct, quiz_id=quiz_id)
        db.session.add(quiz_score)
        db.session.commit()
        return (
            render_template("_score.html", quiz_score=quiz_score),
            200,
            {"HX-Trigger": "updateScores"},
        )
    else:
        # Always fetch scores and display them
        result = db.session.execute(
            db.select(QuizScore.player, QuizScore.score, db.func.max(QuizScore.score).label("max_score"))
            .where(QuizScore.quiz_id == quiz_id)
            .group_by(QuizScore.player, QuizScore.score)
            .order_by(db.desc("max_score"))
        ).all()
        return render_template("_scores.html", player_scores=result)
