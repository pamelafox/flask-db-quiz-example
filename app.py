import os

from flask import Flask, request, render_template
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
    SQLALCHEMY_ECHO=True
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
        score = QuizScore(player=request.form['player'] or 'Anonymous',
                          score=percent_correct,
                           quiz_id=quiz_id
                            )
        db.session.add(score)
        db.session.commit()
        return 'ok'
    else:
        result = db.session.execute(
            db.select(QuizScore.player, QuizScore.score, db.func.max(QuizScore.score).label('max_score'))
                .where(QuizScore.quiz_id == quiz_id)
                .group_by(QuizScore.player, QuizScore.score).order_by(db.desc('max_score'))).all()
        return render_template('_scores.html', player_scores=result)

@app.route('/seed', methods=['GET'])
def seed():
    # if there are no quizzes, create a quiz and add questions
    if len(Quiz.query.all()) > 0:
        return 'ok'
    quiz = Quiz(title='Python Quiz!')
    db.session.add(quiz)
    db.session.commit()
    question = Question(question='Who invented Python?', answer='Guido van Rossum',
                        choices=['Guido van Rossum' , 'Ada Lovelace', 'Rob Pike' , 'Kathleen Booth'], quiz_id=quiz.id)
    db.session.add(question)
    question = Question(question='What is the name of the Python package installer?', answer='pip',
                        choices=['pip', 'py', 'package', 'install'], quiz_id=quiz.id)
    db.session.add(question)
    """
          <fieldset>    
          <legend>What was Python named after?</legend>
          <label><input name="question2" value="snake" type="radio">Python, the type of snake</label><br>
          <label><input name="question2" value="monty" type="radio" data-yes>Monty Python, the comedy group</label><br>
          <label><input name="question2" value="person" type="radio">Python of Aenus, the philosopher</label><br>
          <label><input name="question2" value="car" type="radio">Ford Python, a race car</label><br>
      </fieldset>
    """
    db.session.commit()
    return 'Quiz seeded!'