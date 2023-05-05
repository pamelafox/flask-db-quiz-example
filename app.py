import os

from flask import Flask, request, render_template
from flask_migrate import Migrate
from sqlalchemy import Column, String, Integer
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

class PlayerScore(db.Model):
    __tablename__ = 'player_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)

class Question(db.Model):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(255), nullable=False)
    answer = Column(String(255), nullable=False)
    choices = Column(String(255), nullable=False)
    quiz_id = Column(Integer, nullable=False)

# Set up the routes
@app.route('/')
def index():
    quizzes = db.select(Quiz).all()
    return render_template('index.html', quizzes=quizzes)

@app.route('/quiz/<quiz_id>')
def quiz(quiz_id):
    quiz = db.select(Quiz).where(Quiz.id == quiz_id).first()
    questions = db.select(Question).where(Question.quiz_id == quiz_id).all()
    return render_template('quiz.html', quiz=quiz, questions=questions)

@app.route('/quiz/<quiz_id>/scores', methods=['POST'])
def app_add():
    score = PlayerScore(player=request.form['player'],
                        score=request.form.get('score'))
    db.session.add(score)
    db.session.commit()
    return 'ok'

@app.route('/scores', methods=['GET'])
def app_login():
    result = db.session.execute(db.select(PlayerScore.player, db.func.max(PlayerScore.score).label('max_score')).group_by(PlayerScore.player).order_by('max_score')).all()
    return render_template('_scores.html', player_scores=result)

@app.route('/seed', methods=['GET'])
def seed():
    # if there are no quizzes, create a quiz and add questions
    if len(Quiz.query.all()) > 0:
        return 'ok'
    quiz = Quiz(title='Python Quiz!')
    db.session.add(quiz)
    db.session.commit()
    question = Question(question='Who invented Python?', answer='Guido van Rossum', choices='Guido van Rossum,Ada Lovelace,Rob Pike,Kathleen Booth', quiz_id=quiz.id)
    db.session.add(question)
    question = Question(question='What is the name of the Python package installer?', answer='pip', choices='pip,py,package,install', quiz_id=quiz.id)
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