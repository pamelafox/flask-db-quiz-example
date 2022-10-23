import os

from flask import Flask, request, jsonify, render_template
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

# Create database and tables
db.init_app(app)

class PlayerScore(db.Model):
    __tablename__ = 'player_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)

with app.app_context():
    db.create_all()

# Set up the routes
@app.route('/')
def app_index():
	return render_template('index.html')

@app.route('/score', methods=['POST'])
def app_add():
    score = PlayerScore(player=request.form['player'],
                        score=request.form.get('score'))
    db.session.add(score)
    db.session.commit()
    return 'ok'

@app.route('/scores', methods=['GET'])
def app_login():
    result = db.session.execute(db.select(PlayerScore).group_by(PlayerScore.player).order_by(PlayerScore.score.desc())).scalars()
    return jsonify([ {"player": r.player, "score": r.score} for r in result])

# Run the server
if __name__ == '__main__':
   app.run()