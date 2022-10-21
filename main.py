from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, select, Column, String, Integer
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define the database
engine = create_engine('sqlite:////tmp/data.db')
Base = declarative_base(engine)

class PlayerScore(Base):
    __tablename__ = 'player_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)

# Creates the initial tables
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
# Initialize app
app = Flask(__name__)

# Set up the routes
@app.route('/')
def app_index():
	return render_template('index.html')

@app.route('/score', methods=['POST'])
def app_add():
    session = Session()
    score = PlayerScore(player=request.form['player'],
                        score=request.form.get('score'))
    session.add(score)
    session.commit()
    session.close()
    return 'ok'

@app.route('/scores', methods=['GET'])
def app_login():
    session = Session()
    result = session.query(PlayerScore).group_by(PlayerScore.player).order_by(PlayerScore.score.desc()).all()
    session.close()
    return jsonify([ {"player": r.player, "score": r.score} for r in result])

# Run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)