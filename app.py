import os

import click
from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static')

# Load configuration for prod vs. dev
is_prod_env = 'WEBSITE_HOSTNAME' in os.environ
if not is_prod_env:
    app.config.from_object('config.development')
else:
    app.config.from_object('config.production')

# Configure the database
app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ECHO=False
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

class QuizScore(db.Model):
    __tablename__ = 'quiz_scores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, nullable=False)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)

    @staticmethod
    def questions_for_quiz(quiz_id):
        return db.session.execute(db.select(Question).where(Question.quiz_id == quiz_id)).scalars().all()

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    choices = db.Column("data", db.ARRAY(db.String))
    quiz_id = db.Column(db.Integer, nullable=False)

    @property
    def form_name(self):
        return f'question{self.id}'


# Set up the routes
@app.route('/')
def index():
    quizzes = db.session.execute(db.select(Quiz)).scalars().all()
    return render_template('index.html', quizzes=quizzes)

@app.route('/quizzes/<quiz_id>')
def quiz(quiz_id):
    quiz = db.get_or_404(Quiz, quiz_id)
    questions = Quiz.questions_for_quiz(quiz_id)
    return render_template('quiz.html', quiz=quiz, questions=questions)

@app.route('/quizzes/<quiz_id>/scores', methods=['GET', 'POST'])
def app_add(quiz_id):
    if request.method == 'POST':
        questions = Quiz.questions_for_quiz(quiz_id)
        # iterate over questions and check answers
        num_correct = 0
        for question in questions:
            if request.form.get(question.form_name) == question.answer:
                num_correct += 1
        percent_correct = (num_correct / len(questions)) * 100
        quiz_score = QuizScore(player=request.form['player'] or 'Anonymous',
                          score=percent_correct,
                           quiz_id=quiz_id
                            )
        db.session.add(quiz_score)
        db.session.commit()
        return render_template('_score.html', quiz_score=quiz_score), 200, {'HX-Trigger': 'updateScores'}
    else:
        # Always fetch scores and display them
        result = db.session.execute(
            db.select(QuizScore.player, QuizScore.score, db.func.max(QuizScore.score).label('max_score'))
                .where(QuizScore.quiz_id == quiz_id)
                .group_by(QuizScore.player, QuizScore.score).order_by(db.desc('max_score'))).all()
        return render_template('_scores.html', player_scores=result)

@app.cli.command("seed")
def seed_data():
    if len(Quiz.query.all()) > 0:
        click.echo('Already seeded!')
        return
    # if there are no quizzes, create a quiz and add questions
    quiz = Quiz(title='Python Quiz')
    db.session.add(quiz)
    db.session.commit()
    questions = [
        Question(question='Who invented Python?', answer='Guido van Rossum',
                        choices=['Guido van Rossum' , 'Ada Lovelace', 'Rob Pike' , 'Kathleen Booth'], quiz_id=quiz.id),
        Question(question='What is the name of the Python package installer?', answer='pip',
                        choices=['pip', 'py', 'package', 'install'], quiz_id=quiz.id),
        Question(question='What was Python named after?', answer='Monty Python, the comedy group',
                        choices=['Python, the type of snake', 'Monty Python, the comedy group',
                                'Python of Aenus, the philosopher', 'Ford Python, a race car'], quiz_id=quiz.id),
        Question(question='When was the first version of Python released?', answer='1991',
                        choices=['1971', '1981', '1991', '2001', '2011'], quiz_id=quiz.id)
    ]
    db.session.add_all(questions)
    db.session.commit()
    click.echo('Quiz seeded!')