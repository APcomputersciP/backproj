import threading
from flask import render_template, request, jsonify
from flask.cli import AppGroup
from __init__ import app, db
from api.covid import covid_api
from api.joke import joke_api
from api.user import user_api
from api.player import player_api
from model.users import initUsers
from model.players import initPlayers
from projects.projects import app_projects

# Initialize the SQLAlchemy object to work with the Flask app instance
db.init_app(app)

# Import necessary modules
from flask_cors import CORS

# Define the Quote model
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_text = db.Column(db.String(255), nullable=False)
    quote_author = db.Column(db.String(100), nullable=False)
    user_opinion = db.Column(db.Text, nullable=False)

# setup APIs
app.register_blueprint(joke_api)
app.register_blueprint(covid_api)
app.register_blueprint(user_api)
app.register_blueprint(player_api)
app.register_blueprint(app_projects)

# Apply CORS to your app
CORS(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/table/')
def table():
    return render_template("table.html")

# Manually handle CORS headers for the quote-repository route
@app.route('/quote-repository', methods=['GET', 'POST', 'OPTIONS'])
def quote_repository():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
    elif request.method == 'GET':
        # Handle GET request
        quotes = Quote.query.all()
        quotes_list = [{'quote_text': quote.quote_text, 'quote_author': quote.quote_author, 'user_opinion': quote.user_opinion} for quote in quotes]
        response = jsonify({'quotes': quotes_list})
    else:
        # Handle POST request
        data = request.get_json()
        new_quote = Quote(
            quote_text=data.get('quote'),
            quote_author=data.get('quote_author'),
            user_opinion=data.get('opinion')
        )
        db.session.add(new_quote)
        db.session.commit()
        response_data = {'message': 'Quote submitted successfully'}
        response = jsonify(response_data)

    # Allow requests from the specified origin
    response.headers['Access-Control-Allow-Origin'] = 'https://isabellehp.github.io'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return response

custom_cli = AppGroup('custom', help='Custom commands')

@custom_cli.command('generate_data')
def generate_data():
    initUsers()
    initPlayers()

app.cli.add_command(custom_cli)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True, host="0.0.0.0", port="8086")
